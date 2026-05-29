from __future__ import annotations


class EventScoreCalculator:
    def calculate(self, reliability_score: float, sentiment_score: float, market_reaction: dict[str, float]) -> float:
        market_intensity = min(1.0, abs(market_reaction.get("return_1d", 0.0)) * 10 + market_reaction.get("volume_ratio", 0.0) / 5)
        sentiment_intensity = (sentiment_score + 1) / 2
        return round((reliability_score * 0.4) + (market_intensity * 0.35) + (sentiment_intensity * 0.25), 4)
