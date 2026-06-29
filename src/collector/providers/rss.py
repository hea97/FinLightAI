from __future__ import annotations

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from xml.etree import ElementTree

import httpx

from src.collector.providers.base import NewsProviderResult, normalized_article


class RssNewsProvider:
    name = "BBC RSS"

    def __init__(self, url: str, timeout_seconds: float = 10) -> None:
        self.url = url
        self.timeout_seconds = timeout_seconds

    def collect(self, keywords: list[str], max_records: int = 50) -> NewsProviderResult:
        fetched_at = datetime.now(timezone.utc)
        try:
            response = httpx.get(self.url, timeout=self.timeout_seconds)
            response.raise_for_status()
            root = ElementTree.fromstring(response.content)
        except (httpx.HTTPError, ElementTree.ParseError, ValueError) as exc:
            return NewsProviderResult(
                provider=self.name,
                status="failed",
                message=f"RSS collection failed: {type(exc).__name__}",
                fetched_at=fetched_at,
            )

        selected: list[dict] = []
        lowered_keywords = [keyword.lower() for keyword in keywords if keyword.strip()]
        for item in root.findall(".//item"):
            title = item.findtext("title", default="")
            description = item.findtext("description", default="")
            text = f"{title} {description}".lower()
            matched = next((keyword for keyword in lowered_keywords if keyword in text), "")
            if lowered_keywords and not matched:
                continue
            published = self._published_utc(item.findtext("pubDate", default=""))
            selected.append(
                normalized_article(
                    title=title,
                    content=description,
                    source=self.name,
                    url=item.findtext("link", default=""),
                    published_utc=published,
                    provider=self.name,
                    keyword=matched,
                )
            )
            if len(selected) >= max_records:
                break
        status = "healthy" if selected else "partial"
        message = f"Collected {len(selected)} RSS articles" if selected else "RSS returned no matching articles"
        return NewsProviderResult(self.name, selected, status, message, fetched_at)

    @staticmethod
    def _published_utc(value: str) -> str:
        try:
            parsed = parsedate_to_datetime(value)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed.astimezone(timezone.utc).isoformat()
        except (TypeError, ValueError):
            return datetime.now(timezone.utc).isoformat()
