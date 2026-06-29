from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from src.collector.news_collector import NewsCollector
from src.collector.stock_collector import StockCollector
from src.dashboard.repository import (
    latest_provider_statuses,
    latest_stored_news,
    latest_stock_prices,
    persist_news_records,
    prune_signals,
    reconcile_duplicate_news_titles,
    remove_weekend_stock_prices,
    update_provider_statuses,
    upsert_stock_prices,
    upsert_signal,
)
from src.processor.event_score import EventScoreCalculator
from src.processor.news_filter import NewsFilter
from src.processor.sentiment import SentimentAnalyzer
from src.signal.generator import SignalGenerator


@dataclass
class PipelineSnapshot:
    articles: list[dict[str, Any]]
    market: list[dict[str, Any]]
    data_source: str
    providers: list[str]
    is_fallback: bool
    last_updated: str
    warnings: list[str]
    provider_status: dict[str, str] = field(default_factory=dict)

    def metadata(self) -> dict[str, Any]:
        return {
            "dataSource": self.data_source,
            "providers": self.providers,
            "isFallback": self.is_fallback,
            "lastUpdated": self.last_updated,
            "warnings": self.warnings,
        }


def load_pipeline_snapshot(db: Session, max_news: int = 50) -> PipelineSnapshot:
    warnings: list[str] = []
    collector = NewsCollector()
    news_filter = NewsFilter()
    stored = latest_stored_news(db, max(max_news * 4, 100))
    stored_prepared = news_filter.prepare_records(stored)
    verified_stored = [
        record
        for record in stored_prepared
        if record["passed_filter"] and record.get("provider") != "seed"
    ]
    reviewable_stored = [
        record
        for record in stored_prepared
        if (
            not record["duplicate_flag"]
            and record["relevance_score"] >= 1
            and record.get("provider") != "seed"
        )
    ]
    provider_states = latest_provider_statuses(db)
    if verified_stored:
        prepared = verified_stored[:max_news]
        for record in prepared:
            record["quality_status"] = "verified"
        news_origin = "stored_verified"
    elif reviewable_stored:
        prepared = reviewable_stored[:max_news]
        for record in prepared:
            record["quality_status"] = "low_confidence"
        news_origin = "stored_reviewable"
        warnings.append("No verified stored news is available; showing relevant stored news as low confidence")
    else:
        stored_seed = [record for record in stored_prepared if record.get("provider") == "seed"]
        prepared = (stored_seed or news_filter.prepare_records(collector.fallback_articles()))[:max_news]
        for record in prepared:
            record["quality_status"] = "seed_fallback"
        news_origin = "stored_seed" if stored_seed else "local_seed"
        warnings.append("No relevant stored news is available; run the pipeline refresh command")
    articles = prepared

    market_rows = latest_stock_prices(db, list(StockCollector.DEFAULT_TICKERS))
    if not market_rows:
        warnings.append("No stored market rows are available; run the pipeline refresh command")

    market = [
        {
            "ticker": row.ticker,
            "trade_date": row.trade_date.isoformat(),
            "close": row.close,
            "return_1d": row.return_1d,
            "return_3d": row.return_3d,
            "return_5d": row.return_5d,
            "volume_ratio": row.volume_ratio,
            "volatility_5d": row.volatility_5d,
            "volatility_ratio": row.volatility_ratio,
            "provider": row.provider,
            "data_source": row.data_source,
        }
        for row in market_rows
    ]
    providers = sorted({str(article.get("provider") or "unknown") for article in articles})
    if market:
        providers.append("yfinance")
    providers = list(dict.fromkeys(providers))
    has_seed = any(article.get("provider") == "seed" for article in articles)
    has_real_news = any(article.get("provider") != "seed" for article in articles)
    if has_seed and not has_real_news:
        data_source = "seed_fallback"
    elif has_seed or not market:
        data_source = "mixed"
    else:
        data_source = "real"
    if has_seed:
        warnings.append("Seed news is explicitly labeled and used only as fallback")
    stored_updates = [str(article.get("fetched_at") or article.get("published_utc") or "") for article in articles]
    last_updated = max((value for value in stored_updates if value), default=datetime.now(timezone.utc).isoformat())
    if news_origin.startswith("stored") and provider_states:
        warnings.extend(
            (
                f"{provider} {_normalize_provider_status(state.get('status'), state.get('message'))}; "
                "using latest stored news"
            )
            for provider, state in provider_states.items()
            if state.get("status") in {"failed", "timeout", "error"}
        )
    provider_status = {
        _provider_key(provider): _normalize_provider_status(state.get("status"), state.get("message"))
        for provider, state in provider_states.items()
    }
    for provider in providers:
        provider_status.setdefault(_provider_key(provider), "connected")
    provider_status["yfinance"] = "connected" if market else "error"
    if has_seed:
        provider_status["seed"] = "fallback"
    return PipelineSnapshot(
        articles=articles,
        market=market,
        data_source=data_source,
        providers=providers,
        is_fallback=has_seed,
        last_updated=last_updated,
        warnings=list(dict.fromkeys(warnings)),
        provider_status=provider_status,
    )


