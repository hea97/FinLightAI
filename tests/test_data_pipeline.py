from __future__ import annotations

from datetime import date, datetime, timezone
from time import perf_counter
from types import SimpleNamespace

import pandas as pd
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from src.collector.news_collector import NewsCollector
from src.collector.providers.google_news_rss import GoogleNewsRssProvider
from src.collector.providers.rss import RssNewsProvider
from src.dashboard.app import app
from src.dashboard.database import Base
from src.dashboard.models import NewsFiltered, NewsRaw, Signal, StockPrice
from src.dashboard.repository import (
    persist_news_records,
    reconcile_duplicate_news_titles,
    upsert_stock_prices,
)
from src.dashboard.services.data_pipeline import (
    PipelineSnapshot,
    _eligible_signal_articles,
    _persist_generated_signals,
)
from src.dashboard.routes.api import _industry_articles
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


def test_rss_ai_keyword_uses_word_boundaries_and_rejects_unrelated_news(monkeypatch) -> None:
    class Response:
        content = b"""<rss><channel>
        <item><title>Plane carrying skydivers crashes</title><description>Thailand media report</description>
        <link>https://example.com/unrelated</link></item>
        <item><title>AI chip export control update</title><description>NVIDIA semiconductor policy</description>
        <link>https://example.com/relevant</link></item>
        </channel></rss>"""

        def raise_for_status(self) -> None:
            return None

    monkeypatch.setattr("src.collector.providers.rss.httpx.get", lambda *args, **kwargs: Response())
    result = RssNewsProvider("https://example.com/rss").collect(["AI"])

    assert [article["url"] for article in result.articles] == ["https://example.com/relevant"]


def test_google_news_rss_normalizes_keyless_finance_news(monkeypatch) -> None:
    class Response:
        content = b"""<rss><channel><item>
        <title>NVIDIA AI chip demand lifts semiconductor outlook</title>
        <description><![CDATA[<p>Artificial intelligence chip demand supports NVIDIA suppliers.</p>]]></description>
        <link>https://news.google.com/rss/articles/real-news-id</link>
        <guid>real-news-id</guid>
        <pubDate>Fri, 26 Jun 2026 09:00:00 GMT</pubDate>
        <source>Reuters</source>
        </item></channel></rss>"""

        def raise_for_status(self) -> None:
            return None

    monkeypatch.setattr(
        "src.collector.providers.google_news_rss.httpx.get",
        lambda *args, **kwargs: Response(),
    )

    result = GoogleNewsRssProvider("https://news.google.com/rss/search").collect(
        ["AI", "semiconductor"],
        days=7,
    )

    assert result.status == "healthy"
    assert result.provider == "Google News RSS"
    assert result.articles[0]["source"] == "Reuters"
    assert result.articles[0]["matched_keywords"] == ["AI", "artificial intelligence", "semiconductor", "chip", "NVIDIA"]
    assert result.articles[0]["relevance_score"] == 5
    assert "<p>" not in result.articles[0]["content"]
    assert {
        "title",
        "content",
        "source",
        "url",
        "published_utc",
        "provider",
        "raw_payload",
        "matched_keywords",
        "relevance_score",
    }.issubset(result.articles[0])


def test_finance_rss_filter_accepts_relevant_short_summary_and_traces_rejections() -> None:
    relevant = {
        "title": "NVIDIA AI chip demand lifts semiconductor outlook",
        "content": "Reuters says export control changes could affect NVIDIA chip demand and market supply.",
        "source": "Reuters",
        "url": "https://news.google.com/rss/articles/relevant",
        "published_utc": "2026-06-26T09:00:00Z",
        "provider": "Google News RSS",
    }
    unrelated = {
        "title": "Weekend travel outlook",
        "content": "A short general travel report.",
        "source": "Unknown blog",
        "url": "https://news.google.com/rss/articles/unrelated",
        "published_utc": "2026-06-26T09:00:00Z",
        "provider": "Google News RSS",
    }

    relevant_record, unrelated_record = NewsFilter().prepare_records([relevant, unrelated])

    assert relevant_record["passed_filter"] is True
    assert relevant_record["filter_reasons"] == []
    assert unrelated_record["passed_filter"] is False
    assert {
        "source_score_below_threshold",
        "keyword_score_below_threshold",
        "no_relevant_finance_terms",
        "content_too_short",
    }.issubset(unrelated_record["filter_reasons"])


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


