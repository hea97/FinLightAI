from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pandas as pd
import yfinance as yf

from src.processor.market_metrics import calculate_market_metrics


class StockCollector:
    DEFAULT_TICKERS = ("NVDA", "AMD", "005930.KS", "000660.KS")
    OPTIONAL_ETFS = ("SOXX", "SMH", "AIQ")

    def collect_daily(
        self,
        tickers: list[str] | tuple[str, ...] | None = None,
        period: str = "3mo",
    ) -> list[dict[str, Any]]:
        selected = tuple(tickers or self.DEFAULT_TICKERS)
        rows: list[dict[str, Any]] = []
        fetched_at = datetime.now(timezone.utc)
        for ticker in selected:
            try:
                history = yf.Ticker(ticker).history(period=period, interval="1d", auto_adjust=False)
            except Exception:
                continue
            if history.empty:
                continue
            normalized = self._normalize_history(ticker, history)
            enriched = calculate_market_metrics(normalized)
            for record in enriched.to_dict(orient="records"):
                record["fetched_at"] = fetched_at
                record["provider"] = "yfinance"
                record["data_source"] = "real"
                rows.append(self._clean_record(record))
        return rows

    def collect_latest(self, ticker: str) -> dict[str, Any]:
        records = self.collect_daily([ticker])
        if not records:
            raise RuntimeError(f"No market data returned for {ticker}")
        latest = records[-1]
        ticker_rows = [row for row in records if row["ticker"] == ticker]
        latest["previous_close"] = ticker_rows[-2]["close"] if len(ticker_rows) > 1 else latest["close"]
        latest["ma_volume_20d"] = (
            sum(float(row["volume"]) for row in ticker_rows[-21:-1]) / max(len(ticker_rows[-21:-1]), 1)
        )
        latest["returns"] = [row["return_1d"] or 0.0 for row in ticker_rows[-5:]]
        return latest

    @staticmethod
    def _normalize_history(ticker: str, history: pd.DataFrame) -> pd.DataFrame:
        frame = history.reset_index()
        date_column = "Date" if "Date" in frame.columns else frame.columns[0]
        normalized = pd.DataFrame(
            {
                "ticker": ticker,
                "trade_date": pd.to_datetime(frame[date_column], utc=True).dt.date,
                "open": frame["Open"],
                "high": frame["High"],
                "low": frame["Low"],
                "close": frame["Close"],
                "volume": frame["Volume"],
            }
        )
        return normalized.dropna(subset=["trade_date", "close"])

    @staticmethod
    def _clean_record(record: dict[str, Any]) -> dict[str, Any]:
        cleaned: dict[str, Any] = {}
        for key, value in record.items():
            if pd.isna(value):
                cleaned[key] = None
            elif hasattr(value, "item"):
                cleaned[key] = value.item()
            else:
                cleaned[key] = value
        return cleaned
