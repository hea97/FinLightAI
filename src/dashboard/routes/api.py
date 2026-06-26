from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter

from config.settings import get_settings
from src.collector.news_collector import NewsCollector

router = APIRouter()
KST = timezone(timedelta(hours=9))


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
    articles = _load_gdelt_articles(max_records=20)
    return [
        {
            "title": article.get("title", "Untitled"),
            "source": article.get("source", "GDELT"),
            "reliability_score": _score_article(article),
            "url": article.get("url", ""),
        }
        for article in articles[:10]
    ]


@router.get("/market")
def get_market() -> dict[str, float | str]:
    return {"ticker": "005930.KS", "return_1d": 0.021, "volume_ratio": 2.4, "volatility_5d": 0.018}


@router.get("/briefing")
def get_briefing() -> dict[str, Any]:
    articles = _load_gdelt_articles(max_records=30)
    top_articles = articles[:5]
    caution_count = sum(1 for article in top_articles if _score_article(article) < 0.7)
    risk_score = min(100, 42 + caution_count * 9 + len(top_articles) * 2)

    return {
        "asOf": _now_label(),
        "signal": "YELLOW" if risk_score >= 60 else "GREEN",
        "riskScore": risk_score,
        "headline": "GDELT-based market briefing is ready.",
        "summary": [
            "Recent global AI and semiconductor news was collected from GDELT DOC 2.0.",
            "News Guard currently scores source, URL, and publish-time availability.",
            "Finnhub, KIS, and OpenAI keys can enrich price reaction, portfolio risk, and AI summaries.",
        ],
        "keyNews": [_to_briefing_news(article) for article in top_articles],
        "providerStatus": _provider_status(),
    }


@router.get("/news-guard")
def get_news_guard(filter: str = "all") -> dict[str, Any]:
    raw_articles = _load_gdelt_articles(max_records=50)
    all_articles = [_to_news_guard_article(article) for article in raw_articles]
    articles = all_articles
    if filter in {"trusted", "watch", "blocked"}:
        articles = [article for article in all_articles if article["reliabilityLevel"] == filter]

    total = len(articles)
    trusted = sum(1 for article in articles if article["reliabilityLevel"] == "trusted")
    watch = sum(1 for article in articles if article["reliabilityLevel"] == "watch")
    blocked = sum(1 for article in articles if article["reliabilityLevel"] == "blocked")
    average = round(sum(article["reliabilityScore"] for article in articles) / total, 2) if total else 0

    return {
        "stats": {
            "collectedNewsCount": total,
            "trustedNewsCount": trusted,
            "watchNewsCount": watch,
            "blockedNewsCount": blocked,
            "averageReliabilityScore": average,
            "deltaCollectedNewsCount": total,
        },
        "distribution": {
            "trusted": _distribution_item(trusted, total),
            "watch": _distribution_item(watch, total),
            "blocked": _distribution_item(blocked, total),
        },
        "blockReasons": [
            {"rank": 1, "reason": "Needs cross-source verification", "count": watch + blocked, "ratio": _ratio(watch + blocked, total)},
            {"rank": 2, "reason": "Full article body not collected yet", "count": total, "ratio": _ratio(total, total)},
            {"rank": 3, "reason": "Provider-specific scoring pending", "count": watch, "ratio": _ratio(watch, total)},
        ],
        "quickFilters": [
            {"id": "semiconductor", "label": "Semiconductor", "count": _count_mentions(raw_articles, ["semiconductor", "chip"])},
            {"id": "ai", "label": "AI", "count": _count_mentions(raw_articles, ["ai", "artificial intelligence", "gpu"])},
            {"id": "policy", "label": "Policy", "count": _count_mentions(raw_articles, ["policy", "export", "control", "regulation"])},
        ],
        "providerHealth": _provider_health(raw_articles),
        "articles": articles,
    }


