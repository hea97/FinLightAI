from dataclasses import dataclass


@dataclass(frozen=True)
class SignalThresholds:
    red_volume_ratio: float = 2.0
    red_sentiment_score: float = -0.3
    volatility_multiplier: float = 2.0
    yellow_abs_return_1d: float = 0.03
    yellow_volume_ratio: float = 2.0
