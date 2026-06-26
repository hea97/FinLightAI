from fastapi.testclient import TestClient

from src.collector.news_collector import NewsCollector
from src.dashboard.app import app


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
    client = TestClient(app)

    for path in ["/api/briefing", "/api/industry-impact", "/api/portfolio", "/api/kakao-alert", "/api/mypage", "/api/settings"]:
        response = client.get(path)

        assert response.status_code == 200
        assert response.json()
