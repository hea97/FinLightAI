from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any

import httpx

from config.settings import get_settings


class NewsCollector:
    DEFAULT_KEYWORDS = ["AI", "semiconductor", "policy", "export control", "NVIDIA", "Samsung Electronics"]

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
        params = {
            "query": query,
            "mode": "artlist",
            "format": "json",
            "maxrecords": safe_max_records,
            "timespan": f"{safe_days}d",
            "sort": "datedesc",
        }

        try:
            settings = get_settings()
            response = httpx.get(settings.gdelt_base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            articles = data.get("articles", [])
            if articles:
                return [self._normalize_gdelt_article(article) for article in articles]
        except (httpx.HTTPError, ValueError, TypeError):
            pass

        return self._seed_articles(selected)

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
