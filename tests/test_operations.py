from __future__ import annotations

from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from src.collector.news_collector import NewsCollector
from src.dashboard.app import app
from src.dashboard.database import Base
from src.dashboard.models import DataRefreshRun
from src.dashboard.repository import (
    finish_refresh_run,
    latest_provider_statuses,
    start_refresh_run,
    update_provider_statuses,
)
from src.dashboard.services.data_pipeline import refresh_pipeline_data
from src.processor.trading_calendar import next_trading_day


def test_next_trading_day_skips_us_independence_day_closure() -> None:
    assert next_trading_day(date(2026, 7, 2), "NVDA") == date(2026, 7, 6)


def test_next_trading_day_uses_krx_calendar() -> None:
    assert next_trading_day(date(2026, 7, 3), "005930.KS") == date(2026, 7, 6)


def test_provider_failure_streak_resets_after_recovery() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        update_provider_statuses(
            db,
            {"gdelt": {"status": "failed", "message": "timeout"}},
        )
        update_provider_statuses(
            db,
            {"gdelt": {"status": "failed", "message": "timeout"}},
        )
        assert latest_provider_statuses(db)["gdelt"]["consecutive_failures"] == 2

        update_provider_statuses(
            db,
            {"gdelt": {"status": "healthy", "message": "recovered"}},
        )
        recovered = latest_provider_statuses(db)["gdelt"]
        assert recovered["consecutive_failures"] == 0
        assert recovered["first_failed_at"] == ""
        assert recovered["last_success_at"]


def test_failed_refresh_is_recorded(monkeypatch) -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    monkeypatch.setattr(
        NewsCollector,
        "collect_all",
        lambda self, max_records=100: (_ for _ in ()).throw(RuntimeError("provider exploded")),
    )
    with Session(engine) as db:
        with pytest.raises(RuntimeError, match="provider exploded"):
            refresh_pipeline_data(db, trigger="test")
        run = db.scalar(select(DataRefreshRun))
        assert run is not None
        assert run.status == "failed"
        assert run.trigger == "test"
        assert run.finished_at is not None
        assert run.error_message == "provider exploded"


def test_operations_endpoint_exposes_run_and_provider_history(
    isolated_dashboard_database,
) -> None:
    with isolated_dashboard_database() as db:
        run = start_refresh_run(db, trigger="test")
        update_provider_statuses(
            db,
            {"yfinance": {"status": "failed", "message": "empty response"}},
            run_id=run.id,
        )
        finish_refresh_run(db, run.id, status="partial", counts={"market_rows": 0})

    response = TestClient(app).get("/api/operations/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "degraded"
    assert payload["latestRun"]["status"] == "partial"
    assert payload["providers"]["yfinance"]["consecutive_failures"] == 1
    assert payload["recentProviderEvents"][0]["runId"] == payload["latestRun"]["id"]


def test_operations_endpoint_requires_authentication_in_production(
    monkeypatch,
    isolated_dashboard_database,
) -> None:
    monkeypatch.setattr("src.dashboard.routes.api._is_development_env", lambda: False)

    response = TestClient(app).get("/api/operations/status")

    assert response.status_code == 401
