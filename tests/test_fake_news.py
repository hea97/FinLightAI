from src.collector.fake_news_checker import FakeNewsDetector


def test_reliable_multi_source_article_passes() -> None:
    articles = [
        {
            "title": "Semiconductor policy update affects AI chip supply",
            "content": "Semiconductor policy update affects AI chip supply and market expectations across major companies.",
            "author": "Reporter",
            "url": "https://www.reuters.com/technology/semiconductor-policy-ai-chip-supply",
            "published_at": "2026-05-29T00:00:00+00:00",
        },
        {
            "title": "AI chip supply affected by semiconductor policy update",
            "content": "AI chip supply is being reviewed after a semiconductor policy update.",
            "author": "Reporter",
            "url": "https://apnews.com/article/ai-chip-policy-market",
            "published_at": "2026-05-29T00:00:00+00:00",
        },
    ]
    result = FakeNewsDetector().analyze(articles[0], articles)
    assert result["is_reliable"] is True
    assert result["final_score"] >= 0.65


def test_untrusted_single_source_article_is_blocked() -> None:
    article = {
        "title": "SHOCKING!!! AI chip market collapse",
        "content": "Short claim.",
        "url": "https://unknown-blog.example/post",
        "published_at": "2026-05-29T00:00:00+00:00",
    }
    result = FakeNewsDetector().analyze(article, [article])
    assert result["is_reliable"] is False
    assert "untrusted_source" in result["flags"]
