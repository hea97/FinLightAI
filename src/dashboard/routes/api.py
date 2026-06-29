from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, Response, status
from sqlalchemy.orm import Session

from config.settings import get_settings
from src.collector.news_collector import NewsCollector
from src.dashboard.database import get_db
from src.dashboard.models import PortfolioAsset as PortfolioAssetRecord
from src.dashboard.services.data_pipeline import PipelineSnapshot, load_pipeline_snapshot
from src.dashboard.repository import (
    DuplicatePortfolioAssetError,
    create_asset,
    delete_asset,
    ensure_user,
    get_kakao_rules,
    get_user_settings,
    latest_signals,
    latest_stock_prices,
    list_assets,
    save_user_settings,
    update_asset,
    update_kakao_rule,
    update_mypage,
)
from src.dashboard.schemas import (
    BriefingResponse,
    IndustryImpactResponse,
    KakaoAlertResponse,
    KakaoAlertRule,
    KakaoRuleUpdate,
    MyPageResponse,
    MyPageUpdate,
    NewsGuardResponse,
    PortfolioAsset,
    PortfolioAssetInput,
    PortfolioResponse,
    SettingsResponse,
    SettingsUpdate,
)
from src.processor.event_score import EventScoreCalculator
from src.processor.news_relevance import contains_term
from src.signal.generator import SignalGenerator

router = APIRouter()
KST = timezone(timedelta(hours=9))


def get_current_user_id(x_user_id: str = Header(default="demo-user")) -> str:
    user_id = x_user_id.strip()
    if not user_id or len(user_id) > 80 or not all(char.isalnum() or char in {"-", "_"} for char in user_id):
        raise HTTPException(status_code=400, detail="Invalid X-User-ID header")
    return user_id


