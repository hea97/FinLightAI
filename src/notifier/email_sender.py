from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage

from config.settings import get_settings

logger = logging.getLogger(__name__)


class EmailSender:
    def send_daily_summary(self, subject: str, body: str) -> bool:
        settings = get_settings()
        if not all([settings.smtp_host, settings.smtp_from, settings.alert_email_to]):
            logger.warning("SMTP settings are incomplete")
            return False
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = settings.smtp_from
        message["To"] = settings.alert_email_to
        message.set_content(body)
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as smtp:
            smtp.starttls()
            if settings.smtp_username and settings.smtp_password:
                smtp.login(settings.smtp_username, settings.smtp_password)
            smtp.send_message(message)
        return True