@router.get("/industry-impact")
def get_industry_impact() -> dict[str, Any]:
    articles = _load_gdelt_articles(max_records=50)
    semiconductor_count = _count_mentions(articles, ["semiconductor", "chip", "nvidia", "samsung", "tsmc", "hynix"])
    ai_count = _count_mentions(articles, ["ai", "artificial intelligence", "gpu"])
    policy_count = _count_mentions(articles, ["policy", "export", "control", "regulation"])

    summaries = [
        _industry_summary("semiconductor", "Semiconductor", min(90, 45 + semiconductor_count * 4), semiconductor_count, "CHIP"),
        _industry_summary("it", "AI/IT", min(85, 38 + ai_count * 4), ai_count, "AI"),
        _industry_summary("policy", "Policy/Regulation", max(-70, -20 - policy_count * 5), policy_count, "POL"),
    ]

    return {
        "industries": summaries,
        "details": {summary["id"]: _industry_detail(summary, articles) for summary in summaries},
    }


@router.get("/portfolio")
def get_portfolio() -> dict[str, Any]:
    updated_at = _now_label()
    assets = [
        {
            "id": "asset-samsung",
            "assetName": "Samsung Electronics",
            "symbol": "005930",
            "market": "KR",
            "industry": "Semiconductor",
            "quantity": 32,
            "averageBuyPrice": 71800,
            "currentPrice": 74200,
            "recentSellPrice": 75600,
            "currency": "KRW",
            "status": "holding",
            "decisionMemo": "KIS price data is pending. Temporary reference price is displayed.",
            "relatedNewsCount": 12,
            "cautionNewsCount": 2,
            "updatedAt": updated_at,
        },
        {
            "id": "asset-nvidia",
            "assetName": "NVIDIA",
            "symbol": "NVDA",
            "market": "US",
            "industry": "AI/IT",
            "quantity": 5,
            "averageBuyPrice": 124.2,
            "currentPrice": 132.8,
            "currency": "USD",
            "status": "holding",
            "decisionMemo": "Finnhub or Alpha Vantage can replace this with live or delayed price data.",
            "relatedNewsCount": 14,
            "cautionNewsCount": 3,
            "updatedAt": updated_at,
        },
    ]
    total_input = sum(asset["quantity"] * asset["averageBuyPrice"] for asset in assets)
    total_current = sum(asset["quantity"] * asset["currentPrice"] for asset in assets)

    return {
        "summary": {
            "assetCount": len(assets),
            "totalInputAmount": round(total_input, 2),
            "totalCurrentAmount": round(total_current, 2),
            "valuationGap": round(total_current - total_input, 2),
            "valuationGapRate": round((total_current - total_input) / total_input * 100, 2),
            "linkedIndustryCount": 2,
            "cautionAlertCount": 2,
            "normalAlertCount": 5,
            "updatedAt": updated_at,
        },
        "assets": assets,
        "industryConnections": [
            {"id": "semiconductor", "industryName": "Semiconductor", "connectedAssetCount": 1, "signalLabel": "Positive"},
            {"id": "it", "industryName": "AI/IT", "connectedAssetCount": 1, "signalLabel": "Caution"},
        ],
        "linkedSignals": [
            {
                "id": "signal-gdelt",
                "industryName": "Semiconductor",
                "time": updated_at[-5:],
                "title": "GDELT semiconductor news increased",
                "summary": "News-based risk signal is active until market data APIs are connected.",
                "relatedAssetCount": 2,
                "tone": "caution",
            }
        ],
    }


