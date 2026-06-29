from __future__ import annotations

import hashlib
import threading
import time
from datetime import datetime, timezone
from typing import Any

import httpx

from config.settings import get_settings
from src.collector.providers import GoogleNewsRssProvider, NewsProviderResult, RssNewsProvider
from src.collector.providers.base import normalized_article


class NewsCollector:
    DEFAULT_KEYWORDS = ["AI", "semiconductor", "policy", "export control", "NVIDIA", "Samsung Electronics"]
    _cache: dict[str, tuple[float, list[dict[str, Any]]]] = {}
    _cache_lock = threading.Lock()
    _last_status: dict[str, str] = {"status": "unknown", "message": "Not checked yet"}
    _provider_statuses: dict[str, dict[str, str]] = {}

    def collect_all(
        self,
        keywords: list[str] | None = None,
        days: int = 1,
        max_records: int = 50,
    ) -> NewsProviderResult:
        selected = keywords or self.DEFAULT_KEYWORDS
        gdelt_articles = self.collect_from_gdelt(selected, days, max_records)
        gdelt_status = self.provider_status()
        rss_result = RssNewsProvider(
            get_settings().bbc_rss_url,
            get_settings().external_api_timeout_seconds,
        ).collect(selected, max_records)
        google_result = GoogleNewsRssProvider(
            get_settings().google_news_rss_url,
            get_settings().external_api_timeout_seconds,
        ).collect(selected, max_records, days=max(days, 7))
        type(self)._provider_statuses["GDELT"] = gdelt_status
        type(self)._provider_statuses[rss_result.provider] = {
            "status": rss_result.status,
            "message": rss_result.message,
        }
        type(self)._provider_statuses[google_result.provider] = {
            "status": google_result.status,
            "message": google_result.message,
        }
        articles = self.deduplicate(gdelt_articles + rss_result.articles + google_result.articles)
        if not articles:
            articles = self._seed_articles(selected)
        real_count = sum(article.get("provider") != "seed" for article in articles)
        if real_count == len(articles) and articles:
            source = "real"
        elif real_count:
            source = "mixed"
        else:
            source = "seed_fallback"
        return NewsProviderResult(
            provider="multi",
            articles=articles,
            status=source,
            message="; ".join(
                f"{provider}: {status['message']}" for provider, status in type(self)._provider_statuses.items()
            ),
        )

    def collect_from_gdelt(
        self,
        keywords: list[str] | None = None,
        days: int = 1,
        max_records: int = 50,
    ) -> list[dict[str, Any]]:
        selected = keywords or self.DEFAULT_KEYWORDS
        safe_days = max(1, min(days, 3))
        safe_max_records = max(1, min(max_records, 200))
        query = self._build_gdelt_query(selected)
        cache_key = f"{query}|{safe_days}|{safe_max_records}"
        settings = get_settings()
        cached = self._get_cached(cache_key, settings.external_api_cache_seconds)
        if cached is not None:
            type(self)._last_status = {"status": "healthy", "message": "Live API cache hit"}
            return cached
        params = {
            "query": query,
            "mode": "artlist",
            "format": "json",
            "maxrecords": safe_max_records,
            "timespan": f"{safe_days}d",
            "sort": "datedesc",
        }

        try:
            response = httpx.get(
                settings.gdelt_base_url,
                params=params,
                headers={
                    "Accept": "application/json",
                    "User-Agent": "FinLightAI/0.1 (+https://github.com/hea97/FinLightAI)",
                },
                timeout=settings.external_api_timeout_seconds,
            )
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, dict):
                raise TypeError("GDELT response is not a JSON object")
            articles = data.get("articles", [])
            if not isinstance(articles, list):
                raise TypeError("GDELT articles field is not a list")
            if articles:
                normalized = [self._normalize_gdelt_article(article) for article in articles]
                self._set_cached(cache_key, normalized)
                type(self)._last_status = {"status": "healthy", "message": "Live API connected"}
                return normalized
            type(self)._last_status = {"status": "partial", "message": "GDELT returned no articles"}
        except httpx.TimeoutException:
            type(self)._last_status = {
                "status": "failed",
                "message": f"GDELT timed out after {settings.external_api_timeout_seconds:g}s",
            }
        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code
            status = "rate_limited" if status_code == 429 else "failed"
            type(self)._last_status = {
                "status": status,
                "message": f"GDELT returned HTTP {status_code}",
            }
        except httpx.HTTPError as exc:
            type(self)._last_status = {
                "status": "failed",
                "message": f"GDELT network failure: {type(exc).__name__}",
            }
        except (ValueError, TypeError) as exc:
            type(self)._last_status = {
                "status": "failed",
                "message": f"GDELT response parsing failed: {type(exc).__name__}",
            }

        return []

    @classmethod
    def provider_status(cls) -> dict[str, str]:
        return dict(cls._last_status)

    @classmethod
    def provider_statuses(cls) -> dict[str, dict[str, str]]:
        return {provider: dict(status) for provider, status in cls._provider_statuses.items()}

    def fallback_articles(self, keywords: list[str] | None = None) -> list[dict[str, Any]]:
        return self._seed_articles(keywords or self.DEFAULT_KEYWORDS)

    @classmethod
    def _get_cached(cls, key: str, ttl_seconds: int) -> list[dict[str, Any]] | None:
        if ttl_seconds <= 0:
            return None
        with cls._cache_lock:
            cached = cls._cache.get(key)
            if not cached or time.monotonic() - cached[0] > ttl_seconds:
                cls._cache.pop(key, None)
                return None
            return [dict(article) for article in cached[1]]

    @classmethod
    def _set_cached(cls, key: str, articles: list[dict[str, Any]]) -> None:
        with cls._cache_lock:
            cls._cache[key] = (time.monotonic(), [dict(article) for article in articles])

    def _build_gdelt_query(self, keywords: list[str]) -> str:
        terms = []
        for keyword in keywords:
            cleaned = keyword.strip()
            if not cleaned:
                continue
            terms.append(f'"{cleaned}"' if " " in cleaned else cleaned)
        return f"({' OR '.join(terms)})" if terms else "(AI OR semiconductor)"

    def _normalize_gdelt_article(self, article: dict[str, Any]) -> dict[str, Any]:
        title = article.get("title") or "Untitled GDELT article"
        domain = article.get("domain") or article.get("sourceCommonName") or article.get("source") or "GDELT"
        published_at = article.get("seendate") or datetime.now(timezone.utc).isoformat()
        return normalized_article(
            source=domain,
            title=title,
            content=article.get("description") or title,
            published_utc=published_at,
            provider="GDELT",
            keyword="",
            raw_payload=article,
            url=article.get("url", ""),
            author="GDELT",
            domain=domain,
            image_url=article.get("socialimage", ""),
            language=article.get("language", ""),
            source_country=article.get("sourceCountry", ""),
        )

    def _seed_articles(self, selected: list[str]) -> list[dict[str, Any]]:
        return [
            {
                "source": "Reuters",
                "title": f"Semiconductor policy update affects AI chip supply: {selected[0]}",
                "content": (
                    "Reuters reported a semiconductor policy update affecting AI chip supply chains and market expectations. "
                    "The article describes how AI chip makers, export policy officials, and semiconductor suppliers are "
                    "watching volume, pricing, and volatility in the United States and Korea. Analysts said the policy "
                    "change may create short term market risk while companies assess supply chain exposure."
                ),
                "author": "FinLightAI Seed",
                "url": "https://www.reuters.com/technology/semiconductor-policy-ai-chip-supply",
                "published_utc": datetime.now(timezone.utc).isoformat(),
                "published_at": datetime.now(timezone.utc).isoformat(),
                "domain": "reuters.com",
                "language": "English",
                "source_country": "US",
                "provider": "seed",
                "keyword": selected[0],
                "raw_payload": None,
            }
        ]

    def collect_from_newsapi(self, keywords: list[str] | None = None, from_date: str | None = None) -> list[dict[str, Any]]:
        settings = get_settings()
        if not settings.news_api_key:
            type(self)._provider_statuses["NewsAPI"] = {
                "status": "disabled",
                "message": "NEWS_API_KEY is not configured",
            }
            return []
        selected = keywords or self.DEFAULT_KEYWORDS
        try:
            response = httpx.get(
                "https://newsapi.org/v2/everything",
                params={"q": " OR ".join(selected), "from": from_date, "sortBy": "publishedAt", "pageSize": 100},
                headers={"X-Api-Key": settings.news_api_key},
                timeout=settings.external_api_timeout_seconds,
            )
            response.raise_for_status()
            payload = response.json()
            articles = [
                normalized_article(
                    title=item.get("title") or "",
                    content=item.get("content") or item.get("description") or "",
                    source=(item.get("source") or {}).get("name") or "NewsAPI",
                    url=item.get("url") or "",
                    published_utc=item.get("publishedAt") or datetime.now(timezone.utc).isoformat(),
                    provider="NewsAPI",
                    raw_payload=item,
                )
                for item in payload.get("articles", [])
            ]
            type(self)._provider_statuses["NewsAPI"] = {
                "status": "healthy" if articles else "partial",
                "message": f"Collected {len(articles)} articles",
            }
            return articles
        except (httpx.HTTPError, ValueError, TypeError) as exc:
            type(self)._provider_statuses["NewsAPI"] = {
                "status": "failed",
                "message": f"NewsAPI collection failed: {type(exc).__name__}",
            }
            return []

    def deduplicate(self, articles: list[dict[str, Any]]) -> list[dict[str, Any]]:
        seen: set[str] = set()
        unique: list[dict[str, Any]] = []
        for article in articles:
            fingerprint = self._fingerprint(article)
            if fingerprint in seen:
                continue
            seen.add(fingerprint)
            unique.append(article)
        return unique

    def _fingerprint(self, article: dict[str, Any]) -> str:
        raw = f"{article.get('url', '')}|{article.get('title', '')}".lower().strip()
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()
