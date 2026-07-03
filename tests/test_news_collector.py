import httpx

from src.collector.news_collector import NewsCollector


def test_gdelt_results_are_cached(monkeypatch):
    NewsCollector._cache.clear()
    calls = 0

    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "articles": [
                    {
                        "title": "AI cache test",
                        "url": "https://example.com/cache-test",
                        "domain": "example.com",
                        "seendate": "20260628090000",
                    }
                ]
            }

    def fake_get(*args, **kwargs):
        nonlocal calls
        calls += 1
        return Response()

    monkeypatch.setattr("src.collector.news_collector.httpx.get", fake_get)
    collector = NewsCollector()

    first = collector.collect_from_gdelt(keywords=["cache-test"], max_records=1)
    second = collector.collect_from_gdelt(keywords=["cache-test"], max_records=1)

    assert first == second
    assert calls == 1
    assert NewsCollector.provider_status()["message"] == "Live API cache hit"


def test_gdelt_timeout_reports_failure_without_disguising_seed_as_provider_data(monkeypatch):
    NewsCollector._cache.clear()

    def timeout(*args, **kwargs):
        raise httpx.ReadTimeout("timeout")

    monkeypatch.setattr("src.collector.news_collector.httpx.get", timeout)

    articles = NewsCollector().collect_from_gdelt(keywords=["timeout-test"], max_records=1)

    assert articles == []
    assert NewsCollector.provider_status()["status"] == "failed"
    assert "timed out" in NewsCollector.provider_status()["message"]


def test_gdelt_rate_limit_is_reported_with_http_status(monkeypatch):
    NewsCollector._cache.clear()

    def rate_limited(*args, **kwargs):
        request = httpx.Request("GET", "https://api.gdeltproject.org/api/v2/doc/doc")
        response = httpx.Response(429, request=request)
        raise httpx.HTTPStatusError("rate limited", request=request, response=response)

    monkeypatch.setattr("src.collector.news_collector.httpx.get", rate_limited)

    assert NewsCollector().collect_from_gdelt(keywords=["semiconductor"], max_records=1) == []
    assert NewsCollector.provider_status() == {
        "status": "rate_limited",
        "message": "GDELT returned HTTP 429",
    }