@router.get("/kakao-alert")
def get_kakao_alert() -> dict[str, Any]:
    return {
        "badges": ["Kakao key pending", "FastAPI endpoint ready", "Test send can be wired after auth"],
        "rules": [
            {"id": "market-risk", "icon": "RISK", "label": "Market risk score >= 70", "enabled": True},
            {"id": "industry-impact", "icon": "IND", "label": "Watched industry impact >= 60", "enabled": True},
            {"id": "low-trust-news", "icon": "NEWS", "label": "Low-trust news detected", "enabled": True},
            {"id": "portfolio-news", "icon": "PORT", "label": "Portfolio-related news", "enabled": True},
            {"id": "red-signal", "icon": "RED", "label": "RED signal created", "enabled": True},
            {"id": "daily-briefing", "icon": "DAY", "label": "Daily AI briefing", "enabled": True},
        ],
        "questions": [
            {"id": "q1", "label": "Show today's market signal"},
            {"id": "q2", "label": "Any caution news?"},
            {"id": "q3", "label": "Show semiconductor impact"},
        ],
        "integrations": [
            {"id": "channel", "icon": "K", "label": "Kakao Channel", "value": "Application required", "health": "ready"},
            {"id": "api", "icon": "FL", "label": "FinLightAI API", "value": "Ready", "health": "normal"},
        ],
        "history": [],
        "flow": [
            {"id": "api", "icon": "FL", "title": "FinLightAI API", "subtitle": "Market/news analysis"},
            {"id": "kakao", "icon": "K", "title": "Kakao Message", "subtitle": "Send after key setup"},
        ],
        "previewMessages": [
            {
                "id": "m1",
                "sender": "bot",
                "time": "09:30",
                "body": "[FinLightAI] YELLOW signal\nGDELT-based briefing is ready.",
                "actionLabel": "Open dashboard",
            }
        ],
    }


@router.get("/mypage")
@router.get("/my-page")
def get_mypage() -> dict[str, Any]:
    return {
        "profile": {
            "username": "finlight_user",
            "email": "finlight@example.com",
            "joinedAt": "2026.06.01",
            "lastLoginAt": _now_label(),
            "language": "Korean",
            "alertChannel": "Kakao Channel",
            "channelConnected": False,
        },
        "metrics": [
            {"id": "weekly-alerts", "icon": "ALERT", "label": "Weekly alerts", "value": "0", "helper": "Kakao pending"},
            {"id": "industries", "icon": "IND", "label": "Watched industries", "value": "3", "helper": "Semiconductor, AI, Policy"},
        ],
        "alertSettings": [
            {"id": "kakao", "icon": "K", "title": "Kakao alerts", "description": "Enabled after Kakao API setup.", "enabled": False},
            {"id": "daily-briefing", "icon": "DAY", "title": "Daily AI briefing", "description": "Summarizes key news every day.", "enabled": True},
            {"id": "red-signal", "icon": "RED", "title": "RED signal alert", "description": "Shows high-risk signals immediately.", "enabled": True, "emphasis": True},
            {"id": "portfolio-news", "icon": "PORT", "title": "Portfolio news", "description": "Tracks watched assets.", "enabled": True},
            {"id": "news-guard", "icon": "NEWS", "title": "News Guard", "description": "Shows low-trust news caution signals.", "enabled": True},
        ],
        "interests": ["Semiconductor", "AI", "Policy/Regulation"],
        "connections": [
            {"id": "api", "icon": "FL", "label": "FinLightAI API", "status": "connected", "statusLabel": "Connected"},
            {"id": "news", "icon": "G", "label": "GDELT", "status": "normal", "statusLabel": "Ready"},
        ],
        "activities": [{"id": "a1", "icon": "API", "title": "GDELT real API endpoint prepared", "timestamp": _now_label()}],
        "shortcuts": [
            {"id": "portfolio", "icon": "PORT", "title": "Portfolio", "description": "Review watched assets"},
            {"id": "guard", "icon": "NEWS", "title": "News Guard", "description": "Review collected news"},
        ],
        "guide": {
            "title": "Real API migration",
            "body": "GDELT works without a key. Key-based providers will switch on when their credentials are added.",
            "ctaLabel": "Open settings",
        },
    }


