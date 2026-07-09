from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
import base64
import hashlib
import hmac

import httpx
from fastapi.testclient import TestClient
from sqlalchemy import select

from config.settings import Settings
from src.dashboard.app import app
from src.dashboard.models import EmailSubscription, NotificationDelivery, Signal, User
from src.dashboard.routes import api as api_routes
from src.dashboard.services.data_pipeline import _dispatch_signal_notifications
from src.notifier import notification_service as notification_module
from src.notifier.email_sender import EmailProviderError, EmailSender, EmailSendResult
from src.notifier.notification_service import NotificationService, verify_resend_webhook


class FakeEmailSender:
    def __init__(self):
        self.messages: list[dict[str, str]] = []

    def send(self, **message):
        self.messages.append(message)
        return EmailSendResult(provider="resend", message_id=f"msg-{len(self.messages)}")


def _settings() -> Settings:
    return Settings(
        app_env="test",
        smtp_from="FinLightAI <alerts@example.com>",
        email_provider="resend",
        resend_api_key="test-key",
        notification_token_secret="test-token-secret",
        backend_url="https://api.example.com",
    )


def _api_settings() -> Settings:
    return Settings(
        app_env="test",
        smtp_from="FinLightAI <alerts@example.com>",
        notification_secret="dispatch-secret",
        notification_token_secret="test-token-secret",
        backend_url="https://api.example.com",
    )


def _user(user_id: str = "notification-user") -> User:
    return User(id=user_id, username="Notification User", email="user@example.com")


def _signal(
    *,
    event_key: str,
    ticker: str,
    signal: str,
    event_score: float = 0.8,
) -> Signal:
    return Signal(
        event_key=event_key,
        ticker=ticker,
        trade_date=date(2026, 7, 9),
        event_score=event_score,
        market_reaction_score=0.4,
        signal=signal,
        evidence={"headline": f"{ticker} {signal} signal"},
        data_source="real",
    )


def test_email_subscription_api_get_put_validation_consent_and_user_isolation(
    monkeypatch,
    isolated_dashboard_database,
):
    settings = _api_settings()
    monkeypatch.setattr(api_routes, "get_settings", lambda: settings)
    monkeypatch.setattr(notification_module, "get_settings", lambda: settings)
    confirmation_messages: list[tuple[str, str]] = []

    def fake_confirmation(self, subscription, token):
        confirmation_messages.append((subscription.user_id, subscription.email))

    monkeypatch.setattr(
        notification_module.NotificationService,
        "_send_confirmation",
        fake_confirmation,
    )
    client = TestClient(app)

    initial = client.get("/api/email-subscription", headers={"X-User-ID": "email-user-a"})
    assert initial.status_code == 200
    assert initial.json() == {
        "email": "email-user-a@local.finlight",
        "status": "none",
        "dailySummary": True,
        "immediateRed": True,
        "immediateYellow": True,
        "consentedAt": None,
    }

    invalid = client.put(
        "/api/email-subscription",
        json={"email": "bad@", "dailySummary": True, "immediateRed": True, "immediateYellow": True},
        headers={"X-User-ID": "email-user-a"},
    )
    assert invalid.status_code == 422
    assert confirmation_messages == []

    updated = client.put(
        "/api/email-subscription",
        json={
            "email": "USER-A@Example.COM ",
            "dailySummary": False,
            "immediateRed": True,
            "immediateYellow": False,
        },
        headers={"X-User-ID": "email-user-a"},
    )
    assert updated.status_code == 200
    assert updated.json() == {
        "email": "user-a@example.com",
        "status": "pending",
        "dailySummary": False,
        "immediateRed": True,
        "immediateYellow": False,
        "consentedAt": None,
    }
    assert confirmation_messages == [("email-user-a", "user-a@example.com")]

    pending_dispatch = client.post(
        "/api/notifications/dispatch",
        json={
            "type": "signal",
            "subject": "RED signal",
            "body": "Immediate market-state alert",
            "dedupeKey": "signal:pending-user",
            "signal": "RED",
            "channels": ["email"],
        },
        headers={"X-Notification-Secret": "dispatch-secret"},
    )
    assert pending_dispatch.status_code == 200
    assert pending_dispatch.json() == {"sent": 0, "failed": 0, "duplicate": 0, "skipped": 0}

    second_user = client.put(
        "/api/email-subscription",
        json={
            "email": "user-b@example.com",
            "dailySummary": True,
            "immediateRed": False,
            "immediateYellow": True,
        },
        headers={"X-User-ID": "email-user-b"},
    )
    assert second_user.status_code == 200
    assert second_user.json()["email"] == "user-b@example.com"

    first_user_after_second_update = client.get(
        "/api/email-subscription",
        headers={"X-User-ID": "email-user-a"},
    )
    assert first_user_after_second_update.status_code == 200
    assert first_user_after_second_update.json()["email"] == "user-a@example.com"
    assert first_user_after_second_update.json()["dailySummary"] is False

    with isolated_dashboard_database() as db:
        first_subscription = db.get(EmailSubscription, "email-user-a")
        second_subscription = db.get(EmailSubscription, "email-user-b")
        assert first_subscription is not None
        assert second_subscription is not None
        assert first_subscription.email == "user-a@example.com"
        assert second_subscription.email == "user-b@example.com"


