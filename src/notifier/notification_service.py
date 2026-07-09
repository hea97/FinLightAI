from __future__ import annotations

import hashlib
import hmac
import base64
import binascii
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from config.settings import Settings, get_settings
from src.dashboard.models import EmailSubscription, NotificationDelivery, User
from src.notifier.email_sender import EmailProviderError, EmailSender


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class DispatchResult:
    sent: int = 0
    failed: int = 0
    duplicate: int = 0
    skipped: int = 0


class NotificationService:
    def __init__(self, db: Session, settings: Settings | None = None):
        self.db = db
        self.settings = settings or get_settings()
        self.email_sender = EmailSender(self.settings)

    def _token_hash(self, token: str) -> str:
        secret = self.settings.notification_token_secret or self.settings.jwt_secret_key
        if not secret:
            if not self.settings.is_development():
                raise RuntimeError("NOTIFICATION_TOKEN_SECRET is required")
            secret = "finlight-local-notification-secret"
        return hmac.new(secret.encode(), token.encode(), hashlib.sha256).hexdigest()

    def _unsubscribe_token(self, user_id: str, email: str) -> str:
        signature = self._token_hash(f"unsubscribe:{user_id}:{email}")
        return f"{user_id}.{signature}"

    def subscribe(
        self,
        user_id: str,
        email: str,
        *,
        daily_summary: bool,
        immediate_red: bool,
        immediate_yellow: bool,
    ) -> EmailSubscription:
        email = email.strip().lower()
        confirm_token = secrets.token_urlsafe(32)
        unsubscribe_token = self._unsubscribe_token(user_id, email)
        subscription = self.db.get(EmailSubscription, user_id)
        email_changed = subscription is None or subscription.email != email
        if subscription is None:
            subscription = EmailSubscription(
                user_id=user_id,
                email=email,
                unsubscribe_token_hash=self._token_hash(unsubscribe_token),
            )
            self.db.add(subscription)
        subscription.email = email
        subscription.daily_summary = daily_summary
        subscription.immediate_red = immediate_red
        subscription.immediate_yellow = immediate_yellow
        if email_changed or subscription.status != "active":
            subscription.status = "pending"
            subscription.confirm_token_hash = self._token_hash(confirm_token)
            subscription.unsubscribe_token_hash = self._token_hash(unsubscribe_token)
            subscription.token_expires_at = utc_now() + timedelta(hours=24)
            subscription.consented_at = None
            subscription.unsubscribed_at = None
            self.db.flush()
            self._send_confirmation(subscription, confirm_token)
        self.db.commit()
        self.db.refresh(subscription)
        return subscription

    def _send_confirmation(self, subscription: EmailSubscription, token: str) -> None:
        base_url = (self.settings.backend_url or "http://127.0.0.1:8000").rstrip("/")
        confirm_url = f"{base_url}/api/email-subscription/confirm?token={token}"
        key = f"{subscription.user_id}:double-opt-in:{self._token_hash(token)[:16]}"
        delivery = self._delivery(
            subscription, "email", "double_opt_in", key, self.settings.email_provider
        )
        try:
            result = self.email_sender.send(
                to=subscription.email,
                subject="[FinLightAI] 이메일 알림 구독을 확인해 주세요",
                body=f"아래 링크를 24시간 안에 열어 구독을 확인해 주세요.\n\n{confirm_url}\n\n요청하지 않았다면 무시하세요.",
                idempotency_key=key,
            )
            delivery.status = "sent"
            delivery.provider_message_id = result.message_id
            self.db.commit()
        except EmailProviderError as exc:
            delivery.status = "failed"
            delivery.error_message = str(exc)[:2000]
            self.db.commit()
            raise

    def confirm(self, token: str) -> EmailSubscription | None:
        subscription = self.db.scalar(
            select(EmailSubscription).where(EmailSubscription.confirm_token_hash == self._token_hash(token))
        )
        if not subscription or not subscription.token_expires_at:
            return None
        expires_at = subscription.token_expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at < utc_now():
            return None
        subscription.status = "active"
        subscription.consented_at = utc_now()
        subscription.confirm_token_hash = None
        subscription.token_expires_at = None
        self.db.commit()
        self.db.refresh(subscription)
        return subscription

    def unsubscribe(self, token: str) -> EmailSubscription | None:
        subscription = self.db.scalar(
            select(EmailSubscription).where(EmailSubscription.unsubscribe_token_hash == self._token_hash(token))
        )
        if not subscription:
            return None
        subscription.status = "unsubscribed"
        subscription.unsubscribed_at = utc_now()
        self.db.commit()
        self.db.refresh(subscription)
        return subscription

    def dispatch(
        self,
        *,
        notification_type: str,
        subject: str,
        body: str,
        dedupe_key: str,
        signal: str | None = None,
        channels: tuple[str, ...] = ("email", "kakao"),
    ) -> DispatchResult:
        if notification_type == "signal" and signal not in {"RED", "YELLOW"}:
            return DispatchResult(skipped=1)
        totals = {"sent": 0, "failed": 0, "duplicate": 0, "skipped": 0}
        subscriptions = self.db.scalars(
            select(EmailSubscription).where(EmailSubscription.status == "active")
        ).all()
        for subscription in subscriptions:
            enabled = (
                subscription.daily_summary
                if notification_type == "daily_summary"
                else subscription.immediate_red if signal == "RED" else subscription.immediate_yellow
            )
            if not enabled:
                totals["skipped"] += 1
                continue
            if "email" in channels:
                self._deliver_email(subscription, notification_type, subject, body, dedupe_key, totals)
            if "kakao" in channels:
                self._deliver_kakao(subscription, notification_type, subject, body, dedupe_key, signal, totals)
        return DispatchResult(**totals)

    def _existing(self, channel: str, dedupe_key: str) -> NotificationDelivery | None:
        return self.db.scalar(
            select(NotificationDelivery).where(
                NotificationDelivery.channel == channel,
                NotificationDelivery.dedupe_key == dedupe_key,
            )
        )

    def _record_duplicate(self, delivery: NotificationDelivery) -> None:
        delivery.duplicate_count += 1
        delivery.last_duplicate_at = utc_now()
        self.db.commit()

    def _delivery(self, subscription: EmailSubscription, channel: str, kind: str, key: str, provider: str):
        delivery = NotificationDelivery(
            id=str(uuid4()),
            user_id=subscription.user_id,
            channel=channel,
            notification_type=kind,
            recipient=subscription.email if channel == "email" else subscription.user_id,
            dedupe_key=key,
            status="processing",
            provider=provider,
        )
        self.db.add(delivery)
        self.db.flush()
        return delivery

    def _deliver_email(self, sub, kind, subject, body, key, totals) -> None:
        channel_key = f"{sub.user_id}:{key}"
        existing = self._existing("email", channel_key)
        if existing:
            self._record_duplicate(existing)
            totals["duplicate"] += 1
            return
        delivery = self._delivery(sub, "email", kind, channel_key, self.settings.email_provider)
        try:
            base_url = (self.settings.backend_url or "http://127.0.0.1:8000").rstrip("/")
            unsubscribe_url = (
                f"{base_url}/api/email-subscription/unsubscribe"
                f"?token={self._unsubscribe_token(sub.user_id, sub.email)}"
            )
            email_body = f"{body}\n\n수신 거부: {unsubscribe_url}"
            result = self.email_sender.send(
                to=sub.email,
                subject=subject,
                body=email_body,
                idempotency_key=channel_key,
            )
            delivery.status = "sent"
            delivery.provider_message_id = result.message_id
            totals["sent"] += 1
        except EmailProviderError as exc:
            delivery.status = "failed"
            delivery.error_message = str(exc)[:2000]
            totals["failed"] += 1
        self.db.commit()

    def _deliver_kakao(self, sub, kind, subject, body, key, signal, totals) -> None:
        channel_key = f"{sub.user_id}:{key}"
        existing = self._existing("kakao", channel_key)
        if existing:
            self._record_duplicate(existing)
            totals["duplicate"] += 1
            return
        delivery = self._delivery(sub, "kakao", kind, channel_key, "n8n")
        delivery.metadata_json = {"signal": signal} if signal else {}
        if not self.settings.kakao_channel_approved or not self.settings.n8n_kakao_webhook_url:
            delivery.status = "failed"
            delivery.error_message = "Kakao channel approval or N8N_KAKAO_WEBHOOK_URL is missing"
            totals["failed"] += 1
            self.db.commit()
            return
        headers = {}
        if self.settings.n8n_webhook_token:
            headers["Authorization"] = f"Bearer {self.settings.n8n_webhook_token}"
        try:
            response = httpx.post(
                self.settings.n8n_kakao_webhook_url,
                headers=headers,
                json={
                    "eventId": key,
                    "userId": sub.user_id,
                    "type": kind,
                    "signal": signal,
                    "title": subject,
                    "message": body,
                },
                timeout=15,
            )
            response.raise_for_status()
            payload = response.json() if response.content else {}
            delivery.status = "sent"
            delivery.provider_message_id = payload.get("messageId") or payload.get("executionId")
            totals["sent"] += 1
        except (httpx.HTTPError, ValueError) as exc:
            delivery.status = "failed"
            delivery.error_message = str(exc)[:2000]
            totals["failed"] += 1
        self.db.commit()

    def record_provider_event(self, event_type: str, provider_message_id: str) -> bool:
        delivery = self.db.scalar(
            select(NotificationDelivery).where(
                NotificationDelivery.provider_message_id == provider_message_id
            )
        )
        if not delivery:
            return False
        normalized = {
            "email.delivered": "delivered",
            "email.bounced": "bounced",
            "email.complained": "complained",
            "email.failed": "failed",
            "email.delivery_delayed": "delayed",
        }.get(event_type)
        if not normalized:
            return False
        delivery.status = normalized
        if normalized in {"bounced", "complained"} and delivery.user_id:
            subscription = self.db.get(EmailSubscription, delivery.user_id)
            if subscription:
                subscription.status = "suppressed"
        self.db.commit()
        return True


def verify_resend_webhook(
    *,
    raw_body: bytes,
    message_id: str,
    timestamp: str,
    signature_header: str,
    secret: str,
    now: datetime | None = None,
) -> bool:
    """Verify Resend's Svix signature against the unmodified request body."""
    try:
        timestamp_int = int(timestamp)
        current = int((now or utc_now()).timestamp())
        if abs(current - timestamp_int) > 300:
            return False
        encoded_secret = secret.removeprefix("whsec_")
        secret_bytes = base64.b64decode(encoded_secret)
        signed = f"{message_id}.{timestamp}.".encode() + raw_body
        expected = base64.b64encode(hmac.new(secret_bytes, signed, hashlib.sha256).digest()).decode()
    except (ValueError, TypeError, binascii.Error):
        return False
    signatures = [
        item.split(",", 1)[1]
        for item in signature_header.split()
        if item.startswith("v1,") and "," in item
    ]
    return any(hmac.compare_digest(expected, candidate) for candidate in signatures)
