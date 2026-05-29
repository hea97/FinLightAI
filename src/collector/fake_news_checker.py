from __future__ import annotations

import math
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from difflib import SequenceMatcher
from typing import Any
from urllib.parse import urlparse


def _text(value: Any) -> str:
    return str(value or "").strip()


def _parse_datetime(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if not value:
        return None
    raw = str(value).replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


class SourceVerifier:
    TRUSTED_SOURCES = {
        "yonhap.co.kr": 1.0,
        "chosun.com": 0.9,
        "joongang.co.kr": 0.9,
        "mk.co.kr": 0.85,
        "hankyung.com": 0.85,
        "edaily.co.kr": 0.8,
        "reuters.com": 1.0,
        "bloomberg.com": 1.0,
        "wsj.com": 0.95,
        "ft.com": 0.95,
        "cnbc.com": 0.85,
        "apnews.com": 1.0,
    }

    def get_source_score(self, url: str) -> float:
        host = urlparse(url).netloc.lower().removeprefix("www.")
        for domain, score in self.TRUSTED_SOURCES.items():
            if host == domain or host.endswith(f".{domain}"):
                return score
        return 0.3

    def check_author_byline(self, article: dict[str, Any]) -> bool:
        return bool(_text(article.get("author")) or _text(article.get("byline")))


class DateManipulationDetector:
    DATE_PATTERN = re.compile(r"\b(20\d{2}|19\d{2})[-./년 ]?(0?[1-9]|1[0-2])?[-./월 ]?(0?[1-9]|[12]\d|3[01])?")

    def detect_recycled_news(self, article: dict[str, Any], window_days: int = 30) -> bool:
        published_at = _parse_datetime(article.get("published_at"))
        if not published_at:
            return True
        years = [int(match.group(1)) for match in self.DATE_PATTERN.finditer(_text(article.get("content")))]
        if not years:
            return False
        return any(abs(published_at.year - year) * 365 > window_days for year in years)

    def check_date_context_mismatch(self, title: str, content: str, published_at: str) -> float:
        published = _parse_datetime(published_at)
        if not published:
            return 1.0
        years = [int(match.group(1)) for match in self.DATE_PATTERN.finditer(f"{title} {content}")]
        if not years:
            return 0.0
        closest_gap = min(abs(published.year - year) for year in years)
        return min(1.0, closest_gap / 3)


class SensationalismDetector:
    CLICKBAIT_PATTERNS = [
        r"충격[!！]?",
        r"긴급[!！]?",
        r"경악[!！]?",
        r"단독[!！]?",
        r"속보[!！]?",
        r"폭락[!！]?",
        r"폭등[!！]?",
        r"BREAKING",
        r"URGENT",
        r"SHOCKING",
        r"EXCLUSIVE",
    ]

    def calculate_sensationalism_score(self, title: str) -> float:
        if not title:
            return 0.0
        hits = sum(1 for pattern in self.CLICKBAIT_PATTERNS if re.search(pattern, title, re.IGNORECASE))
        punctuation_boost = min(title.count("!") + title.count("？") + title.count("?"), 3) * 0.1
        return min(1.0, hits * 0.3 + punctuation_boost)

    def check_headline_body_consistency(self, title: str, content: str) -> float:
        title_words = set(re.findall(r"[\w가-힣]{2,}", title.lower()))
        content_words = set(re.findall(r"[\w가-힣]{2,}", content.lower()))
        if not title_words or not content_words:
            return 0.0
        overlap = len(title_words & content_words) / len(title_words)
        sequence = SequenceMatcher(None, title.lower(), content[: max(len(title) * 4, 1)].lower()).ratio()
        return min(1.0, (overlap * 0.75) + (sequence * 0.25))


class CrossReferenceChecker:
    def check_multi_source_coverage(self, article: dict[str, Any], all_articles: list[dict[str, Any]]) -> bool:
        return self.calculate_coverage_score(article, all_articles) >= 0.4

    def calculate_coverage_score(self, article: dict[str, Any], all_articles: list[dict[str, Any]]) -> float:
        target_title = _text(article.get("title")).lower()
        if not target_title:
            return 0.0
        domains: set[str] = set()
        for candidate in all_articles:
            title = _text(candidate.get("title")).lower()
            if SequenceMatcher(None, target_title, title).ratio() >= 0.45:
                domain = urlparse(_text(candidate.get("url"))).netloc.lower().removeprefix("www.")
                if domain:
                    domains.add(domain)
        return min(1.0, len(domains) / 5)


@dataclass(frozen=True)
class ReliabilityThresholds:
    source_weight: float = 0.30
    date_weight: float = 0.20
    sensationalism_weight: float = 0.15
    consistency_weight: float = 0.20
    coverage_weight: float = 0.15
    min_final_score: float = 0.65
    min_source_score: float = 0.8


class FakeNewsDetector:
    def __init__(self, thresholds: ReliabilityThresholds | None = None) -> None:
        self.thresholds = thresholds or ReliabilityThresholds()
        self.sources = SourceVerifier()
        self.dates = DateManipulationDetector()
        self.sensationalism = SensationalismDetector()
        self.cross_reference = CrossReferenceChecker()

    def analyze(self, article: dict[str, Any], all_articles: list[dict[str, Any]]) -> dict[str, Any]:
        title = _text(article.get("title"))
        content = _text(article.get("content") or article.get("description"))
        source = self.sources.get_source_score(_text(article.get("url")))
        date_mismatch = self.dates.check_date_context_mismatch(title, content, _text(article.get("published_at")))
        sensationalism = self.sensationalism.calculate_sensationalism_score(title)
        consistency = self.sensationalism.check_headline_body_consistency(title, content)
        coverage = self.cross_reference.calculate_coverage_score(article, all_articles)

        date_score = 1 - date_mismatch
        sensationalism_score = 1 - sensationalism
        final_score = (
            source * self.thresholds.source_weight
            + date_score * self.thresholds.date_weight
            + sensationalism_score * self.thresholds.sensationalism_weight
            + consistency * self.thresholds.consistency_weight
            + coverage * self.thresholds.coverage_weight
        )
        final_score = round(max(0.0, min(1.0, final_score)), 4)

        flags = self._flags(source, date_mismatch, sensationalism, consistency, coverage)
        is_reliable = final_score >= self.thresholds.min_final_score and source >= self.thresholds.min_source_score
        return {
            "is_reliable": is_reliable,
            "final_score": final_score,
            "breakdown": {
                "source": round(source, 4),
                "date": round(date_score, 4),
                "sensationalism": round(sensationalism_score, 4),
                "consistency": round(consistency, 4),
                "coverage": round(coverage, 4),
            },
            "flags": flags,
        }

    def analyze_batch(self, articles: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [self.analyze(article, articles) for article in articles]

    def _flags(self, source: float, date_mismatch: float, sensationalism: float, consistency: float, coverage: float) -> list[str]:
        flags: list[str] = []
        if source < self.thresholds.min_source_score:
            flags.append("untrusted_source")
        if date_mismatch > 0.3:
            flags.append("date_context_mismatch")
        if sensationalism > 0.5:
            flags.append("sensational_headline")
        if consistency < 0.6:
            flags.append("headline_body_inconsistency")
        if coverage < 0.4:
            flags.append("low_cross_source_coverage")
        return flags