def test_double_opt_in_api_confirm_token_expiration_and_errors(
    monkeypatch,
    isolated_dashboard_database,
):
    settings = _api_settings()
    monkeypatch.setattr(api_routes, "get_settings", lambda: settings)
    monkeypatch.setattr(notification_module, "get_settings", lambda: settings)
    sent_messages: list[dict[str, str]] = []

    def fake_send(self, **message):
        sent_messages.append(message)
        return EmailSendResult(provider="smtp", message_id=f"confirm-{len(sent_messages)}")

    monkeypatch.setattr(notification_module.EmailSender, "send", fake_send)
    client = TestClient(app)

    subscribe = client.put(
        "/api/email-subscription",
        json={
            "email": "confirm-user@example.com",
            "dailySummary": True,
            "immediateRed": True,
            "immediateYellow": True,
        },
        headers={"X-User-ID": "confirm-user"},
    )

    assert subscribe.status_code == 200
    assert subscribe.json()["status"] == "pending"
    assert len(sent_messages) == 1
    assert sent_messages[0]["to"] == "confirm-user@example.com"
    assert "/api/email-subscription/confirm?token=" in sent_messages[0]["body"]
    token = sent_messages[0]["body"].split("token=", 1)[1].splitlines()[0]

    with isolated_dashboard_database() as db:
        subscription = db.get(EmailSubscription, "confirm-user")
        delivery = db.scalar(
            select(NotificationDelivery).where(
                NotificationDelivery.user_id == "confirm-user",
                NotificationDelivery.notification_type == "double_opt_in",
            )
        )
        assert subscription is not None
        assert subscription.status == "pending"
        assert subscription.token_expires_at is not None
        expires_at = subscription.token_expires_at.replace(tzinfo=timezone.utc)
        assert timedelta(hours=23, minutes=55) <= expires_at - datetime.now(timezone.utc) <= timedelta(hours=24)
        assert delivery is not None
        assert delivery.status == "sent"
        assert delivery.recipient == "confirm-user@example.com"

    invalid = client.get("/api/email-subscription/confirm?token=not-a-real-token")
    assert invalid.status_code == 400
    assert invalid.json()["detail"] == "Confirmation token is invalid or expired"

    confirmed = client.get(f"/api/email-subscription/confirm?token={token}")
    assert confirmed.status_code == 200
    assert confirmed.json()["status"] == "active"
    assert confirmed.json()["email"] == "confirm-user@example.com"
    assert confirmed.json()["consentedAt"] is not None

    with isolated_dashboard_database() as db:
        subscription = db.get(EmailSubscription, "confirm-user")
        assert subscription is not None
        assert subscription.status == "active"
        assert subscription.consented_at is not None
        assert subscription.confirm_token_hash is None
        assert subscription.token_expires_at is None

    expired_subscribe = client.put(
        "/api/email-subscription",
        json={
            "email": "expired-user@example.com",
            "dailySummary": True,
            "immediateRed": True,
            "immediateYellow": True,
        },
        headers={"X-User-ID": "expired-user"},
    )
    assert expired_subscribe.status_code == 200
    expired_token = sent_messages[-1]["body"].split("token=", 1)[1].splitlines()[0]

    with isolated_dashboard_database() as db:
        subscription = db.get(EmailSubscription, "expired-user")
        assert subscription is not None
        subscription.token_expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
        db.commit()

    expired = client.get(f"/api/email-subscription/confirm?token={expired_token}")
    assert expired.status_code == 400
    assert expired.json()["detail"] == "Confirmation token is invalid or expired"

    with isolated_dashboard_database() as db:
        subscription = db.get(EmailSubscription, "expired-user")
        assert subscription is not None
        assert subscription.status == "pending"
        assert subscription.consented_at is None