def test_duplicate_titles_are_suppressed_across_refreshes_while_raw_rows_remain() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    session = Session(engine)
    base = {
        "content": "Reuters AI semiconductor chip policy export " + ("detail " * 40),
        "source": "Reuters",
        "published_utc": "2026-06-26T09:00:00Z",
        "provider": "Google News RSS",
    }
    first = NewsFilter().prepare_records(
        [{**base, "title": "NVIDIA AI Chip Policy!", "url": "https://news.example/first"}]
    )
    second = NewsFilter().prepare_records(
        [{**base, "title": "nvidia ai chip policy", "url": "https://news.example/second"}]
    )

    persist_news_records(session, first)
    persist_news_records(session, second)
    duplicates = reconcile_duplicate_news_titles(session)

    filtered_rows = list(session.scalars(select(NewsFiltered).order_by(NewsFiltered.id)))
    raw_rows = list(session.scalars(select(NewsRaw).order_by(NewsRaw.id)))
    assert len(raw_rows) == 2
    assert duplicates == 1
    assert filtered_rows[0].duplicate_flag is False
    assert filtered_rows[1].duplicate_flag is True
    assert filtered_rows[1].passed_filter is False
    assert "duplicate_title_across_refreshes" in raw_rows[1].raw_payload["_filter"]["reasons"]


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


def test_only_verified_real_news_is_eligible_for_signal_generation() -> None:
    base = {
        "title": "NVIDIA AI chip export update",
        "content": "Semiconductor market update",
        "url": "https://news.google.com/rss/articles/verified",
        "source": "Reuters",
        "provider": "Google News RSS",
        "duplicate_flag": False,
        "relevance_score": 3,
    }

    assert _eligible_signal_articles([{**base, "passed_filter": True}]) == [
        {**base, "passed_filter": True}
    ]
    assert _eligible_signal_articles([{**base, "passed_filter": False}]) == []
    assert _eligible_signal_articles([{**base, "passed_filter": True, "provider": "seed"}]) == []


def test_generated_signal_is_persisted_without_future_market_leakage() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    session = Session(engine)
    article = {
        "title": "NVIDIA AI chip export policy",
        "content": "Semiconductor export control risk affects NVIDIA.",
        "url": "https://example.com/event",
        "published_utc": "2026-06-25T09:00:00+00:00",
        "provider": "GDELT",
        "source_score": 0.9,
        "duplicate_flag": False,
    }
    market = [
        {
            "ticker": "NVDA",
            "trade_date": "2026-06-26",
            "return_1d": -0.04,
            "volume_ratio": 2.3,
            "volatility_5d": 0.07,
            "volatility_ratio": 1.5,
        }
    ]

    _persist_generated_signals(session, [article], market)
    _persist_generated_signals(session, [article], market)

    assert session.scalar(select(func.count()).select_from(Signal)) == 1
    stored = session.scalar(select(Signal))
    assert stored is not None
    assert stored.trade_date >= date(2026, 6, 25)
    assert stored.evidence["provider"] == "GDELT"