@router.get("/settings")
def get_settings_view() -> dict[str, Any]:
    settings = get_settings()
    api_connections = [
        {"id": "gdelt", "name": "GDELT DOC 2.0 API", "connected": True},
        {"id": "newsapi", "name": "NewsAPI", "connected": bool(settings.news_api_key)},
        {"id": "guardian", "name": "The Guardian API", "connected": bool(settings.guardian_api_key)},
        {"id": "finnhub", "name": "Finnhub API", "connected": bool(settings.finnhub_api_key)},
        {"id": "alpha-vantage", "name": "Alpha Vantage", "connected": bool(settings.alpha_vantage_api_key)},
        {"id": "openai", "name": "OpenAI API", "connected": bool(settings.openai_api_key)},
        {"id": "opendart", "name": "OpenDART", "connected": bool(settings.opendart_api_key)},
        {"id": "kis", "name": "KIS Open API", "connected": bool(settings.kis_app_key and settings.kis_app_secret)},
        {"id": "kakao", "name": "Kakao Message API", "connected": bool(settings.kakao_rest_api_key)},
    ]
    connected_count = sum(1 for item in api_connections if item["connected"])

    return {
        "statusCards": [
            {"id": "data", "icon": "DATA", "title": "Data collection", "value": "Partially connected", "description": "GDELT real API is available.", "tone": "normal"},
            {"id": "api", "icon": "API", "title": "API integration", "value": f"{connected_count} / {len(api_connections)} connected", "description": "Credential-based APIs are waiting for keys.", "tone": "warning"},
            {"id": "guard", "icon": "GUARD", "title": "News Guard", "value": "Basic", "description": "Source and URL based scoring.", "tone": "strict"},
            {"id": "kakao", "icon": "K", "title": "Kakao alerts", "value": "Application required", "description": "Connect after Kakao developer/business setup.", "tone": "warning"},
        ],
        "dataCollection": {
            "newsInterval": "15 min",
            "newsRetention": "90 days",
            "marketDataRetention": "2 years",
            "keywords": NewsCollector.DEFAULT_KEYWORDS,
            "lowTrustFilter": True,
            "duplicateNewsRemoval": True,
        },
        "newsGuard": {
            "minimumSourceTrust": settings.min_source_score,
            "sensationalThreshold": 0.7,
            "minimumReportScore": 22,
            "sensitivity": "high",
            "mode": "strict",
        },
        "notifications": [
            {"id": "major-event", "label": "Major event alerts", "description": "When important news events occur", "enabled": True},
            {"id": "yellow-signal", "label": "YELLOW signal alerts", "description": "When caution signals occur", "enabled": True},
            {"id": "portfolio-risk", "label": "Portfolio risk alerts", "description": "Risk signals for watched assets", "enabled": True},
            {"id": "daily-briefing", "label": "Daily AI briefing", "description": "Daily summary", "enabled": True},
            {"id": "weekly-report", "label": "Weekly report", "description": "Weekly market summary", "enabled": True},
        ],
        "kakaoChannel": {
            "botName": "FinLightAI Kakao Channel",
            "statusLabel": "Application required",
            "description": "Connect alert sending after Kakao channel and message API setup.",
        },
        "apiConnections": api_connections,
        "display": {
            "language": "Korean",
            "theme": "Dark mode",
            "numberFormat": "Korea (KRW)",
            "timezone": "(UTC+09:00) Seoul",
        },
        "misc": {
            "searchLogRetention": "180 days",
            "sessionTimeout": "30 min",
            "kakaoNotice": "Production alerts should follow Kakao Bizmessage and channel policy.",
        },
    }


def _load_gdelt_articles(max_records: int = 50) -> list[dict[str, Any]]:
    collector = NewsCollector()
    return collector.deduplicate(collector.collect_from_gdelt(days=1, max_records=max_records))


def _to_news_guard_article(article: dict[str, Any]) -> dict[str, Any]:
    score = _score_article(article)
    if score >= 0.78:
        level = "trusted"
    elif score >= 0.5:
        level = "watch"
    else:
        level = "blocked"

    return {
        "id": _article_id(article),
        "title": article.get("title", "Untitled"),
        "source": article.get("source") or article.get("domain") or "GDELT",
        "publishedAgo": _published_label(article.get("published_at")),
        "summary": "Collected by GDELT. Full-body verification can be added with additional providers.",
        "reliabilityLevel": level,
        "reliabilityScore": score,
        "impactScore": _impact_score(article),
        "sentimentScore": _sentiment_score(article),
        "industries": _industries_for_article(article),
        "tags": _tags_for_article(article),
        "originalUrl": article.get("url", ""),
        "reasons": _reasons_for_score(score),
    }


