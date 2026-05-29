from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any


class NewsCollector:
    DEFAULT_KEYWORDS = ["AI", "semiconductor", "policy", "export control", "NVIDIA", "Samsung Electronics"]

    def collect_from_gdelt(self, keywords: list[str] | None = None, days: int = 1) -> list[dict[str, Any]]:
        selected = keywords or self.DEFAULT_KEYWORDS
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