def test_signal_api_exposes_verified_real_news_evidence(isolated_dashboard_database) -> None:
    article = {
        "title": "NVIDIA AI chip export policy",
        "content": "Semiconductor export control affects NVIDIA market supply.",
        "url": "https://news.google.com/rss/articles/verified-signal",
        "published_utc": "2026-06-25T09:00:00+00:00",
        "provider": "Google News RSS",
        "source": "Reuters",
        "source_score": 0.9,
        "keyword_score": 4,
        "duplicate_flag": False,
    }
    market = [
        {
            "ticker": "NVDA",
            "trade_date": "2026-06-26",
            "return_1d": -0.01,
            "volume_ratio": 1.2,
            "volatility_5d": 0.02,
            "volatility_ratio": 1.0,
        }
    ]
    with isolated_dashboard_database() as db:
        _persist_generated_signals(db, [article], market)

    payload = TestClient(app).get("/api/signals").json()

    assert len(payload) == 1
    assert payload[0]["is_verified"] is True
    assert payload[0]["data_source"] == "real"
    assert payload[0]["evidence"]["url"] == article["url"]
    assert payload[0]["evidence"]["source"] == "Reuters"
    assert payload[0]["evidence"]["provider"] == "Google News RSS"


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


def test_news_guard_uses_only_relevant_stored_filtered_news(isolated_dashboard_database) -> None:
    trusted = {
        "title": "NVIDIA AI semiconductor export control update",
        "content": "Reuters reported an AI semiconductor chip export control update. " + ("verified detail " * 30),
        "source": "Reuters",
        "url": "https://reuters.example/verified-ai-news",
        "published_utc": "2026-06-28T09:00:00+00:00",
        "provider": "GDELT",
    }
    unrelated = {
        "title": "Plane carrying skydivers crashes in France",
        "content": "BBC international report about an aviation accident. " + ("unrelated detail " * 30),
        "source": "BBC RSS",
        "url": "https://bbc.example/unrelated",
        "published_utc": "2026-06-28T08:00:00+00:00",
        "provider": "BBC RSS",
    }
    with isolated_dashboard_database() as db:
        persist_news_records(db, NewsFilter().prepare_records([trusted, unrelated]))

    payload = TestClient(app).get("/api/news-guard").json()

    assert payload["stats"]["collectedNewsCount"] == 1
    assert payload["articles"][0]["title"] == trusted["title"]
    assert payload["articles"][0]["qualityStatus"] == "verified"
    assert payload["articles"][0]["provider"] == "GDELT"
    assert payload["isFallback"] is False


def test_provider_status_warnings_and_metadata_are_consistent(monkeypatch) -> None:
    snapshot = PipelineSnapshot(
        articles=[],
        market=[],
        data_source="mixed",
        providers=["BBC RSS"],
        is_fallback=False,
        last_updated="2026-06-29T00:00:00+00:00",
        warnings=["GDELT timed out; using latest stored news"],
        provider_status={
            "gdelt": "timeout",
            "bbcrss": "connected",
            "yfinance": "connected",
            "gemini": "rate_limited",
        },
    )
    monkeypatch.setattr("src.dashboard.routes.api.load_pipeline_snapshot", lambda db, max_news=50: snapshot)

    payload = TestClient(app).get("/api/briefing").json()

    assert payload["providerStatus"]["gdelt"] == "timeout"
    assert payload["providerStatus"]["gemini"] == "rate_limited"
    assert any("Gemini rate_limited" in warning for warning in payload["warnings"])
    assert {"dataSource", "providers", "isFallback", "lastUpdated", "warnings"}.issubset(payload)


def test_dashboard_requests_do_not_wait_for_external_providers() -> None:
    client = TestClient(app)
    started = perf_counter()

    for path in ("/api/briefing", "/api/news-guard", "/api/industry-impact"):
        assert client.get(path).status_code == 200

    assert perf_counter() - started < 2.0


def test_industry_evidence_excludes_unrelated_articles() -> None:
    unrelated = {"title": "Plane carrying skydivers", "content": "France aviation report"}
    relevant = {"title": "NVIDIA AI chip export control", "content": "Semiconductor policy update"}

    assert _industry_articles("it", [unrelated, relevant]) == [relevant]
    assert _industry_articles("semiconductor", [unrelated, relevant]) == [relevant]


def test_empty_market_and_signal_endpoints_are_explicit() -> None:
    client = TestClient(app)

    market = client.get("/api/market").json()
    signals = client.get("/api/signals").json()

    assert market["dataSource"] == "not_connected"
    assert market["warnings"]
    assert signals == []
