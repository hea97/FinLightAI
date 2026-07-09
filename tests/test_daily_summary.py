from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import select

from config.settings import Settings
from scripts.send_daily_summary import build_daily_summary, send_daily_summary
from src.dashboard.models import EmailSubscription, NotificationDelivery, Signal, User
from src.notifier.email_sender import EmailSendResult
from src.notifier.notification_service import NotificationService


def _settings() -> Settings:
    return Settings(
        app_env="test",
        smtp_from="FinLightAI <alerts@example.com>",
        email_provider="resend",
        resend_api_key="test-key",
        notification_token_secret="test-token-secret",
        backend_url="https://api.example.com",
    )


def _signal(
    *,
    event_key: str,
    ticker: str,
    trade_date: date,
    signal: str,
    event_score: float,
    created_at: datetime,
) -> Signal:
    return Signal(
        event_key=event_key,
        ticker=ticker,
        trade_date=trade_date,
        event_score=event_score,
        market_reaction_score=0.42,
        signal=signal,
        evidence={"headline": f"{ticker} {signal} highlight"},
        data_source="real",
        created_at=created_at,
    )


def test_build_daily_summary_counts_green_and_highlights_latest_signals():
    signals = [
        _signal(
            event_key="red-1",
            ticker="NVDA",
            trade_date=date(2026, 7, 9),
            signal="RED",
            event_score=0.91,
            created_at=datetime(2026, 7, 9, 1, tzinfo=timezone.utc),
        ),
        _signal(
            event_key="yellow-1",
            ticker="AMD",
            trade_date=date(2026, 7, 9),
            signal="YELLOW",
            event_score=0.62,
            created_at=datetime(2026, 7, 9, 0, tzinfo=timezone.utc),
        ),
        _signal(
            event_key="green-1",
            ticker="MSFT",
            trade_date=date(2026, 7, 8),
            signal="GREEN",
            event_score=0.12,
            created_at=datetime(2026, 7, 8, 23, tzinfo=timezone.utc),
        ),
    ]

    subject, body, dedupe_key = build_daily_summary(signals, date(2026, 7, 9))

    assert subject == "[FinLightAI] 2026-07-09 daily market summary"
    assert dedupe_key == "daily-summary:2026-07-09"
    assert "KST date: 2026-07-09" in body
    assert "Signal counts: RED 1 / YELLOW 1 / GREEN 1" in body
    assert "Latest signal highlights:" in body
    assert "- NVDA: RED (event score 0.9, trade date 2026-07-09)" in body
    assert "- AMD: YELLOW (event score 0.6, trade date 2026-07-09)" in body
    assert "- MSFT: GREEN (event score 0.1, trade date 2026-07-08)" in body


def test_send_daily_summary_uses_kst_date_and_prevents_same_day_duplicates(
    monkeypatch,
    isolated_dashboard_database,
):
    settings = _settings()
    monkeypatch.setattr("src.notifier.notification_service.get_settings", lambda: settings)
    sent_messages: list[dict[str, str]] = []

    def fake_send(self, **message):
        sent_messages.append(message)
        return EmailSendResult(provider="resend", message_id=f"daily-{len(sent_messages)}")

    monkeypatch.setattr("src.notifier.email_sender.EmailSender.send", fake_send)

    with isolated_dashboard_database() as db:
        service = NotificationService(db, settings)
        unsubscribe_token = service._unsubscribe_token("daily-user", "daily@example.com")
        db.add(User(id="daily-user", username="Daily User", email="daily@example.com"))
        db.add(
            EmailSubscription(
                user_id="daily-user",
                email="daily@example.com",
                status="active",
                daily_summary=True,
                immediate_red=True,
                immediate_yellow=True,
                unsubscribe_token_hash=service._token_hash(unsubscribe_token),
                consented_at=datetime.now(timezone.utc),
            )
        )
        db.add_all(
            [
                _signal(
                    event_key="daily-red",
                    ticker="NVDA",
                    trade_date=date(2026, 7, 9),
                    signal="RED",
                    event_score=0.93,
                    created_at=datetime(2026, 7, 9, 2, tzinfo=timezone.utc),
                ),
                _signal(
                    event_key="daily-yellow",
                    ticker="AMD",
                    trade_date=date(2026, 7, 9),
                    signal="YELLOW",
                    event_score=0.57,
                    created_at=datetime(2026, 7, 9, 1, tzinfo=timezone.utc),
                ),
                _signal(
                    event_key="daily-green",
                    ticker="MSFT",
                    trade_date=date(2026, 7, 9),
                    signal="GREEN",
                    event_score=0.21,
                    created_at=datetime(2026, 7, 9, 0, tzinfo=timezone.utc),
                ),
            ]
        )
        db.commit()

        first = send_daily_summary(db, today=date(2026, 7, 9))
        second = send_daily_summary(db, today=date(2026, 7, 9))

        assert first.sent == 1
        assert second.duplicate == 1
        assert len(sent_messages) == 1
        assert sent_messages[0]["subject"] == "[FinLightAI] 2026-07-09 daily market summary"
        assert "KST date: 2026-07-09" in sent_messages[0]["body"]
        assert "Signal counts: RED 1 / YELLOW 1 / GREEN 1" in sent_messages[0]["body"]
        assert "- NVDA: RED (event score 0.9, trade date 2026-07-09)" in sent_messages[0]["body"]

        delivery = db.scalar(
            select(NotificationDelivery).where(
                NotificationDelivery.notification_type == "daily_summary",
                NotificationDelivery.channel == "email",
            )
        )
        assert delivery is not None
        assert delivery.dedupe_key == "daily-user:daily-summary:2026-07-09"
        assert delivery.duplicate_count == 1
