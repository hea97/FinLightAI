from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

from sqlalchemy import delete, select

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.dashboard.database import SessionLocal  # noqa: E402
from src.dashboard.models import NewsFiltered, NewsRaw, Signal  # noqa: E402


KNOWN_FIXTURE_URLS = {
    "https://example.com/ai-chip-policy",
    "https://example.com/fallback",
    "https://example.com/event",
    "https://example.com/news/1",
    "https://example.com/1",
    "https://example.com/2",
}


def event_key(url: str, title: str) -> str:
    return hashlib.sha256(f"{url}|{title}".lower().encode("utf-8")).hexdigest()


def cleanup_fixture_data(apply_changes: bool, fixture_urls: set[str]) -> dict[str, int]:
    with SessionLocal() as db:
        fixture_news = list(db.scalars(select(NewsRaw).where(NewsRaw.url.in_(fixture_urls))))
        raw_ids = [row.id for row in fixture_news]
        event_keys = {event_key(row.url, row.title) for row in fixture_news}
        signal_ids = list(db.scalars(select(Signal.id).where(Signal.event_key.in_(event_keys)))) if event_keys else []
        filtered_ids = (
            list(db.scalars(select(NewsFiltered.id).where(NewsFiltered.raw_id.in_(raw_ids))))
            if raw_ids
            else []
        )
        result = {
            "news_raw": len(raw_ids),
            "news_filtered": len(filtered_ids),
            "signals": len(signal_ids),
        }
        if not apply_changes:
            return result

        if signal_ids:
            db.execute(delete(Signal).where(Signal.id.in_(signal_ids)))
        if filtered_ids:
            db.execute(delete(NewsFiltered).where(NewsFiltered.id.in_(filtered_ids)))
        if raw_ids:
            db.execute(delete(NewsRaw).where(NewsRaw.id.in_(raw_ids)))
        db.commit()
        return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Remove only explicitly known FinLightAI test-fixture news and derived signals.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Commit deletions. Without this flag the command is a dry run.",
    )
    parser.add_argument(
        "--fixture-url",
        action="append",
        default=[],
        help="Add an exact fixture URL to the built-in allowlist.",
    )
    args = parser.parse_args()
    fixture_urls = KNOWN_FIXTURE_URLS | set(args.fixture_url)
    result = cleanup_fixture_data(args.apply, fixture_urls)
    mode = "deleted" if args.apply else "would_delete"
    print({mode: result})


if __name__ == "__main__":
    main()