def _to_briefing_news(article: dict[str, Any]) -> dict[str, Any]:
    return {
        "title": article.get("title", "Untitled"),
        "source": article.get("source") or "GDELT",
        "url": article.get("url", ""),
        "publishedAt": article.get("published_at", ""),
        "reliabilityScore": _score_article(article),
    }


def _industry_summary(industry_id: str, name: str, score: int, news_count: int, icon: str) -> dict[str, Any]:
    if score >= 40:
        tone = "positive"
        label = "Positive"
    elif score >= 10:
        tone = "weak_positive"
        label = "Weak positive"
    elif score > -10:
        tone = "neutral"
        label = "Neutral"
    elif score > -40:
        tone = "caution"
        label = "Caution"
    else:
        tone = "negative"
        label = "Negative"
    return {"id": industry_id, "name": name, "score": score, "tone": tone, "toneLabel": label, "newsCount": news_count, "icon": icon}


def _industry_detail(summary: dict[str, Any], articles: list[dict[str, Any]]) -> dict[str, Any]:
    top_news = [_to_related_news(index, article) for index, article in enumerate(articles[:5], start=1)]
    return {
        "industryId": summary["id"],
        "title": f"{summary['name']} detail",
        "score": summary["score"],
        "statusLabel": summary["toneLabel"],
        "description": f"{summary['name']} impact is calculated from GDELT news flow. Market price reaction can be added after price API setup.",
        "relatedStocks": _related_stocks(summary["id"]),
        "newsCount": summary["newsCount"],
        "averageSentiment": round(summary["score"] / 100, 2),
        "riskPoints": 2 if summary["score"] < 0 else 1,
        "updatedAt": _now_label(),
        "reasons": {
            "positive": ["Related news volume detected", "Core technology or policy keywords found"],
            "caution": ["Price data not connected yet", "Additional source verification recommended"],
        },
        "topNews": top_news,
    }


def _to_related_news(rank: int, article: dict[str, Any]) -> dict[str, Any]:
    sentiment = _sentiment_score(article)
    if sentiment > 0.15:
        label = "Positive"
    elif sentiment < -0.15:
        label = "Negative"
    else:
        label = "Neutral"

    return {
        "id": _article_id(article),
        "rank": rank,
        "title": article.get("title", "Untitled"),
        "source": article.get("source") or "GDELT",
        "sentimentLabel": label,
        "impactScore": round(_impact_score(article) / 100, 2),
    }


def _score_article(article: dict[str, Any]) -> float:
    score = 0.58
    if article.get("url"):
        score += 0.18
    if article.get("domain") or article.get("source"):
        score += 0.14
    if article.get("published_at"):
        score += 0.08
    if article.get("provider") == "GDELT":
        score += 0.02
    return round(min(score, 0.96), 2)


def _impact_score(article: dict[str, Any]) -> int:
    text = _article_text(article)
    score = 45
    for keyword in ["semiconductor", "chip", "nvidia", "samsung", "tsmc", "hynix", "export", "policy", "ai"]:
        if keyword in text:
            score += 6
    return min(score, 92)


def _sentiment_score(article: dict[str, Any]) -> float:
    text = _article_text(article)
    positive = sum(1 for word in ["growth", "supply", "support", "investment", "positive", "gain"] if word in text)
    negative = sum(1 for word in ["risk", "control", "restriction", "ban", "decline", "negative", "loss"] if word in text)
    return round(max(-0.8, min(0.8, (positive - negative) * 0.16)), 2)


def _count_mentions(articles: list[dict[str, Any]], keywords: list[str]) -> int:
    return sum(1 for article in articles if _mentions(article, keywords))


