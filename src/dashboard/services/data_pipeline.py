from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from src.collector.news_collector import NewsCollector
from src.collector.stock_collector import StockCollector
from src.dashboard.repository import (
    latest_stock_prices,
    persist_news_records,
    update_provider_statuses,
    upsert_stock_prices,
)
from src.processor.news_filter import NewsFilter


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
