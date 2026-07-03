from __future__ import annotations

import html
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from xml.etree import ElementTree

import httpx

from src.collector.providers.base import NewsProviderResult, normalized_article
from src.processor.news_relevance import matched_relevance_terms


class GoogleNewsRssProvider:
    name = "Google News RSS"

    def __init__(self, url: str, timeout_seconds: float = 10) -> None:
        self.url = url
        self.timeout_seconds = timeout_seconds

    def collect(
        self,
        keywords: list[str],
        max_records: int = 50,
        days: int = 7,
    ) -> NewsProviderResult:
        fetched_at = datetime.now(timezone.utc)
        query = self._query(keywords, days)
        try:
            response = httpx.get(
                self.url,
                params={
                    "q": query,
                    "hl": "en-US",
                    "gl": "US",
                    "ceid": "US:en",
                },
                headers={"User-Agent": "FinLightAI/0.1 (+https://github.com/hea97/FinLightAI)"},
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            root = ElementTree.fromstring(response.content)
        except httpx.TimeoutException:
            return NewsProviderResult(
                provider=self.name,
                status="failed",
                message=f"Google News RSS timed out after {self.timeout_seconds:g}s",
                fetched_at=fetched_at,
            )
        except (httpx.HTTPError, ElementTree.ParseError, ValueError) as exc:
            return NewsProviderResult(
                provider=self.name,
                status="failed",
                message=f"Google News RSS collection failed: {type(exc).__name__}",
                fetched_at=fetched_at,
            )

        selected: list[dict] = []
        for item in root.findall(".//item"):
            title = self._plain_text(item.findtext("title", default=""))
            summary = self._plain_text(item.findtext("description", default=""))
            matches = matched_relevance_terms(f"{title} {summary}")
            if not matches:
                continue
            source = self._plain_text(item.findtext("source", default="")) or self.name
            published = self._published_utc(item.findtext("pubDate", default=""))
            raw_payload = {
                "guid": item.findtext("guid", default=""),
                "source": source,
                "query": query,
            }
            selected.append(
                normalized_article(
                    title=title,
                    content=summary,
                    source=source,
                    url=item.findtext("link", default=""),
                    published_utc=published,
                    provider=self.name,
                    keyword=", ".join(matches),
                    raw_payload=raw_payload,
                    matched_keywords=matches,
                    relevance_score=len(matches),
                )
            )
            if len(selected) >= max_records:
                break

        status = "healthy" if selected else "partial"
        message = (
            f"Collected {len(selected)} relevant articles"
            if selected
            else "Google News RSS returned no relevant articles"
        )
        return NewsProviderResult(self.name, selected, status, message, fetched_at)

    @staticmethod
    def _query(keywords: list[str], days: int) -> str:
        terms = []
        for keyword in keywords:
            cleaned = " ".join(keyword.split())
            if not cleaned:
                continue
            terms.append(f'"{cleaned}"' if " " in cleaned else cleaned)
        bounded_days = max(1, min(days, 30))
        return f"({' OR '.join(terms)}) when:{bounded_days}d"

    @staticmethod
    def _plain_text(value: str) -> str:
        without_tags = re.sub(r"<[^>]+>", " ", html.unescape(value or ""))
        return " ".join(without_tags.split())

    @staticmethod
    def _published_utc(value: str) -> str:
        try:
            parsed = parsedate_to_datetime(value)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed.astimezone(timezone.utc).isoformat()
        except (TypeError, ValueError):
            return datetime.now(timezone.utc).isoformat()
