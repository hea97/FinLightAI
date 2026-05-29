from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/signals")
def get_signals() -> list[dict[str, str | float]]:
    return [
        {
            "ticker": "005930.KS",
            "signal": "YELLOW",
            "headline": "Semiconductor policy update affects AI chip supply",
            "reliability_score": 0.88,
            "return_1d": 0.021,
            "volume_ratio": 2.4,
        }
    ]


@router.get("/news")
def get_news() -> list[dict[str, str | float]]:
    return [
        {
            "title": "Semiconductor policy update affects AI chip supply",
            "source": "Reuters",
            "reliability_score": 0.88,
            "url": "https://www.reuters.com/technology/semiconductor-policy-ai-chip-supply",
        }
    ]


@router.get("/market")
def get_market() -> dict[str, float | str]:
    return {"ticker": "005930.KS", "return_1d": 0.021, "volume_ratio": 2.4, "volatility_5d": 0.018}
