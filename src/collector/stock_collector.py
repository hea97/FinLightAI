from __future__ import annotations

from typing import Any


class StockCollector:
    def collect_latest(self, ticker: str) -> dict[str, Any]:
        return {
            "ticker": ticker,
            "close": 100.0,
            "previous_close": 98.0,
            "volume": 2_400_000,
            "ma_volume_20d": 1_000_000,
            "high": 103.0,
            "low": 96.0,
            "returns": [0.01, -0.02, 0.015, -0.005, 0.02],
        }
