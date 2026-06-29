from __future__ import annotations

import re
from typing import Any

from config.settings import get_settings


class NewsFilter:
    TRUSTED_SOURCES = ("reuters", "ap news", "bbc", "bloomberg", "financial times")
    KEYWORDS = ("ai", "semiconductor", "chip", "policy", "export", "nvidia", "samsung", "sk hynix", "tsmc")

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
        return sum(1 for keyword in self.KEYWORDS if keyword in lowered)

    def prepare_records(self, articles: list[dict[str, Any]]) -> list[dict[str, Any]]:
        seen_urls: set[str] = set()
        seen_titles: set[str] = set()
        records: list[dict[str, Any]] = []
        for article in articles:
            title = str(article.get("title") or "")
            content = str(article.get("content") or article.get("summary") or "")
            url = str(article.get("url") or "").strip().lower()
            normalized_title = re.sub(r"[^a-z0-9가-힣]+", " ", title.lower()).strip()
            duplicate = bool((url and url in seen_urls) or (normalized_title and normalized_title in seen_titles))
            if url:
                seen_urls.add(url)
            if normalized_title:
                seen_titles.add(normalized_title)
            source = str(article.get("source") or article.get("domain") or "")
            source_score = 0.9 if any(name in source.lower() for name in self.TRUSTED_SOURCES) else 0.65
            keyword_score = self._keyword_score(f"{title} {content}")
            reliability = article.get("reliability") or {}
            reliability_score = reliability.get("final_score")
            passed = (
                not duplicate
                and source_score >= self.settings.min_source_score
                and keyword_score >= self.settings.min_keyword_score
                and len(content) >= self.settings.min_content_length
            )
            records.append(
                {
                    **article,
                    "source_score": source_score,
                    "keyword_score": keyword_score,
                    "duplicate_flag": duplicate,
                    "content_length": len(content),
                    "passed_filter": passed,
                    "reliability_score": reliability_score,
                }
            )
        return records
