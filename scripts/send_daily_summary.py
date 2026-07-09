from __future__ import annotations

import sys
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.dashboard.database import SessionLocal  # noqa: E402
from src.dashboard.repository import latest_signals  # noqa: E402
from src.notifier.notification_service import NotificationService  # noqa: E402

KST = ZoneInfo("Asia/Seoul")


def kst_today() -> date:
    return datetime.now(KST).date()


def build_daily_summary(signals, today: date) -> tuple[str, str, str]:
    counts = {signal: 0 for signal in ("RED", "YELLOW", "GREEN")}
    for row in signals:
        if row.signal in counts:
            counts[row.signal] += 1

    highlights = "\n".join(
        f"- {row.ticker}: {row.signal} (event score {row.event_score:.1f}, trade date {row.trade_date.isoformat()})"
        for row in signals[:5]
    ) or "- No market signals were generated."
    subject = f"[FinLightAI] {today.isoformat()} daily market summary"
    body = (
        f"KST date: {today.isoformat()}\n"
        f"Signal counts: RED {counts['RED']} / YELLOW {counts['YELLOW']} / GREEN {counts['GREEN']}\n\n"
        "Latest signal highlights:\n"
        f"{highlights}\n\n"
        "This summary is market-state information, not investment advice."
    )
    return subject, body, f"daily-summary:{today.isoformat()}"


def send_daily_summary(db, today: date | None = None):
    summary_date = today or kst_today()
    signals = latest_signals(db, limit=20)
    subject, body, dedupe_key = build_daily_summary(signals, summary_date)
    return NotificationService(db).dispatch(
        notification_type="daily_summary",
        subject=subject,
        body=body,
        dedupe_key=dedupe_key,
        channels=("email",),
    )


def main() -> None:
    with SessionLocal() as db:
        print(send_daily_summary(db))


if __name__ == "__main__":
    main()
