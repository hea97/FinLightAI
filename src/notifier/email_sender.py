from __future__ import annotations

import logging
import smtplib
from dataclasses import dataclass
from email.message import EmailMessage
from email.utils import parseaddr

import httpx

from config.settings import Settings, get_settings

logger = logging.getLogger(__name__)


class EmailProviderError(RuntimeError):
    pass


@dataclass(frozen=True)
class EmailSendResult:
    provider: str
    message_id: str | None


class EmailSender:
    """Transactional email adapter supporting SMTP and Resend."""

    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()

    def send(
        self, *, to: str, subject: str, body: str, idempotency_key: str | None = None
    ) -> EmailSendResult:
        sender = self._validated_sender()
        if self.settings.email_provider == "resend":
            return self._send_resend(
                sender=sender,
                to=to,
                subject=subject,
                body=body,
                idempotency_key=idempotency_key,
            )
        return self._send_smtp(sender=sender, to=to, subject=subject, body=body)

    def _validated_sender(self) -> str:
        sender = (self.settings.smtp_from or "").strip()
        if not sender:
            raise EmailProviderError("SMTP_FROM is required")
        _, address = parseaddr(sender)
        local, separator, domain = address.partition("@")
        if not local or not separator or "." not in domain:
            raise EmailProviderError("SMTP_FROM must include a valid sender email address")
        return sender

    def _send_smtp(self, *, sender: str, to: str, subject: str, body: str) -> EmailSendResult:
        if not self.settings.smtp_host:
            raise EmailProviderError("SMTP_HOST is required")
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = sender
        message["To"] = to
        message.set_content(body)
        try:
            with smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port, timeout=15) as smtp:
                smtp.starttls()
                if self.settings.smtp_username and self.settings.smtp_password:
                    smtp.login(self.settings.smtp_username, self.settings.smtp_password)
                smtp.send_message(message)
        except (OSError, smtplib.SMTPException) as exc:
            raise EmailProviderError(str(exc)) from exc
        return EmailSendResult(provider="smtp", message_id=message.get("Message-ID"))

    def _send_resend(
        self, *, sender: str, to: str, subject: str, body: str, idempotency_key: str | None
    ) -> EmailSendResult:
        if not self.settings.resend_api_key:
            raise EmailProviderError("RESEND_API_KEY is required")
        try:
            headers = {"Authorization": f"Bearer {self.settings.resend_api_key}"}
            if idempotency_key:
                headers["Idempotency-Key"] = idempotency_key[:256]
            response = httpx.post(
                "https://api.resend.com/emails",
                headers=headers,
                json={"from": sender, "to": [to], "subject": subject, "text": body},
                timeout=15,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise EmailProviderError(str(exc)) from exc
        return EmailSendResult(provider="resend", message_id=response.json().get("id"))

    def send_daily_summary(self, subject: str, body: str) -> bool:
        """Backward-compatible one-recipient entrypoint used by older scripts."""
        if not self.settings.alert_email_to:
            logger.warning("ALERT_EMAIL_TO is not configured")
            return False
        try:
            self.send(to=self.settings.alert_email_to, subject=subject, body=body)
        except EmailProviderError:
            logger.exception("Email delivery failed")
            return False
        return True