def refresh_pipeline_data(db: Session, max_news: int = 100) -> dict[str, Any]:
    """Explicitly refresh external data; dashboard GET requests never call this."""
    collector = NewsCollector()
    news_result = collector.collect_all(max_records=max_news)
    collected = collector.deduplicate(news_result.articles)
    prepared = NewsFilter().prepare_records(collected)
    persist_news_records(db, prepared)
    duplicate_news_rows = reconcile_duplicate_news_titles(db)
    provider_states = collector.provider_statuses()

    market_rows = StockCollector().collect_daily(period="1mo")
    if market_rows:
        remove_weekend_stock_prices(db, StockCollector.DEFAULT_TICKERS)
        upsert_stock_prices(db, market_rows)
        provider_states["yfinance"] = {
            "status": "healthy",
            "message": f"Collected {len(market_rows)} daily market rows",
        }
    else:
        provider_states["yfinance"] = {
            "status": "failed",
            "message": "yfinance returned no market rows",
        }
    update_provider_statuses(db, provider_states)
    latest_market = latest_stock_prices(db, list(StockCollector.DEFAULT_TICKERS))
    signal_market = [
        {
            "ticker": row.ticker,
            "trade_date": row.trade_date.isoformat(),
            "return_1d": row.return_1d,
            "return_3d": row.return_3d,
            "return_5d": row.return_5d,
            "volume_ratio": row.volume_ratio,
            "volatility_5d": row.volatility_5d,
            "volatility_ratio": row.volatility_ratio,
        }
        for row in latest_market
    ]
    signal_articles = _eligible_signal_articles(prepared)
    valid_event_keys = {
        hashlib.sha256(
            f"{article.get('url', '')}|{article.get('title', '')}".lower().encode("utf-8")
        ).hexdigest()
        for article in signal_articles
    }
    prune_signals(db, valid_event_keys)
    signal_count = _persist_generated_signals(db, signal_articles, signal_market)
    return {
        "news_rows": len(prepared),
        "verified_news_rows": sum(1 for row in prepared if row["passed_filter"]),
        "market_rows": len(market_rows),
        "signal_rows": signal_count,
        "duplicate_news_rows": duplicate_news_rows,
        "provider_status": provider_states,
    }


def _provider_key(provider: str) -> str:
    return provider.lower().replace(" ", "").replace("_", "")


def _eligible_signal_articles(articles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        article
        for article in articles
        if (
            article.get("provider") != "seed"
            and article.get("passed_filter") is True
            and not article.get("duplicate_flag")
            and article.get("relevance_score", 0) >= 2
            and article.get("url")
            and article.get("source")
        )
    ]


def _normalize_provider_status(status: str | None, message: str | None = None) -> str:
    normalized = (status or "").lower()
    lowered_message = (message or "").lower()
    if "timeout" in lowered_message or normalized == "timeout":
        return "timeout"
    if normalized in {"healthy", "connected", "cached"}:
        return "connected"
    if normalized == "disabled":
        return "disabled"
    if normalized in {"partial", "fallback"}:
        return "fallback"
    if normalized == "rate_limited":
        return "rate_limited"
    return "error"


def _persist_generated_signals(
    db: Session,
    articles: list[dict[str, Any]],
    market_rows: list[dict[str, Any]],
) -> int:
    calculator = EventScoreCalculator()
    generator = SignalGenerator()
    sentiment_analyzer = SentimentAnalyzer()
    market_by_ticker = {row["ticker"]: row for row in market_rows}
    persisted = 0
    for article in articles:
        if article.get("duplicate_flag"):
            continue
        published_date = _published_date(article)
        text = f"{article.get('title', '')} {article.get('content', '')}"
        sentiment = sentiment_analyzer.analyze(text)
        for ticker in calculator.affected_tickers(article):
            market = market_by_ticker.get(ticker)
            if not market:
                continue
            trade_date = date.fromisoformat(market["trade_date"])
            if published_date and trade_date < published_date:
                continue
            market_with_sentiment = {**market, "sentiment_score": float(sentiment["score"])}
            event_score = calculator.calculate(
                float(article.get("reliability_score") or article.get("source_score") or 0),
                float(sentiment["score"]),
                market_with_sentiment,
            )
            event_key = hashlib.sha256(
                f"{article.get('url', '')}|{article.get('title', '')}".lower().encode("utf-8")
            ).hexdigest()
            upsert_signal(
                db,
                {
                    "event_key": event_key,
                    "ticker": ticker,
                    "trade_date": trade_date,
                    "event_score": event_score,
                    "market_reaction_score": calculator.market_reaction_score(market_with_sentiment),
                    "signal": generator.generate(event_score, market_with_sentiment),
                    "evidence": calculator.evidence(article, market_with_sentiment),
                    "data_source": "seed_fallback" if article.get("provider") == "seed" else "real",
                },
            )
            persisted += 1
    return persisted


def _published_date(article: dict[str, Any]) -> date | None:
    raw = str(article.get("published_utc") or article.get("published_at") or "")
    if not raw:
        return None
    try:
        if raw.endswith("Z"):
            raw = f"{raw[:-1]}+00:00"
        return datetime.fromisoformat(raw).date()
    except ValueError:
        try:
            return datetime.strptime(raw[:8], "%Y%m%d").date()
        except ValueError:
            return None
