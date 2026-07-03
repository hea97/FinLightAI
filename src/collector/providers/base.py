from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class NewsProviderResult:
    provider: str
    articles: list[dict[str, Any]] = field(default_factory=list)
    status: str = "healthy"
    message: str = ""
    fetched_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


def normalized_article(
    *,
    title: str,
    content: str,
    source: str,
    url: str,
    published_utc: str,
    provider: str,
    keyword: str = "",
    raw_payload: dict[str, Any] | None = None,
    **extra: Any,
) -> dict[str, Any]:
    return {
        "title": title.strip() or "Untitled article",
        "content": content.strip() or title.strip(),
        "summary": content.strip() or title.strip(),
        "source": source.strip() or provider,
        "url": url.strip(),
        "published_utc": published_utc,
        "published_at": published_utc,
        "provider": provider,
        "keyword": keyword,
        "raw_payload": raw_payload,
        **extra,
    }
