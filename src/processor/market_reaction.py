from __future__ import annotations

import statistics
from typing import Any


class MarketReactionAnalyzer:
    def analyze(self, market_data: dict[str, Any]) -> dict[str, float]:
        close = float(market_data["close"])
        previous_close = float(market_data["previous_close"])
        volume = float(market_data["volume"])
        ma_volume = max(float(market_data.get("ma_volume_20d") or 1), 1)
        returns = [float(value) for value in market_data.get("returns", [])]
        return {
            "return_1d": round((close - previous_close) / previous_close, 6),
            "volume_ratio": round(volume / ma_volume, 4),
            "volatility_5d": round(statistics.pstdev(returns[-5:]) if len(returns) >= 2 else 0.0, 6),
        }
