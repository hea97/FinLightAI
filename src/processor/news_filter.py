from __future__ import annotations

from typing import Any

from config.settings import get_settings
from src.processor.news_relevance import contains_term, normalize_title, relevance_score


class NewsFilter:
    TRUSTED_SOURCES = ("reuters", "ap news", "bbc", "bloomberg", "financial times")
    QUALIFIED_FINANCE_SOURCES = (
        "cnbc",
        "yahoo finance",
        "nasdaq",
        "marketwatch",
        "techcrunch",
        "nvidia newsroom",
        "nvidia blog",
        "nvidia developer",
        "supermicro",
    )
    RSS_PROVIDERS = ("BBC RSS", "Google News RSS")
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
        return sum(1 for keyword in self.KEYWORDS if contains_term(text, keyword))

    def prepare_records(self, articles: list[dict[str, Any]]) -> list[dict[str, Any]]:
        seen_urls: set[str] = set()
        seen_titles: set[str] = set()
        records: list[dict[str, Any]] = []
        for article in articles:
            title = str(article.get("title") or "")
            content = str(article.get("content") or article.get("summary") or "")
            url = str(article.get("url") or "").strip().lower()
            normalized_title = normalize_title(title)
            duplicate = bool((url and url in seen_urls) or (normalized_title and normalized_title in seen_titles))
            if url:
                seen_urls.add(url)
            if normalized_title:
                seen_titles.add(normalized_title)
            source = str(article.get("source") or article.get("domain") or "")
            source_lower = source.lower()
            if any(name in source_lower for name in self.TRUSTED_SOURCES):
                source_score = 0.9
            elif any(name in source_lower for name in self.QUALIFIED_FINANCE_SOURCES):
                source_score = 0.8
            else:
                source_score = 0.65
            keyword_score = self._keyword_score(f"{title} {content}")
            article_relevance_score = relevance_score(f"{title} {content}")
            reliability = article.get("reliability") or {}
            reliability_score = reliability.get("final_score")
            provider = str(article.get("provider") or "")
            min_content_length = (
                self.settings.min_rss_content_length
                if provider in self.RSS_PROVIDERS
                else self.settings.min_content_length
            )
            filter_reasons: list[str] = []
            if duplicate:
                filter_reasons.append("duplicate_title_or_url")
            if source_score < self.settings.min_source_score:
                filter_reasons.append("source_score_below_threshold")
            if keyword_score < self.settings.min_keyword_score:
                filter_reasons.append("keyword_score_below_threshold")
            if article_relevance_score < 1:
                filter_reasons.append("no_relevant_finance_terms")
            if len(content) < min_content_length:
                filter_reasons.append("content_too_short")
            passed = not filter_reasons
            records.append(
                {
                    **article,
                    "source_score": source_score,
                    "keyword_score": keyword_score,
                    "relevance_score": article_relevance_score,
                    "duplicate_flag": duplicate,
                    "content_length": len(content),
                    "passed_filter": passed,
                    "reliability_score": reliability_score,
                    "filter_reasons": filter_reasons,
                }
            )
        return records
