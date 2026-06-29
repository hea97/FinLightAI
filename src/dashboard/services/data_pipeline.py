from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from src.collector.news_collector import NewsCollector
from src.collector.stock_collector import StockCollector
from src.dashboard.repository import (
    latest_stock_prices,
    persist_news_records,
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
    news_result = collector.collect_all(max_records=max_news)
    articles = collector.deduplicate(news_result.articles)
    prepared = NewsFilter().prepare_records(articles)
    try:
        persist_news_records(db, prepared)
        update_provider_statuses(db, collector.provider_statuses())
    except Exception as exc:
        db.rollback()
        warnings.append(f"News persistence unavailable: {type(exc).__name__}")

    market_rows = latest_stock_prices(db, list(StockCollector.DEFAULT_TICKERS))
    if not market_rows:
        try:
            collected = StockCollector().collect_daily(period="1mo")
            if collected:
                upsert_stock_prices(db, collected)
                market_rows = latest_stock_prices(db, list(StockCollector.DEFAULT_TICKERS))
            else:
                warnings.append("yfinance returned no market rows")
        except Exception as exc:
            db.rollback()
            warnings.append(f"Market collection unavailable: {type(exc).__name__}")

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
    try:
        _persist_generated_signals(db, prepared, market)
    except Exception as exc:
        db.rollback()
        warnings.append(f"Signal persistence unavailable: {type(exc).__name__}")
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
    if news_result.message and news_result.status != "real":
        warnings.append(news_result.message)
    if has_seed:
        warnings.append("Seed news is explicitly labeled and used only as fallback")
    now = datetime.now(timezone.utc).isoformat()
    return PipelineSnapshot(
        articles=articles,
        market=market,
        data_source=data_source,
        providers=providers,
        is_fallback=has_seed,
        last_updated=now,
        warnings=list(dict.fromkeys(warnings)),
    )


def _persist_generated_signals(
    db: Session,
    articles: list[dict[str, Any]],
    market_rows: list[dict[str, Any]],
) -> None:
    calculator = EventScoreCalculator()
    generator = SignalGenerator()
    sentiment_analyzer = SentimentAnalyzer()
    market_by_ticker = {row["ticker"]: row for row in market_rows}
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
