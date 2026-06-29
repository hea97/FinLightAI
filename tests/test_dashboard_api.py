from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import func, select

from src.collector.news_collector import NewsCollector
from src.dashboard.app import app
from src.dashboard.database import SessionLocal
from src.dashboard.models import NewsRaw, Signal
from src.processor.gemini_client import GeminiClient


def _sample_articles():
    return [
        {
            "source": "example.com",
            "title": "AI chip export policy affects semiconductor supply",
            "content": "AI chip policy creates risk for semiconductor supply.",
            "author": "GDELT",
            "url": "https://example.com/ai-chip-policy",
            "published_at": "20260626090000",
            "domain": "example.com",
            "language": "English",
            "source_country": "US",
            "provider": "GDELT",
        }
    ]


def test_news_guard_endpoint_returns_view_model(monkeypatch):
    monkeypatch.setattr(NewsCollector, "collect_from_gdelt", lambda self, days=1, max_records=50, keywords=None: _sample_articles())

    response = TestClient(app).get("/api/news-guard")

    assert response.status_code == 200
    payload = response.json()
    assert payload["stats"]["collectedNewsCount"] == 1
    assert payload["providerHealth"][0]["provider"] == "GDELT"
    assert payload["articles"][0]["reliabilityLevel"] == "trusted"


def test_core_real_api_transition_endpoints(monkeypatch):
    monkeypatch.setattr(NewsCollector, "collect_from_gdelt", lambda self, days=1, max_records=50, keywords=None: _sample_articles())
    monkeypatch.setattr(
        GeminiClient,
        "generate_briefing",
        lambda self, articles: {"headline": "AI briefing generated.", "summary": ["One", "Two", "Three"]},
    )
    client = TestClient(app)

    for path in ["/api/briefing", "/api/industry-impact", "/api/portfolio", "/api/kakao-alert", "/api/mypage", "/api/settings"]:
        response = client.get(path)

        assert response.status_code == 200
        assert response.json()


def test_portfolio_crud_is_scoped_to_user():
    client = TestClient(app)
    user_id = f"test-{uuid4().hex}"
    other_user_id = f"test-{uuid4().hex}"
    headers = {"X-User-ID": user_id}
    payload = {
        "assetName": "Test Asset",
        "symbol": f"T{uuid4().hex[:7].upper()}",
        "market": "US",
        "industry": "AI/IT",
        "quantity": 2,
        "averageBuyPrice": 100,
        "currentPrice": 110,
        "currency": "USD",
        "status": "holding",
        "decisionMemo": "API integration test",
    }

    created = client.post("/api/portfolio", headers=headers, json=payload)
    assert created.status_code == 201
    asset = created.json()
    assert asset["symbol"] == payload["symbol"]

    duplicate = client.post("/api/portfolio", headers=headers, json=payload)
    assert duplicate.status_code == 409

    hidden = client.patch(
        f"/api/portfolio/{asset['id']}",
        headers={"X-User-ID": other_user_id},
        json={**payload, "currentPrice": 120},
    )
    assert hidden.status_code == 404

    updated = client.patch(
        f"/api/portfolio/{asset['id']}",
        headers=headers,
        json={**payload, "currentPrice": 120},
    )
    assert updated.status_code == 200
    assert updated.json()["currentPrice"] == 120

    deleted = client.delete(f"/api/portfolio/{asset['id']}", headers=headers)
    assert deleted.status_code == 204


def test_user_settings_and_alert_rules_are_persisted():
    client = TestClient(app)
    user_id = f"test-{uuid4().hex}"
    headers = {"X-User-ID": user_id}

    settings = client.get("/api/settings", headers=headers)
    assert settings.status_code == 200
    payload = settings.json()
    payload["notifications"][0]["enabled"] = False
    writable = {
        key: payload[key]
        for key in ["dataCollection", "newsGuard", "notifications", "display", "misc"]
    }

    saved = client.put("/api/settings", headers=headers, json=writable)
    assert saved.status_code == 200
    assert saved.json()["notifications"][0]["enabled"] is False
    assert client.get("/api/settings", headers=headers).json()["notifications"][0]["enabled"] is False

    rule = client.patch(
        "/api/kakao-alert/rules/daily-briefing",
        headers=headers,
        json={"enabled": False},
    )
    assert rule.status_code == 200
    assert rule.json()["enabled"] is False

    mypage = client.patch(
        "/api/mypage",
        headers=headers,
        json={"interests": ["AI", "Semiconductor", "AI"]},
    )
    assert mypage.status_code == 200
    assert mypage.json()["interests"] == ["AI", "Semiconductor"]


def test_dashboard_requests_do_not_mutate_development_database(monkeypatch):
    with SessionLocal() as development_db:
        before = (
            development_db.scalar(select(func.count()).select_from(NewsRaw)),
            development_db.scalar(select(func.count()).select_from(Signal)),
        )

    monkeypatch.setattr(
        NewsCollector,
        "collect_from_gdelt",
        lambda self, days=1, max_records=50, keywords=None: _sample_articles(),
    )
    response = TestClient(app).get("/api/news-guard")

    assert response.status_code == 200
    with SessionLocal() as development_db:
        after = (
            development_db.scalar(select(func.count()).select_from(NewsRaw)),
            development_db.scalar(select(func.count()).select_from(Signal)),
        )
    assert after == before