def test_unsubscribe_link_api_and_future_dispatch_exclusion(
    monkeypatch,
    isolated_dashboard_database,
):
    settings = _api_settings()
    monkeypatch.setattr(api_routes, "get_settings", lambda: settings)
    monkeypatch.setattr(notification_module, "get_settings", lambda: settings)
    sent_messages: list[dict[str, str]] = []

    def fake_send(self, **message):
        sent_messages.append(message)
        return EmailSendResult(provider="smtp", message_id=f"delivery-{len(sent_messages)}")

    monkeypatch.setattr(notification_module.EmailSender, "send", fake_send)

    with isolated_dashboard_database() as db:
        service = NotificationService(db, settings)
        unsubscribe_token = service._unsubscribe_token("unsubscribe-user", "unsubscribe@example.com")
        db.add(_user("unsubscribe-user"))
        db.add(
            EmailSubscription(
                user_id="unsubscribe-user",
                email="unsubscribe@example.com",
                status="active",
                daily_summary=True,
                immediate_red=True,
                immediate_yellow=True,
                unsubscribe_token_hash=service._token_hash(unsubscribe_token),
                consented_at=datetime.now(timezone.utc),
            )
        )
        db.commit()

    client = TestClient(app)
    first_dispatch = client.post(
        "/api/notifications/dispatch",
        json={
            "type": "signal",
            "subject": "RED signal",
            "body": "Immediate market-state alert",
            "dedupeKey": "signal:unsubscribe-before",
            "signal": "RED",
            "channels": ["email"],
        },
        headers={"X-Notification-Secret": "dispatch-secret"},
    )
    assert first_dispatch.status_code == 200
    assert first_dispatch.json()["sent"] == 1
    assert len(sent_messages) == 1
    assert "/api/email-subscription/unsubscribe?token=" in sent_messages[0]["body"]
    unsubscribe_token_from_body = sent_messages[0]["body"].split("token=", 1)[1].splitlines()[0]

    unsubscribed = client.get(f"/api/email-subscription/unsubscribe?token={unsubscribe_token_from_body}")
    assert unsubscribed.status_code == 200
    assert unsubscribed.json()["status"] == "unsubscribed"
    assert unsubscribed.json()["email"] == "unsubscribe@example.com"

    with isolated_dashboard_database() as db:
        subscription = db.get(EmailSubscription, "unsubscribe-user")
        assert subscription is not None
        assert subscription.status == "unsubscribed"
        assert subscription.unsubscribed_at is not None

    second_dispatch = client.post(
        "/api/notifications/dispatch",
        json={
            "type": "signal",
            "subject": "RED signal again",
            "body": "Another market-state alert",
            "dedupeKey": "signal:unsubscribe-after",
            "signal": "RED",
            "channels": ["email"],
        },
        headers={"X-Notification-Secret": "dispatch-secret"},
    )
    assert second_dispatch.status_code == 200
    assert second_dispatch.json() == {"sent": 0, "failed": 0, "duplicate": 0, "skipped": 0}
    assert len(sent_messages) == 1


