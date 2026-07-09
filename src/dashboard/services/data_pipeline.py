from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.collector.news_collector import NewsCollector
from src.collector.stock_collector import StockCollector
from src.dashboard.repository import (
    clear_signals,
    finish_refresh_run,
    latest_provider_statuses,
    latest_stored_news,
    latest_stock_prices,
    persist_news_records,
    reconcile_duplicate_news_titles,
    remove_weekend_stock_prices,
    start_refresh_run,
    update_provider_statuses,
    upsert_stock_prices,
    upsert_signal,
)
from src.dashboard.models import Signal
from src.processor.event_score import EventScoreCalculator
from src.processor.news_filter import NewsFilter
from src.processor.news_relevance import relevance_score
from src.processor.sentiment import SentimentAnalyzer
from src.processor.trading_calendar import event_date_for_exchange, next_trading_day
from src.signal.generator import SignalGenerator
from src.notifier.notification_service import NotificationService


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
    stored_prepared = [
        {
            **record,
            "relevance_score": relevance_score(
                f"{record.get('title', '')} {record.get('content', '')}"
            ),
        }
        for record in stored
    ]
    verified_stored = [
        record
        for record in stored_prepared
        if (
            record["passed_filter"]
            and not record["duplicate_flag"]
            and record.get("provider") != "seed"
        )
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


def refresh_pipeline_data(
    db: Session,
    max_news: int = 100,
    *,
    trigger: str = "manual",
) -> dict[str, Any]:
    """Explicitly refresh external data; dashboard GET requests never call this."""
    run = start_refresh_run(db, trigger=trigger)
    try:
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
        update_provider_statuses(db, provider_states, run_id=run.id)
        signal_market = [
            {
                **row,
                "trade_date": (
                    row["trade_date"].isoformat()
                    if isinstance(row.get("trade_date"), date)
                    else str(row.get("trade_date"))
                ),
            }
            for row in market_rows
        ]
        signal_articles = _eligible_signal_articles(prepared)
        clear_signals(db)
        signal_count = _persist_generated_signals(db, signal_articles, signal_market)
        notification_counts = _dispatch_signal_notifications(db)
        counts = {
            "news_rows": len(prepared),
            "verified_news_rows": sum(1 for row in prepared if row["passed_filter"]),
            "market_rows": len(market_rows),
            "signal_rows": signal_count,
            "duplicate_news_rows": duplicate_news_rows,
            "notification_sent": notification_counts["sent"],
            "notification_failed": notification_counts["failed"],
            "notification_duplicate": notification_counts["duplicate"],
        }
        unhealthy = [
            provider
            for provider, state in provider_states.items()
            if str(state.get("status", "")).lower() not in {"healthy", "connected", "cached"}
        ]
        run_status = "partial" if unhealthy or not prepared or not market_rows else "succeeded"
        finish_refresh_run(db, run.id, status=run_status, counts=counts)
        return {
            **counts,
            "run_id": run.id,
            "status": run_status,
            "provider_status": provider_states,
        }
    except Exception as exc:
        db.rollback()
        finish_refresh_run(db, run.id, status="failed", error_message=str(exc))
        raise


def _dispatch_signal_notifications(db: Session) -> dict[str, int]:
    totals = {"sent": 0, "failed": 0, "duplicate": 0, "skipped": 0}
    service = NotificationService(db)
    signals = db.scalars(
        select(Signal)
        .where(Signal.signal.in_(("RED", "YELLOW")))
        .order_by(Signal.created_at.desc())
    ).all()
    for signal in signals:
        result = service.dispatch(
            notification_type="signal",
            subject=f"[FinLightAI] {signal.ticker} {signal.signal} 시장 상태 신호",
            body=(
                f"종목: {signal.ticker}\n"
                f"시장 상태: {signal.signal}\n"
                f"이벤트 점수: {signal.event_score:.1f}\n"
                "본 알림은 투자 추천이 아닌 시장 상태 정보입니다."
            ),
            dedupe_key=f"signal:{signal.event_key}:{signal.ticker}:{signal.trade_date.isoformat()}",
            signal=signal.signal,
            channels=("email",),
        )
        for key in totals:
            totals[key] += getattr(result, key)
    return totals


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
    market_by_ticker: dict[str, list[dict[str, Any]]] = {}
    for row in market_rows:
        market_by_ticker.setdefault(str(row["ticker"]), []).append(row)
    for rows in market_by_ticker.values():
        rows.sort(key=lambda row: str(row["trade_date"]))
    persisted = 0
    for article in articles:
        if article.get("duplicate_flag"):
            continue
        published_at = _published_datetime(article)
        text = f"{article.get('title', '')} {article.get('content', '')}"
        sentiment = sentiment_analyzer.analyze(text)
        for ticker in calculator.affected_tickers(article):
            candidates = market_by_ticker.get(ticker, [])
            if not candidates:
                continue
            event_date = event_date_for_exchange(published_at, ticker) if published_at else None
            expected_trade_date = next_trading_day(event_date, ticker) if event_date else None
            market = (
                next(
                    (
                        row
                        for row in candidates
                        if date.fromisoformat(str(row["trade_date"])) == expected_trade_date
                    ),
                    None,
                )
                if expected_trade_date
                else candidates[-1]
            )
            if market is None:
                continue
            trade_date = date.fromisoformat(str(market["trade_date"]))
            market_with_sentiment = {**market, "sentiment_score": float(sentiment["score"])}
            event_score = calculator.calculate(
                float(article.get("reliability_score") or article.get("source_score") or 0),
                float(sentiment["score"]),
                market_with_sentiment,
            )
            event_key = hashlib.sha256(
                f"{article.get('url', '')}|{article.get('title', '')}".lower().encode("utf-8")
            ).hexdigest()
            evidence = calculator.evidence(article, market_with_sentiment)
            evidence.update(
                {
                    "event_date": event_date.isoformat() if event_date else None,
                    "expected_trade_date": expected_trade_date.isoformat() if expected_trade_date else None,
                    "market_match": "exact" if expected_trade_date else "latest_without_event_date",
                }
            )
            upsert_signal(
                db,
                {
                    "event_key": event_key,
                    "ticker": ticker,
                    "trade_date": trade_date,
                    "event_score": event_score,
                    "market_reaction_score": calculator.market_reaction_score(market_with_sentiment),
                    "signal": generator.generate(event_score, market_with_sentiment),
                    "evidence": evidence,
                    "data_source": "seed_fallback" if article.get("provider") == "seed" else "real",
                },
            )
            persisted += 1
    return persisted


def _published_datetime(article: dict[str, Any]) -> datetime | None:
    raw = str(article.get("published_utc") or article.get("published_at") or "")
    if not raw:
        return None
    try:
        if raw.endswith("Z"):
            raw = f"{raw[:-1]}+00:00"
        return datetime.fromisoformat(raw)
    except ValueError:
        try:
            return datetime.strptime(raw[:8], "%Y%m%d").replace(tzinfo=timezone.utc)
        except ValueError:
            return None