@router.get("/signals")
def get_signals(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    return [
        {
            "event_key": row.event_key,
            "ticker": row.ticker,
            "trade_date": row.trade_date.isoformat(),
            "signal": row.signal,
            "event_score": row.event_score,
            "market_reaction_score": row.market_reaction_score,
            "data_source": row.data_source,
            "is_verified": bool(
                row.data_source == "real"
                and row.evidence.get("url")
                and row.evidence.get("source")
                and row.evidence.get("provider")
            ),
            "evidence": row.evidence,
            "created_at": row.created_at.isoformat() if row.created_at else None,
        }
        for row in latest_signals(db)
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
def get_market(
    ticker: str = "005930.KS",
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    rows = latest_stock_prices(db, [ticker])
    if not rows:
        return {
            "ticker": ticker,
            "dataSource": "not_connected",
            "provider": None,
            "lastUpdated": None,
            "warnings": ["No stored market data is available"],
        }
    row = rows[0]
    return {
        "ticker": row.ticker,
        "trade_date": row.trade_date.isoformat(),
        "close": row.close,
        "return_1d": row.return_1d,
        "return_3d": row.return_3d,
        "return_5d": row.return_5d,
        "volume_ratio": row.volume_ratio,
        "volatility_5d": row.volatility_5d,
        "volatility_ratio": row.volatility_ratio,
        "dataSource": row.data_source,
        "provider": row.provider,
        "lastUpdated": row.fetched_at.isoformat() if row.fetched_at else row.trade_date.isoformat(),
        "warnings": [],
    }


@router.get("/briefing", response_model=BriefingResponse)
def get_briefing(db: Session = Depends(get_db)) -> dict[str, Any]:
    snapshot = load_pipeline_snapshot(db, max_news=30)
    articles = snapshot.articles
    top_articles = articles[:5]
    caution_count = sum(1 for article in top_articles if _score_article(article) < 0.7)
    market = _strongest_market_reaction(snapshot.market)
    market_score = EventScoreCalculator.market_reaction_score(market)
    risk_score = min(100, round(32 + caution_count * 9 + len(top_articles) * 2 + market_score * 36))
    event_score = EventScoreCalculator().calculate(
        max((_score_article(article) for article in top_articles), default=0),
        min((_sentiment_score(article) for article in top_articles), default=0),
        market,
    )
    market["sentiment_score"] = min((_sentiment_score(article) for article in top_articles), default=0)
    signal = SignalGenerator().generate(event_score, market)
    ai_briefing = None
    gemini_status = snapshot.provider_status.get("gemini", "fallback")
    fallback_summary = [
        "Recent relevant AI and semiconductor news was loaded from the available pipeline data.",
        "News quality, provider state, and market reaction are shown separately.",
        "This fallback summary is used because the AI briefing provider is unavailable.",
    ]
    metadata = snapshot.metadata()
    provider_status = _provider_status(snapshot, gemini_status)
    if gemini_status not in {"healthy", "cached", "connected"}:
        metadata["warnings"] = list(
            dict.fromkeys(
                [
                    *metadata["warnings"],
                    f"Gemini {provider_status['gemini']}; using static briefing fallback",
                ]
            )
        )

    return {
        "asOf": _now_label(),
        "signal": signal,
        "riskScore": risk_score,
        "headline": ai_briefing["headline"] if ai_briefing else "Market briefing fallback is ready.",
        "summary": ai_briefing["summary"] if ai_briefing else fallback_summary,
        "keyNews": [_to_briefing_news(article) for article in top_articles],
        "providerStatus": provider_status,
        **metadata,
    }


@router.get("/news-guard", response_model=NewsGuardResponse)
def get_news_guard(filter: str = "all", db: Session = Depends(get_db)) -> dict[str, Any]:
    snapshot = load_pipeline_snapshot(db, max_news=50)
    raw_articles = snapshot.articles
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
        "providerHealth": _provider_health(snapshot),
        "articles": articles,
        **snapshot.metadata(),
    }


@router.get("/industry-impact", response_model=IndustryImpactResponse)
def get_industry_impact(db: Session = Depends(get_db)) -> dict[str, Any]:
    snapshot = load_pipeline_snapshot(db, max_news=50)
    articles = snapshot.articles
    semiconductor_count = _count_mentions(articles, ["semiconductor", "chip", "nvidia", "samsung", "tsmc", "hynix"])
    ai_count = _count_mentions(articles, ["ai", "artificial intelligence", "gpu"])
    policy_count = _count_mentions(articles, ["policy", "export", "control", "regulation"])

    semiconductor_adjustment = _industry_market_adjustment(snapshot.market, "semiconductor")
    ai_adjustment = _industry_market_adjustment(snapshot.market, "it")
    summaries = [
        _industry_summary("semiconductor", "Semiconductor", _bounded_score(semiconductor_count * 8 + semiconductor_adjustment), semiconductor_count, "CHIP"),
        _industry_summary("it", "AI/IT", _bounded_score(ai_count * 8 + ai_adjustment), ai_count, "AI"),
        _industry_summary("policy", "Policy/Regulation", _bounded_score(-policy_count * 8), policy_count, "POL"),
    ]

    return {
        "industries": summaries,
        "details": {
            summary["id"]: _industry_detail(summary, articles, bool(snapshot.market))
            for summary in summaries
        },
        **snapshot.metadata(),
    }


@router.get("/portfolio", response_model=PortfolioResponse)
def get_portfolio(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    records = list_assets(db, user_id)
    market_rows = latest_stock_prices(db)
    return _portfolio_response(records, market_rows, latest_signals(db, limit=20))


@router.post("/portfolio", response_model=PortfolioAsset, status_code=status.HTTP_201_CREATED)
def post_portfolio_asset(
    payload: PortfolioAssetInput,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    try:
        asset = create_asset(db, user_id, payload)
    except DuplicatePortfolioAssetError as exc:
        raise HTTPException(status_code=409, detail="This asset is already in the portfolio") from exc
    return _portfolio_asset_dict(asset)


@router.patch("/portfolio/{asset_id}", response_model=PortfolioAsset)
def patch_portfolio_asset(
    asset_id: str,
    payload: PortfolioAssetInput,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    try:
        asset = update_asset(db, user_id, asset_id, payload)
    except DuplicatePortfolioAssetError as exc:
        raise HTTPException(status_code=409, detail="This asset is already in the portfolio") from exc
    if not asset:
        raise HTTPException(status_code=404, detail="Portfolio asset not found")
    return _portfolio_asset_dict(asset)


@router.delete("/portfolio/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_portfolio_asset(
    asset_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> Response:
    if not delete_asset(db, user_id, asset_id):
        raise HTTPException(status_code=404, detail="Portfolio asset not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/kakao-alert", response_model=KakaoAlertResponse)
def get_kakao_alert(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    settings = get_settings()
    rules = get_kakao_rules(db, user_id)
    kakao_ready = bool(settings.kakao_rest_api_key and settings.kakao_channel_id)
    return {
        "badges": [
            "Kakao API configured" if kakao_ready else "Kakao key pending",
            "Alert rules persisted",
            "Test send available after OAuth",
        ],
        "rules": [{"id": rule.rule_id, "icon": rule.icon, "label": rule.label, "enabled": rule.enabled} for rule in rules],
        "questions": [
            {"id": "q1", "label": "Show today's market signal"},
            {"id": "q2", "label": "Any caution news?"},
            {"id": "q3", "label": "Show semiconductor impact"},
        ],
        "integrations": [
            {
                "id": "channel",
                "icon": "K",
                "label": "Kakao Channel",
                "value": "Configured" if kakao_ready else "Application required",
                "health": "connected" if kakao_ready else "ready",
            },
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


@router.patch("/kakao-alert/rules/{rule_id}", response_model=KakaoAlertRule)
def patch_kakao_rule(
    rule_id: str,
    payload: KakaoRuleUpdate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    rule = update_kakao_rule(db, user_id, rule_id, payload.enabled)
    if not rule:
        raise HTTPException(status_code=404, detail="Kakao alert rule not found")
    return {"id": rule.rule_id, "icon": rule.icon, "label": rule.label, "enabled": rule.enabled}


@router.get("/mypage", response_model=MyPageResponse)
@router.get("/my-page", response_model=MyPageResponse)
def get_mypage(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    user = ensure_user(db, user_id)
    return {
        "profile": {
            "username": user.username,
            "email": user.email,
            "joinedAt": _format_datetime(user.created_at),
            "lastLoginAt": _format_datetime(user.last_login_at),
            "language": user.language,
            "alertChannel": user.alert_channel,
            "channelConnected": user.channel_connected,
        },
        "metrics": [
            {"id": "weekly-alerts", "icon": "ALERT", "label": "Weekly alerts", "value": "0", "helper": "Kakao pending"},
            {"id": "industries", "icon": "IND", "label": "Watched industries", "value": "3", "helper": "Semiconductor, AI, Policy"},
        ],
        "alertSettings": user.alert_settings,
        "interests": user.interests,
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


@router.patch("/mypage", response_model=MyPageResponse)
@router.patch("/my-page", response_model=MyPageResponse)
def patch_mypage(
    payload: MyPageUpdate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    update_mypage(
        db,
        user_id,
        [item.model_dump(by_alias=True, exclude_none=True) for item in payload.alert_settings] if payload.alert_settings is not None else None,
        payload.interests,
    )
    return get_mypage(user_id, db)


@router.get("/settings", response_model=SettingsResponse)
def get_settings_view(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    settings = get_settings()
    api_connections = [
        {"id": "gdelt", "name": "GDELT DOC 2.0 API", "connected": True},
        {"id": "newsapi", "name": "NewsAPI", "connected": bool(settings.news_api_key)},
        {"id": "guardian", "name": "The Guardian API", "connected": bool(settings.guardian_api_key)},
        {"id": "finnhub", "name": "Finnhub API", "connected": bool(settings.finnhub_api_key)},
        {"id": "alpha-vantage", "name": "Alpha Vantage", "connected": bool(settings.alpha_vantage_api_key)},
        {"id": "gemini", "name": "Gemini API", "connected": bool(settings.gemini_api_key)},
        {"id": "openai", "name": "OpenAI API", "connected": bool(settings.openai_api_key)},
        {"id": "opendart", "name": "OpenDART", "connected": bool(settings.opendart_api_key)},
        {"id": "kis", "name": "KIS Open API", "connected": bool(settings.kis_app_key and settings.kis_app_secret)},
        {"id": "kakao", "name": "Kakao Message API", "connected": bool(settings.kakao_rest_api_key)},
    ]
    connected_count = sum(1 for item in api_connections if item["connected"])

    defaults = {
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
    stored = get_user_settings(db, user_id, defaults)
    return {
        "statusCards": [
            {"id": "data", "icon": "DATA", "title": "Data collection", "value": "Partially connected", "description": "GDELT real API is available.", "tone": "normal"},
            {"id": "api", "icon": "API", "title": "API integration", "value": f"{connected_count} / {len(api_connections)} connected", "description": "Credential-based APIs are waiting for keys.", "tone": "warning"},
            {"id": "guard", "icon": "GUARD", "title": "News Guard", "value": "Basic", "description": "Source and URL based scoring.", "tone": "strict"},
            {"id": "kakao", "icon": "K", "title": "Kakao alerts", "value": "Application required", "description": "Connect after Kakao developer/business setup.", "tone": "warning"},
        ],
        "dataCollection": stored["dataCollection"],
        "newsGuard": stored["newsGuard"],
        "notifications": stored["notifications"],
        "kakaoChannel": {
            "botName": "FinLightAI Kakao Channel",
            "statusLabel": "Application required",
            "description": "Connect alert sending after Kakao channel and message API setup.",
        },
        "apiConnections": api_connections,
        "display": stored["display"],
        "misc": stored["misc"],
    }


@router.put("/settings", response_model=SettingsResponse)
def put_settings(
    payload: SettingsUpdate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    save_user_settings(db, user_id, payload)
    return get_settings_view(user_id, db)


def _portfolio_response(
    records: list[PortfolioAssetRecord],
    market_rows: list[Any] | None = None,
    signal_rows: list[Any] | None = None,
) -> dict[str, Any]:
    market_by_ticker = {row.ticker: row for row in market_rows or []}
    assets = []
    for record in records:
        market_ticker = f"{record.symbol}.KS" if record.market == "KR" and "." not in record.symbol else record.symbol
        assets.append(_portfolio_asset_dict(record, market_by_ticker.get(market_ticker)))
    rates = {"KRW": 1.0, "USD": 1382.0, "TWD": 43.0}
    total_input = sum(asset["quantity"] * asset["averageBuyPrice"] * rates[asset["currency"]] for asset in assets)
    total_current = sum(asset["quantity"] * asset["currentPrice"] * rates[asset["currency"]] for asset in assets)
    industries: dict[str, int] = {}
    for asset in assets:
        industries[asset["industry"]] = industries.get(asset["industry"], 0) + 1
    caution_count = sum(asset["cautionNewsCount"] for asset in assets)
    related_count = sum(asset["relatedNewsCount"] for asset in assets)
    updated_at = max((asset["updatedAt"] for asset in assets), default=_now_label())

    return {
        "summary": {
            "assetCount": len(assets),
            "totalInputAmount": round(total_input, 2),
            "totalCurrentAmount": round(total_current, 2),
            "valuationGap": round(total_current - total_input, 2),
            "valuationGapRate": round((total_current - total_input) / total_input * 100, 2) if total_input else 0,
            "linkedIndustryCount": len(industries),
            "cautionAlertCount": caution_count,
            "normalAlertCount": max(related_count - caution_count, 0),
            "updatedAt": updated_at,
        },
        "assets": assets,
        "industryConnections": [
            {
                "id": hashlib.sha1(industry.encode("utf-8")).hexdigest()[:8],
                "industryName": industry,
                "connectedAssetCount": count,
                "signalLabel": "Caution" if industry == "AI/IT" else "Positive",
            }
            for industry, count in industries.items()
        ],
        "linkedSignals": [_portfolio_signal_dict(row, assets) for row in (signal_rows or [])[:5]],
    }


def _portfolio_asset_dict(record: PortfolioAssetRecord, market_row: Any | None = None) -> dict[str, Any]:
    return {
        "id": record.id,
        "assetName": record.asset_name,
        "symbol": record.symbol,
        "market": record.market,
        "industry": record.industry,
        "quantity": record.quantity,
        "averageBuyPrice": record.average_buy_price,
        "currentPrice": market_row.close if market_row else record.current_price,
        "recentSellPrice": record.recent_sell_price,
        "currency": record.currency,
        "status": record.status,
        "decisionMemo": record.decision_memo,
        "relatedNewsCount": record.related_news_count,
        "cautionNewsCount": record.caution_news_count,
        "updatedAt": (
            market_row.fetched_at.isoformat()
            if market_row and market_row.fetched_at
            else _format_datetime(record.updated_at)
        ),
        "priceDataSource": "real" if market_row else "mock",
        "priceAsOf": market_row.trade_date.isoformat() if market_row else None,
    }


def _portfolio_signal_dict(row: Any, assets: list[dict[str, Any]]) -> dict[str, Any]:
    related = [
        asset
        for asset in assets
        if asset["symbol"] == row.ticker or f"{asset['symbol']}.KS" == row.ticker
    ]
    evidence = row.evidence or {}
    return {
        "id": f"signal-{row.id}",
        "industryName": related[0]["industry"] if related else "Market",
        "time": row.trade_date.isoformat(),
        "title": evidence.get("title") or evidence.get("headline") or f"{row.ticker} market signal",
        "summary": f"{row.signal} · event score {row.event_score:.2f}",
        "relatedAssetCount": len(related),
        "tone": "negative" if row.signal == "RED" else "caution" if row.signal == "YELLOW" else "neutral",
    }


def _format_datetime(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(KST).strftime("%Y.%m.%d %H:%M")


def _load_gdelt_articles(max_records: int = 50) -> list[dict[str, Any]]:
    collector = NewsCollector()
    return collector.deduplicate(collector.collect_from_gdelt(days=1, max_records=max_records))


def _strongest_market_reaction(rows: list[dict[str, Any]]) -> dict[str, float]:
    if not rows:
        return {}
    return max(
        rows,
        key=lambda row: (
            abs(float(row.get("return_1d") or 0)),
            float(row.get("volume_ratio") or 0),
            float(row.get("volatility_ratio") or 0),
        ),
    )


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
        "provider": article.get("provider") or "unknown",
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
        "qualityStatus": article.get("quality_status", "low_confidence"),
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


def _industry_detail(
    summary: dict[str, Any],
    articles: list[dict[str, Any]],
    market_connected: bool,
) -> dict[str, Any]:
    matching_articles = _industry_articles(summary["id"], articles)
    top_news = [
        _to_related_news(index, article)
        for index, article in enumerate(matching_articles[:5], start=1)
    ]
    market_description = (
        "Latest yfinance market reactions are included."
        if market_connected
        else "Stored market reaction data is not available."
    )
    return {
        "industryId": summary["id"],
        "title": f"{summary['name']} detail",
        "score": summary["score"],
        "statusLabel": summary["toneLabel"],
        "description": (
            f"{summary['name']} impact uses filtered matching news. "
            f"{market_description}"
        ),
        "relatedStocks": _related_stocks(summary["id"]),
        "newsCount": summary["newsCount"],
        "averageSentiment": round(summary["score"] / 100, 2),
        "riskPoints": 2 if summary["score"] < 0 else 1,
        "updatedAt": _now_label(),
        "reasons": {
            "positive": ["Filtered industry-matching evidence", "Related market reaction when available"],
            "caution": ["Low-confidence articles are labeled", "Additional source verification recommended"],
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
    quality_status = article.get("quality_status")
    if article.get("provider") == "seed" or quality_status == "seed_fallback":
        score = min(score, 0.5)
    elif quality_status == "low_confidence":
        score = min(score, 0.69)
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
    return any(contains_term(text, keyword) for keyword in keywords)


def _industry_articles(industry_id: str, articles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    mapping = {
        "semiconductor": ["semiconductor", "chip", "export control", "nvidia", "amd", "samsung", "sk hynix"],
        "it": ["ai", "artificial intelligence", "gpu", "nvidia", "amd"],
        "policy": ["policy", "regulation", "export control", "restriction"],
    }
    return [article for article in articles if _mentions(article, mapping.get(industry_id, []))]


def _industry_market_adjustment(market: list[dict[str, Any]], industry_id: str) -> int:
    tickers = {
        "semiconductor": {"NVDA", "AMD", "005930.KS", "000660.KS"},
        "it": {"NVDA", "AMD"},
    }.get(industry_id, set())
    returns = [
        float(row.get("return_1d") or 0)
        for row in market
        if row.get("ticker") in tickers
    ]
    return round(sum(returns) / len(returns) * 100) if returns else 0


def _bounded_score(score: int) -> int:
    return max(-90, min(90, score))


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


def _provider_status(snapshot: PipelineSnapshot, gemini_status: str | None = None) -> dict[str, str]:
    settings = get_settings()
    result = dict(snapshot.provider_status)
    result.update(
        {
            "newsapi": result.get("newsapi", "connected" if settings.news_api_key else "disabled"),
            "guardian": result.get("guardian", "connected" if settings.guardian_api_key else "disabled"),
            "finnhub": result.get("finnhub", "connected" if settings.finnhub_api_key else "disabled"),
            "alphaVantage": "connected" if settings.alpha_vantage_api_key else "disabled",
            "kis": "connected" if settings.kis_app_key and settings.kis_app_secret else "disabled",
            "openai": "connected" if settings.openai_api_key else "disabled",
            "kakao": "connected" if settings.kakao_rest_api_key else "disabled",
        }
    )
    gemini_mapping = {
        "healthy": "connected",
        "cached": "connected",
        "ready": "connected",
        "not_configured": "disabled",
        "rate_limited": "rate_limited",
        "timeout": "timeout",
        "fallback": "fallback",
    }
    result["gemini"] = gemini_mapping.get(gemini_status or "", "error")
    return result


def _provider_health(snapshot: PipelineSnapshot) -> list[dict[str, str]]:
    settings = get_settings()
    status = snapshot.provider_status
    return [
        {"provider": "GDELT", "status": status.get("gdelt", "error"), "message": _status_message(status.get("gdelt", "error")), "lastCheckedAt": snapshot.last_updated},
        {"provider": "NewsAPI", "status": status.get("newsapi", "connected" if settings.news_api_key else "disabled"), "message": _status_message(status.get("newsapi", "disabled"))},
        {"provider": "Guardian", "status": "connected" if settings.guardian_api_key else "disabled", "message": "Configured" if settings.guardian_api_key else "API key pending"},
        {"provider": "Finnhub", "status": "connected" if settings.finnhub_api_key else "disabled", "message": "Configured" if settings.finnhub_api_key else "API key pending"},
        {"provider": "BBC RSS", "status": status.get("bbcrss", "error"), "message": _status_message(status.get("bbcrss", "error")), "lastCheckedAt": snapshot.last_updated},
        {"provider": "Google News RSS", "status": status.get("googlenewsrss", "error"), "message": _status_message(status.get("googlenewsrss", "error")), "lastCheckedAt": snapshot.last_updated},
    ]


def _status_message(status: str) -> str:
    messages = {
        "connected": "Connected",
        "timeout": "Timed out; using stored or fallback data",
        "rate_limited": "Rate limited",
        "disabled": "Not configured",
        "fallback": "Fallback data active",
        "error": "Provider unavailable",
    }
    return messages.get(status, "Provider state unknown")


def _now_label() -> str:
    return datetime.now(timezone.utc).astimezone(KST).strftime("%Y.%m.%d %H:%M")