def test_double_opt_in_confirmation_and_unsubscribe(isolated_dashboard_database):
    with isolated_dashboard_database() as db:
        db.add(_user())
        db.commit()
        service = NotificationService(db, _settings())
        sender = FakeEmailSender()
        service.email_sender = sender

        subscription = service.subscribe(
            "notification-user",
            "USER@example.com",
            daily_summary=True,
            immediate_red=True,
            immediate_yellow=False,
        )

        assert subscription.status == "pending"
        assert sender.messages[0]["to"] == "user@example.com"
        token = sender.messages[0]["body"].split("token=", 1)[1].splitlines()[0]
        assert service.confirm(token).status == "active"

        unsubscribe_token = service._unsubscribe_token("notification-user", "user@example.com")
        assert service.unsubscribe(unsubscribe_token).status == "unsubscribed"


def test_dispatch_records_success_duplicate_and_bounce(isolated_dashboard_database):
    with isolated_dashboard_database() as db:
        db.add(_user())
        db.add(
            EmailSubscription(
                user_id="notification-user",
                email="user@example.com",
                status="active",
                daily_summary=True,
                immediate_red=True,
                immediate_yellow=True,
                unsubscribe_token_hash="stored-token-hash",
                consented_at=datetime.now(timezone.utc),
            )
        )
        db.commit()
        service = NotificationService(db, _settings())
        service.email_sender = FakeEmailSender()

        first = service.dispatch(
            notification_type="signal",
            subject="RED signal",
            body="Immediate market-state alert",
            dedupe_key="signal:NVDA:2026-07-06",
            signal="RED",
            channels=("email",),
        )
        second = service.dispatch(
            notification_type="signal",
            subject="RED signal",
            body="Immediate market-state alert",
            dedupe_key="signal:NVDA:2026-07-06",
            signal="RED",
            channels=("email",),
        )

        assert first.sent == 1
        assert second.duplicate == 1
        delivery = db.scalar(select(NotificationDelivery))
        assert delivery.status == "sent"
        assert delivery.duplicate_count == 1
        assert service.record_provider_event("email.bounced", delivery.provider_message_id) is True
        assert delivery.status == "bounced"
        assert db.get(EmailSubscription, "notification-user").status == "suppressed"


def test_refresh_signal_notifications_respect_signal_type_preferences_and_history(
    monkeypatch,
    isolated_dashboard_database,
):
    settings = _settings()
    monkeypatch.setattr(notification_module, "get_settings", lambda: settings)
    sent_messages: list[dict[str, str]] = []

    def fake_send(self, **message):
        if message["to"] == "fail@example.com":
            raise EmailProviderError("provider rejected recipient")
        sent_messages.append(message)
        return EmailSendResult(provider="resend", message_id=f"signal-{len(sent_messages)}")

    monkeypatch.setattr(notification_module.EmailSender, "send", fake_send)

    with isolated_dashboard_database() as db:
        service = NotificationService(db, settings)
        users = [
            ("red-user", "red@example.com", True, False),
            ("yellow-user", "yellow@example.com", False, True),
            ("fail-user", "fail@example.com", True, False),
        ]
        for user_id, email, immediate_red, immediate_yellow in users:
            unsubscribe_token = service._unsubscribe_token(user_id, email)
            db.add(User(id=user_id, username=user_id, email=email))
            db.add(
                EmailSubscription(
                    user_id=user_id,
                    email=email,
                    status="active",
                    daily_summary=True,
                    immediate_red=immediate_red,
                    immediate_yellow=immediate_yellow,
                    unsubscribe_token_hash=service._token_hash(unsubscribe_token),
                    consented_at=datetime.now(timezone.utc),
                )
            )
        db.add_all(
            [
                _signal(event_key="event-red", ticker="NVDA", signal="RED", event_score=0.91),
                _signal(event_key="event-yellow", ticker="AMD", signal="YELLOW", event_score=0.62),
                _signal(event_key="event-green", ticker="MSFT", signal="GREEN", event_score=0.18),
            ]
        )
        db.commit()

        first = _dispatch_signal_notifications(db)
        second = _dispatch_signal_notifications(db)

        assert first == {"sent": 2, "failed": 1, "duplicate": 0, "skipped": 3}
        assert second == {"sent": 0, "failed": 0, "duplicate": 3, "skipped": 3}
        assert {message["to"] for message in sent_messages} == {
            "red@example.com",
            "yellow@example.com",
        }
        assert all("MSFT" not in message["subject"] for message in sent_messages)

        deliveries = db.scalars(select(NotificationDelivery).order_by(NotificationDelivery.recipient)).all()
        assert [(row.recipient, row.status, row.duplicate_count) for row in deliveries] == [
            ("fail@example.com", "failed", 1),
            ("red@example.com", "sent", 1),
            ("yellow@example.com", "sent", 1),
        ]
        assert {row.notification_type for row in deliveries} == {"signal"}
        assert {row.channel for row in deliveries} == {"email"}
        assert {row.dedupe_key for row in deliveries} == {
            "red-user:signal:event-red:NVDA:2026-07-09",
            "yellow-user:signal:event-yellow:AMD:2026-07-09",
            "fail-user:signal:event-red:NVDA:2026-07-09",
        }
        assert all("event-green" not in row.dedupe_key for row in deliveries)
        failed = [row for row in deliveries if row.status == "failed"]
        assert all(row.error_message == "provider rejected recipient" for row in failed)


