from __future__ import annotations

import math
from typing import Any

import pandas as pd


def safe_ratio(numerator: Any, denominator: Any, default: float = 0.0) -> float:
    """Return a finite ratio without leaking NaN/zero denominator values."""
    try:
        numerator_value = float(numerator)
        denominator_value = float(denominator)
    except (TypeError, ValueError):
        return default
    if not math.isfinite(numerator_value) or not math.isfinite(denominator_value) or denominator_value == 0:
        return default
    result = numerator_value / denominator_value
    return result if math.isfinite(result) else default


def calculate_market_metrics(frame: pd.DataFrame) -> pd.DataFrame:
    """Add backward-looking market metrics to normalized daily OHLCV rows."""
    result = frame.copy().sort_values("trade_date").reset_index(drop=True)
    close = pd.to_numeric(result["close"], errors="coerce")
    volume = pd.to_numeric(result["volume"], errors="coerce")

    result["return_1d"] = close.pct_change(fill_method=None)
    result["return_3d"] = close.pct_change(periods=3, fill_method=None)
    result["return_5d"] = close.pct_change(periods=5, fill_method=None)
    average_volume = volume.rolling(window=20, min_periods=2).mean().shift(1)
    result["volume_ratio"] = [safe_ratio(value, baseline) for value, baseline in zip(volume, average_volume, strict=False)]
    daily_return = close.pct_change(fill_method=None)
    result["volatility_5d"] = daily_return.rolling(window=5, min_periods=2).std(ddof=0)
    baseline_volatility = result["volatility_5d"].rolling(window=20, min_periods=2).mean().shift(1)
    result["volatility_ratio"] = [
        safe_ratio(value, baseline)
        for value, baseline in zip(result["volatility_5d"], baseline_volatility, strict=False)
    ]

    metric_columns = [
        "return_1d",
        "return_3d",
        "return_5d",
        "volume_ratio",
        "volatility_5d",
        "volatility_ratio",
    ]
    result[metric_columns] = result[metric_columns].replace([float("inf"), float("-inf")], pd.NA)
    return result
