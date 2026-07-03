from __future__ import annotations

from typing import Any


class EventScoreCalculator:
    TICKER_RULES = {
        "NVDA": ("ai", "nvidia", "gpu", "semiconductor", "chip", "export control"),
        "AMD": ("ai", "amd", "gpu", "semiconductor", "chip", "export control"),
        "005930.KS": ("samsung", "korea", "semiconductor", "chip", "export control"),
        "000660.KS": ("sk hynix", "hynix", "korea", "semiconductor", "chip", "export control"),
        "SOXX": ("semiconductor", "chip", "export control"),
        "SMH": ("semiconductor", "chip", "export control"),
        "AIQ": ("ai", "artificial intelligence"),
    }

    def calculate(self, reliability_score: float, sentiment_score: float, market_reaction: dict[str, float]) -> float:
        market_intensity = self.market_reaction_score(market_reaction)
        sentiment_intensity = (sentiment_score + 1) / 2
        return round((reliability_score * 0.4) + (market_intensity * 0.35) + (sentiment_intensity * 0.25), 4)

    def affected_tickers(self, article: dict[str, Any]) -> list[str]:
        text = f"{article.get('title', '')} {article.get('content', '')} {article.get('summary', '')}".lower()
        matched = [
            ticker
            for ticker, keywords in self.TICKER_RULES.items()
            if any(keyword in text for keyword in keywords)
        ]
        return matched or ["AIQ"]

    @staticmethod
    def market_reaction_score(market_reaction: dict[str, float]) -> float:
        points = 0
        if abs(float(market_reaction.get("return_1d") or 0)) >= 0.02:
            points += 1
        if float(market_reaction.get("volume_ratio") or 0) >= 1.5:
            points += 1
        if float(market_reaction.get("volatility_ratio") or 0) >= 1.3:
            points += 1
        return round(points / 3, 4)

    def evidence(self, article: dict[str, Any], market_reaction: dict[str, float]) -> dict[str, Any]:
        return {
            "title": article.get("title", ""),
            "headline": article.get("title", ""),
            "url": article.get("url", ""),
            "published_utc": article.get("published_utc") or article.get("published_at", ""),
            "source": article.get("source", ""),
            "provider": article.get("provider", "unknown"),
            "source_score": article.get("source_score"),
            "keyword_score": article.get("keyword_score"),
            "return_1d": market_reaction.get("return_1d"),
            "volume_ratio": market_reaction.get("volume_ratio"),
            "volatility_ratio": market_reaction.get("volatility_ratio"),
            "market_reaction_score": self.market_reaction_score(market_reaction),
        }