def test_green_signal_is_not_dispatched(isolated_dashboard_database):
    with isolated_dashboard_database() as db:
        service = NotificationService(db, _settings())
        result = service.dispatch(
            notification_type="signal",
            subject="GREEN",
            body="No immediate alert",
            dedupe_key="green:1",
            signal="GREEN",
        )
        assert result.skipped == 1


def test_resend_provider_uses_verified_sender_configuration(monkeypatch):
    requests: list[dict[str, object]] = []

    def fake_post(url, *, headers, json, timeout):
        requests.append({"url": url, "headers": headers, "json": json, "timeout": timeout})
        return httpx.Response(200, json={"id": "resend-message-1"}, request=httpx.Request("POST", url))

    monkeypatch.setattr("src.notifier.email_sender.httpx.post", fake_post)
    sender = EmailSender(_settings())

    result = sender.send(
        to="recipient@example.com",
        subject="Provider smoke",
        body="Resend provider configuration check",
        idempotency_key="provider-smoke-key",
    )

    assert result.provider == "resend"
    assert result.message_id == "resend-message-1"
    assert requests == [
        {
            "url": "https://api.resend.com/emails",
            "headers": {
                "Authorization": "Bearer test-key",
                "Idempotency-Key": "provider-smoke-key",
            },
            "json": {
                "from": "FinLightAI <alerts@example.com>",
                "to": ["recipient@example.com"],
                "subject": "Provider smoke",
                "text": "Resend provider configuration check",
            },
            "timeout": 15,
        }
    ]


def test_email_sender_rejects_invalid_sender_address():
    sender = EmailSender(
        Settings(
            app_env="test",
            email_provider="resend",
            resend_api_key="test-key",
            smtp_from="FinLightAI alerts",
        )
    )

    try:
        sender.send(to="recipient@example.com", subject="Invalid", body="Invalid")
    except EmailProviderError as exc:
        assert "SMTP_FROM must include a valid sender email address" in str(exc)
    else:
        raise AssertionError("Expected invalid SMTP_FROM to be rejected")


def test_resend_webhook_signature_is_verified():
    raw_body = b'{"type":"email.bounced"}'
    timestamp = "1783296000"
    message_id = "msg_webhook_1"
    secret_bytes = b"webhook-signing-secret"
    secret = "whsec_" + base64.b64encode(secret_bytes).decode()
    signed = f"{message_id}.{timestamp}.".encode() + raw_body
    signature = base64.b64encode(hmac.new(secret_bytes, signed, hashlib.sha256).digest()).decode()
    now = datetime.fromtimestamp(int(timestamp), timezone.utc)

    assert verify_resend_webhook(
        raw_body=raw_body,
        message_id=message_id,
        timestamp=timestamp,
        signature_header=f"v1,{signature}",
        secret=secret,
        now=now,
    )
    assert not verify_resend_webhook(
        raw_body=raw_body + b" ",
        message_id=message_id,
        timestamp=timestamp,
        signature_header=f"v1,{signature}",
        secret=secret,
        now=now,
    )
