from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

import httpx

from config.settings import get_settings

logger = logging.getLogger(__name__)


class DiscordNotifier:
    COLORS = {"RED": 0xE53935, "YELLOW": 0xFDD835, "GREEN": 0x43A047}

    def __init__(self, webhook_url: str | None = None, client: httpx.Client | None = None) -> None:
        self.webhook_url = webhook_url if webhook_url is not None else get_settings().discord_webhook_url
        self.client = client or httpx.Client(timeout=10)

    def build_signal_payload(self, signal: str, ticker: str, data: dict[str, Any]) -> dict[str, Any]:
        color = self.COLORS.get(signal.upper(), self.COLORS["GREEN"])
        title_prefix = {"RED": "RED signal", "YELLOW": "YELLOW signal", "GREEN": "GREEN signal"}.get(signal.upper(), "Signal")
        return {
            "embeds": [
                {
                    "title": f"{title_prefix} | {ticker}",
                    "description": str(data.get("headline", "No headline provided")),
                    "color": color,
                    "fields": [
                        {"name": "Return 1D", "value": f"{data.get('return_1d', 0):.2%}", "inline": True},
                        {"name": "Volume Ratio", "value": f"{data.get('volume_ratio', 0):.2f}x", "inline": True},
                        {"name": "Reliability", "value": f"{data.get('reliability_score', 0):.2f}", "inline": True},
                        {"name": "Sentiment", "value": str(data.get("sentiment_label", "neutral")), "inline": True},
                    ],
                    "timestamp": data.get("timestamp") or datetime.now(timezone.utc).isoformat(),
                    "footer": {"text": "FinLightAI market-state alert. Not investment advice."},
                }
            ]
        }

    def send_signal_alert(self, signal: str, ticker: str, data: dict[str, Any]) -> bool:
        if signal.upper() not in {"RED", "YELLOW"}:
            logger.info("Skipping Discord alert for non-alert signal: %s", signal)
            return False
        if not self.webhook_url:
            logger.warning("Discord webhook URL is not configured")
            return False

        payload = self.build_signal_payload(signal, ticker, data)
        response = self.client.post(self.webhook_url, json=payload)
        if response.status_code not in {200, 204}:
            logger.error("Discord webhook failed with status %s: %s", response.status_code, response.text)
            return False
        return True

    def send_daily_summary(self, summary: dict[str, Any]) -> bool:
        if not self.webhook_url:
            logger.warning("Discord webhook URL is not configured")
            return False
        response = self.client.post(self.webhook_url, json={"content": summary.get("message", "FinLightAI daily summary")})
        return response.status_code in {200, 204}
