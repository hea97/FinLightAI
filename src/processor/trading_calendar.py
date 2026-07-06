from __future__ import annotations

from datetime import date, datetime
from functools import lru_cache
from zoneinfo import ZoneInfo

import exchange_calendars as xcals
import pandas as pd


def exchange_for_ticker(ticker: str) -> str:
    """Map the supported ticker notation to an exchange calendar."""
    normalized = ticker.upper()
    if normalized.endswith((".KS", ".KQ")):
        return "XKRX"
    return "XNYS"


@lru_cache(maxsize=4)
def _calendar(exchange: str):
    return xcals.get_calendar(exchange)


def next_trading_day(event_date: date, ticker: str) -> date:
    """Return the first exchange session strictly after an event's calendar date."""
    calendar = _calendar(exchange_for_ticker(ticker))
    timestamp = pd.Timestamp(event_date)
    if calendar.is_session(timestamp):
        session = calendar.next_session(timestamp)
    else:
        session = calendar.date_to_session(timestamp, direction="next")
    return session.date()


def event_date_for_exchange(published_at: datetime, ticker: str) -> date:
    timezone_name = "Asia/Seoul" if exchange_for_ticker(ticker) == "XKRX" else "America/New_York"
    if published_at.tzinfo is None:
        published_at = published_at.replace(tzinfo=ZoneInfo("UTC"))
    return published_at.astimezone(ZoneInfo(timezone_name)).date()
