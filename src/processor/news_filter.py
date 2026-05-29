from __future__ import annotations

from typing import Any

from config.settings import get_settings


class NewsFilter:
    def __init__(self) -> None:
        self.settings = get_settings()

    def filter(self, articles: list[dict[str, Any]], reliability_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
        filtered: list[dict[str, Any]] = []
        for article, reliability in zip(articles, reliability_results, strict=False):
            content = str(article.get("content") or article.get("description") or "")
            keyword_score = self._keyword_score(f"{article.get('title', '')} {content}")
            if not reliability.get("is_reliable"):
                continue
            if keyword_score < self.settings.min_keyword_score:
                continue
            if len(content) < self.settings.min_content_length:
                continue
            filtered.append({**article, "reliability": reliability, "keyword_score": keyword_score})
        return filtered

    def _keyword_score(self, text: str) -> int:
        lowered = text.lower()
        keywords = ["ai", "semiconductor", "chip", "policy", "export", "nvidia", "samsung", "sk hynix", "tsmc"]
        return sum(1 for keyword in keywords if keyword in lowered)
