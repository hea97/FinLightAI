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


def test_gdelt_timeout_uses_seed_fallback(monkeypatch):
    NewsCollector._cache.clear()

    def timeout(*args, **kwargs):
        raise httpx.ReadTimeout("timeout")

    monkeypatch.setattr("src.collector.news_collector.httpx.get", timeout)

    articles = NewsCollector().collect_from_gdelt(keywords=["timeout-test"], max_records=1)

    assert articles[0]["provider"] == "seed"
    assert NewsCollector.provider_status()["status"] == "failed"
