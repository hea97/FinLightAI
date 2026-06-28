from __future__ import annotations

import hashlib
import threading
import time
from datetime import datetime, timezone
from typing import Any

import httpx

from config.settings import get_settings


class NewsCollector:
    DEFAULT_KEYWORDS = ["AI", "semiconductor", "policy", "export control", "NVIDIA", "Samsung Electronics"]
    _cache: dict[str, tuple[float, list[dict[str, Any]]]] = {}
    _cache_lock = threading.Lock()
    _last_status: dict[str, str] = {"status": "unknown", "message": "Not checked yet"}

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
                timeout=settings.external_api_timeout_seconds,
            )
            response.raise_for_status()
            data = response.json()
            articles = data.get("articles", [])
            if articles:
                normalized = [self._normalize_gdelt_article(article) for article in articles]
                self._set_cached(cache_key, normalized)
                type(self)._last_status = {"status": "healthy", "message": "Live API connected"}
                return normalized
            type(self)._last_status = {"status": "partial", "message": "Live API returned no articles; using seed fallback"}
        except httpx.TimeoutException:
            type(self)._last_status = {"status": "failed", "message": "Live API timed out; using seed fallback"}
        except (httpx.HTTPError, ValueError, TypeError):
            type(self)._last_status = {"status": "failed", "message": "Live API request failed; using seed fallback"}

        return self._seed_articles(selected)

    @classmethod
    def provider_status(cls) -> dict[str, str]:
        return dict(cls._last_status)

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
        return {
            "source": domain,
            "title": title,
            "content": article.get("description") or title,
            "author": "GDELT",
            "url": article.get("url", ""),
            "published_at": published_at,
            "domain": domain,
            "image_url": article.get("socialimage", ""),
            "language": article.get("language", ""),
            "source_country": article.get("sourceCountry", ""),
            "provider": "GDELT",
        }

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
                "published_at": datetime.now(timezone.utc).isoformat(),
                "domain": "reuters.com",
                "language": "English",
                "source_country": "US",
                "provider": "seed",
            }
        ]

    def collect_from_newsapi(self, keywords: list[str] | None = None, from_date: str | None = None) -> list[dict[str, Any]]:
        selected = keywords or self.DEFAULT_KEYWORDS
        return [
            {
                "source": "AP News",
                "title": f"AI chip makers watch policy headlines: {selected[-1]}",
                "content": (
                    "Multiple AI chip makers are monitoring semiconductor policy headlines while investors assess volume "
                    "and volatility. The report describes export control risk, GPU supply conditions, and market reaction "
                    "among chip suppliers. It gives additional coverage of the same policy event without issuing investment advice."
                ),
                "author": "FinLightAI Seed",
                "url": "https://apnews.com/article/ai-chip-policy-market",
                "published_at": datetime.now(timezone.utc).isoformat(),
            }
        ]

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