def _mentions(article: dict[str, Any], keywords: list[str]) -> bool:
    text = _article_text(article)
    return any(keyword in text for keyword in keywords)


def _article_text(article: dict[str, Any]) -> str:
    return f"{article.get('title', '')} {article.get('content', '')}".lower()


def _industries_for_article(article: dict[str, Any]) -> list[str]:
    industries = []
    if _mentions(article, ["semiconductor", "chip", "nvidia", "samsung", "tsmc", "hynix"]):
        industries.append("Semiconductor")
    if _mentions(article, ["ai", "gpu", "artificial intelligence"]):
        industries.append("AI/IT")
    if _mentions(article, ["policy", "export", "control", "regulation"]):
        industries.append("Policy/Regulation")
    return industries or ["Market"]


def _tags_for_article(article: dict[str, Any]) -> list[str]:
    tags = []
    if _mentions(article, ["export", "control", "policy", "regulation"]):
        tags.append("Policy")
    if _mentions(article, ["nvidia", "samsung", "tsmc", "sk hynix"]):
        tags.append("Company")
    if _mentions(article, ["ai", "semiconductor", "chip"]):
        tags.append("Technology")
    return tags or ["News"]


def _reasons_for_score(score: float) -> list[str]:
    if score >= 0.78:
        return ["URL present", "Source domain present", "Collected by GDELT"]
    if score >= 0.5:
        return ["Collected by GDELT", "Needs cross-source verification"]
    return ["Weak source evidence", "Full-body analysis needed"]


def _related_stocks(industry_id: str) -> list[str]:
    mapping = {
        "semiconductor": ["Samsung Electronics", "SK Hynix", "NVIDIA", "TSMC"],
        "it": ["NVIDIA", "Microsoft", "NAVER"],
        "policy": ["Samsung Electronics", "SK Hynix", "NVIDIA"],
    }
    return mapping.get(industry_id, ["Watched asset"])


def _distribution_item(count: int, total: int) -> dict[str, float | int]:
    return {"count": count, "ratio": _ratio(count, total)}


def _ratio(count: int, total: int) -> float:
    return round((count / total * 100), 1) if total else 0


def _article_id(article: dict[str, Any]) -> str:
    raw = f"{article.get('url', '')}|{article.get('title', '')}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:12]


def _published_label(value: Any) -> str:
    if not value:
        return "recent"
    return str(value)


def _provider_status() -> dict[str, str]:
    settings = get_settings()
    return {
        "gdelt": "connected",
        "newsapi": "connected" if settings.news_api_key else "waiting_for_api_key",
        "guardian": "connected" if settings.guardian_api_key else "waiting_for_api_key",
        "finnhub": "connected" if settings.finnhub_api_key else "waiting_for_api_key",
        "alphaVantage": "connected" if settings.alpha_vantage_api_key else "waiting_for_api_key",
        "kis": "connected" if settings.kis_app_key and settings.kis_app_secret else "waiting_for_api_key",
        "openai": "connected" if settings.openai_api_key else "waiting_for_api_key",
        "kakao": "connected" if settings.kakao_rest_api_key else "waiting_for_api_key",
    }


def _provider_health(articles: list[dict[str, Any]]) -> list[dict[str, str]]:
    using_seed = any(article.get("provider") == "seed" for article in articles)
    gdelt_status = "partial" if using_seed else "healthy"
    gdelt_message = "Using seed fallback; live call returned no data or failed" if using_seed else "Live API connected"
    return [
        {"provider": "GDELT", "status": gdelt_status, "message": gdelt_message, "lastCheckedAt": _now_label()},
        {"provider": "NewsAPI", "status": "disabled", "message": "API key pending"},
        {"provider": "Guardian", "status": "disabled", "message": "API key pending"},
        {"provider": "Finnhub", "status": "disabled", "message": "API key pending"},
        {"provider": "BBC RSS", "status": "partial", "message": "Backup provider candidate"},
    ]


def _now_label() -> str:
    return datetime.now(timezone.utc).astimezone(KST).strftime("%Y.%m.%d %H:%M")
