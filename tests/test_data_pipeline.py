from __future__ import annotations

from datetime import date, datetime, timezone
from types import SimpleNamespace

import pandas as pd
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from src.collector.news_collector import NewsCollector
from src.collector.providers.rss import RssNewsProvider
from src.dashboard.app import app
from src.dashboard.database import Base
from src.dashboard.models import NewsFiltered, NewsRaw, StockPrice
from src.dashboard.repository import persist_news_records, upsert_stock_prices
from src.dashboard.services.data_pipeline import PipelineSnapshot
from src.processor.event_score import EventScoreCalculator
from src.processor.market_metrics import calculate_market_metrics, safe_ratio
from src.processor.news_filter import NewsFilter
from src.signal.generator import SignalGenerator


def test_safe_ratio_returns_and_rolling_volatility_are_finite() -> None:
    frame = pd.DataFrame(
        {
            "trade_date": pd.date_range("2026-06-01", periods=8),
            "close": [100, 101, 99, 103, 104, 106, 105, 108],
            "volume": [0, 100, 120, 140, 160, 180, 200, 220],
        }
    )

    result = calculate_market_metrics(frame)

    assert safe_ratio(1, 0) == 0
    assert safe_ratio(float("nan"), 2) == 0
    assert result.iloc[-1]["return_1d"] == 108 / 105 - 1
    assert result["volatility_5d"].dropna().map(lambda value: value == value).all()


def test_stock_and_news_upserts_do_not_create_duplicates() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    session = Session(engine)
    stock = {
        "ticker": "NVDA",
        "trade_date": date(2026, 6, 26),
        "close": 100.0,
        "provider": "yfinance",
        "data_source": "real",
        "fetched_at": datetime.now(timezone.utc),
    }
    article = {
        "title": "AI semiconductor export policy update",
        "content": "Reuters AI semiconductor chip policy export " + ("detail " * 40),
        "source": "Reuters",
        "url": "https://example.com/news/1",
        "published_utc": "2026-06-26T09:00:00Z",
        "provider": "GDELT",
    }
    prepared = NewsFilter().prepare_records([article])

    upsert_stock_prices(session, [stock])
    stock["close"] = 101.0
    upsert_stock_prices(session, [stock])
    persist_news_records(session, prepared)
    persist_news_records(session, prepared)

    assert session.scalar(select(func.count()).select_from(StockPrice)) == 1
    assert session.scalar(select(StockPrice.close)) == 101.0
    assert session.scalar(select(func.count()).select_from(NewsRaw)) == 1
    assert session.scalar(select(func.count()).select_from(NewsFiltered)) == 1


def test_rss_normalization_and_missing_newsapi_key_are_graceful(monkeypatch) -> None:
    class Response:
        content = b"""<rss><channel><item>
        <title>AI chip policy</title>
        <description>Semiconductor export policy update</description>
        <link>https://example.com/rss/1</link>
        <pubDate>Fri, 26 Jun 2026 09:00:00 GMT</pubDate>
        </item></channel></rss>"""

        def raise_for_status(self) -> None:
            return None

    monkeypatch.setattr("src.collector.providers.rss.httpx.get", lambda *args, **kwargs: Response())
    result = RssNewsProvider("https://example.com/rss").collect(["chip"])

    assert result.status == "healthy"
    assert {
        "title",
        "content",
        "source",
        "url",
        "published_utc",
        "provider",
        "keyword",
        "raw_payload",
    }.issubset(result.articles[0])

    monkeypatch.setattr(
        "src.collector.news_collector.get_settings",
        lambda: SimpleNamespace(news_api_key=None),
    )
    assert NewsCollector().collect_from_newsapi() == []
    assert NewsCollector.provider_statuses()["NewsAPI"]["status"] == "disabled"


def test_duplicate_titles_are_flagged_before_filtering() -> None:
    base = {
        "title": "AI Chip Policy!",
        "content": "Reuters AI semiconductor chip policy export " + ("detail " * 40),
        "source": "Reuters",
        "published_utc": "2026-06-26T09:00:00Z",
        "provider": "GDELT",
    }
    records = NewsFilter().prepare_records(
        [
            {**base, "url": "https://example.com/1"},
            {**base, "title": "AI chip policy", "url": "https://example.com/2"},
        ]
    )

    assert records[0]["duplicate_flag"] is False
    assert records[1]["duplicate_flag"] is True
    assert records[1]["passed_filter"] is False


def test_signal_requires_market_confirmation_for_red() -> None:
    calculator = EventScoreCalculator()
    article = {"title": "AI semiconductor export control", "content": "Samsung NVIDIA AMD chip policy"}
    strong_market = {
        "return_1d": -0.04,
        "volume_ratio": 2.3,
        "volatility_5d": 0.07,
        "volatility_ratio": 1.5,
        "sentiment_score": -0.6,
    }

    assert {"NVDA", "AMD", "005930.KS", "000660.KS"}.issubset(calculator.affected_tickers(article))
    assert SignalGenerator().generate(0.9, strong_market) == "RED"
    assert SignalGenerator().generate(0.9, {"sentiment_score": -0.8}) == "GREEN"
    assert SignalGenerator().generate(0.4, {"return_1d": 0.01, "volume_ratio": 1.1}) == "GREEN"


def test_dashboard_pipeline_endpoints_expose_fallback_metadata(monkeypatch) -> None:
    article = {
        "title": "AI semiconductor export policy",
        "content": "AI chip policy creates risk for semiconductor supply.",
        "source": "Seed fixture",
        "url": "https://example.com/fallback",
        "published_at": "2026-06-26T09:00:00Z",
        "provider": "seed",
    }
    snapshot = PipelineSnapshot(
        articles=[article],
        market=[],
        data_source="seed_fallback",
        providers=["seed"],
        is_fallback=True,
        last_updated="2026-06-29T00:00:00+00:00",
        warnings=["Provider unavailable; seed fallback active"],
    )
    monkeypatch.setattr("src.dashboard.routes.api.load_pipeline_snapshot", lambda db, max_news=50: snapshot)
    client = TestClient(app)

    for path in ("/api/briefing", "/api/news-guard", "/api/industry-impact"):
        response = client.get(path)
        assert response.status_code == 200
        payload = response.json()
        assert payload["dataSource"] == "seed_fallback"
        assert payload["isFallback"] is True
        assert payload["providers"] == ["seed"]
        assert payload["warnings"]
        assert payload["lastUpdated"]
