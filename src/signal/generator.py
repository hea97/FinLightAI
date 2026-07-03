from __future__ import annotations

from src.signal.thresholds import SignalThresholds


class SignalGenerator:
    def __init__(self, thresholds: SignalThresholds | None = None) -> None:
        self.thresholds = thresholds or SignalThresholds()

    def generate(self, event_score: float, market_data: dict[str, float], fake_news_flags: list[str] | None = None) -> str:
        if fake_news_flags:
            return "GREEN"

        volatility = market_data.get("volatility_5d", 0.0)
        volume_ratio = market_data.get("volume_ratio", 0.0)
        sentiment_score = market_data.get("sentiment_score", 0.0)
        return_1d = market_data.get("return_1d", 0.0)
        volatility_ratio = market_data.get("volatility_ratio", 0.0)

        if (
            event_score >= 0.7
            and abs(return_1d) >= 0.02
            and volatility >= self.thresholds.yellow_abs_return_1d * self.thresholds.volatility_multiplier
            and volume_ratio >= self.thresholds.red_volume_ratio
            and (volatility_ratio >= 1.3 or volatility_ratio == 0)
            and sentiment_score <= self.thresholds.red_sentiment_score
        ):
            return "RED"
        if abs(return_1d) >= self.thresholds.yellow_abs_return_1d or volume_ratio >= self.thresholds.yellow_volume_ratio:
            return "YELLOW"
        return "GREEN"
