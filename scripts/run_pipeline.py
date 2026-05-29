from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.collector.fake_news_checker import FakeNewsDetector
from src.collector.news_collector import NewsCollector
from src.collector.stock_collector import StockCollector
from src.notifier.discord_bot import DiscordNotifier
from src.processor.event_score import EventScoreCalculator
from src.processor.market_reaction import MarketReactionAnalyzer
from src.processor.news_filter import NewsFilter
from src.processor.sentiment import SentimentAnalyzer
from src.signal.generator import SignalGenerator


def main() -> None:
    news_collector = NewsCollector()
    articles = news_collector.deduplicate(news_collector.collect_from_gdelt() + news_collector.collect_from_newsapi())
    reliability = FakeNewsDetector().analyze_batch(articles)
    filtered = NewsFilter().filter(articles, reliability)
    if not filtered:
        print("No reliable articles passed the filter.")
        return

    article = filtered[0]
    sentiment = SentimentAnalyzer().analyze(f"{article['title']} {article.get('content', '')}")
    market = MarketReactionAnalyzer().analyze(StockCollector().collect_latest("005930.KS"))
    market["sentiment_score"] = float(sentiment["score"])
    event_score = EventScoreCalculator().calculate(float(article["reliability"]["final_score"]), float(sentiment["score"]), market)
    signal = SignalGenerator().generate(event_score, market, article["reliability"]["flags"])
    DiscordNotifier().send_signal_alert(
        signal,
        "005930.KS",
        {
            **market,
            "headline": article["title"],
            "reliability_score": article["reliability"]["final_score"],
            "sentiment_label": sentiment["label"],
        },
    )
    print({"signal": signal, "event_score": event_score, "headline": article["title"]})


if __name__ == "__main__":
    main()
