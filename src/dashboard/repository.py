from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.dashboard.models import KakaoAlertRule, PortfolioAsset, User, UserSettings
from src.dashboard.schemas import PortfolioAssetInput, SettingsUpdate


DEFAULT_ALERT_SETTINGS = [
    {"id": "kakao", "icon": "K", "title": "Kakao alerts", "description": "Enabled after Kakao API setup.", "enabled": False},
    {"id": "daily-briefing", "icon": "DAY", "title": "Daily AI briefing", "description": "Summarizes key news every day.", "enabled": True},
    {"id": "red-signal", "icon": "RED", "title": "RED signal alert", "description": "Shows high-risk signals immediately.", "enabled": True, "emphasis": True},
    {"id": "portfolio-news", "icon": "PORT", "title": "Portfolio news", "description": "Tracks watched assets.", "enabled": True},
    {"id": "news-guard", "icon": "NEWS", "title": "News Guard", "description": "Shows low-trust news caution signals.", "enabled": True},
]

DEFAULT_KAKAO_RULES = [
    ("market-risk", "RISK", "Market risk score >= 70"),
    ("industry-impact", "IND", "Watched industry impact >= 60"),
    ("low-trust-news", "NEWS", "Low-trust news detected"),
    ("portfolio-news", "PORT", "Portfolio-related news"),
    ("red-signal", "RED", "RED signal created"),
    ("daily-briefing", "DAY", "Daily AI briefing"),
]


class DuplicatePortfolioAssetError(Exception):
    pass


def ensure_user(db: Session, user_id: str) -> User:
    user = db.get(User, user_id)
    if user:
        return user

    user = User(
        id=user_id,
        username="finlight_user" if user_id == "demo-user" else user_id,
        email="finlight@example.com" if user_id == "demo-user" else f"{user_id}@local.finlight",
        interests=["Semiconductor", "AI", "Policy/Regulation"],
        alert_settings=DEFAULT_ALERT_SETTINGS,
    )
    db.add(user)
    db.flush()
    _seed_assets(db, user_id)
    _seed_kakao_rules(db, user_id)
    db.commit()
    db.refresh(user)
    return user


def list_assets(db: Session, user_id: str) -> list[PortfolioAsset]:
    ensure_user(db, user_id)
    query = select(PortfolioAsset).where(PortfolioAsset.user_id == user_id).order_by(PortfolioAsset.updated_at.desc())
    return list(db.scalars(query))


def create_asset(db: Session, user_id: str, payload: PortfolioAssetInput) -> PortfolioAsset:
    ensure_user(db, user_id)
    asset = PortfolioAsset(
        id=f"asset-{uuid4().hex[:12]}",
        user_id=user_id,
        **payload.model_dump(),
    )
    db.add(asset)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicatePortfolioAssetError from exc
    db.refresh(asset)
    return asset


def update_asset(db: Session, user_id: str, asset_id: str, payload: PortfolioAssetInput) -> PortfolioAsset | None:
    asset = db.scalar(select(PortfolioAsset).where(PortfolioAsset.id == asset_id, PortfolioAsset.user_id == user_id))
    if not asset:
        return None
    for key, value in payload.model_dump().items():
        setattr(asset, key, value)
    asset.updated_at = datetime.now(timezone.utc)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicatePortfolioAssetError from exc
    db.refresh(asset)
    return asset


def delete_asset(db: Session, user_id: str, asset_id: str) -> bool:
    asset = db.scalar(select(PortfolioAsset).where(PortfolioAsset.id == asset_id, PortfolioAsset.user_id == user_id))
    if not asset:
        return False
    db.delete(asset)
    db.commit()
    return True


def get_kakao_rules(db: Session, user_id: str) -> list[KakaoAlertRule]:
    ensure_user(db, user_id)
    query = select(KakaoAlertRule).where(KakaoAlertRule.user_id == user_id).order_by(KakaoAlertRule.rule_id)
    return list(db.scalars(query))


def update_kakao_rule(db: Session, user_id: str, rule_id: str, enabled: bool) -> KakaoAlertRule | None:
    rule = db.scalar(select(KakaoAlertRule).where(KakaoAlertRule.user_id == user_id, KakaoAlertRule.rule_id == rule_id))
    if not rule:
        return None
    rule.enabled = enabled
    db.commit()
    db.refresh(rule)
    return rule


def update_mypage(db: Session, user_id: str, alert_settings: list[dict] | None, interests: list[str] | None) -> User:
    user = ensure_user(db, user_id)
    if alert_settings is not None:
        user.alert_settings = alert_settings
    if interests is not None:
        user.interests = list(dict.fromkeys(item.strip() for item in interests if item.strip()))
    db.commit()
    db.refresh(user)
    return user


def get_user_settings(db: Session, user_id: str, default_payload: dict) -> dict:
    ensure_user(db, user_id)
    stored = db.get(UserSettings, user_id)
    if stored:
        return stored.payload
    stored = UserSettings(user_id=user_id, payload=default_payload)
    db.add(stored)
    db.commit()
    return stored.payload


def save_user_settings(db: Session, user_id: str, payload: SettingsUpdate) -> dict:
    ensure_user(db, user_id)
    data = payload.model_dump(by_alias=True)
    stored = db.get(UserSettings, user_id)
    if stored:
        stored.payload = data
    else:
        db.add(UserSettings(user_id=user_id, payload=data))
    db.commit()
    return data


def _seed_assets(db: Session, user_id: str) -> None:
    assets = [
        PortfolioAsset(
            id=f"{user_id}-samsung",
            user_id=user_id,
            asset_name="Samsung Electronics",
            symbol="005930",
            market="KR",
            industry="Semiconductor",
            quantity=32,
            average_buy_price=71800,
            current_price=74200,
            recent_sell_price=75600,
            currency="KRW",
            status="holding",
            decision_memo="KIS price data is pending. Temporary reference price is displayed.",
            related_news_count=12,
            caution_news_count=2,
        ),
        PortfolioAsset(
            id=f"{user_id}-nvidia",
            user_id=user_id,
            asset_name="NVIDIA",
            symbol="NVDA",
            market="US",
            industry="AI/IT",
            quantity=5,
            average_buy_price=124.2,
            current_price=132.8,
            currency="USD",
            status="holding",
            decision_memo="Finnhub or Alpha Vantage can replace this with live or delayed price data.",
            related_news_count=14,
            caution_news_count=3,
        ),
    ]
    db.add_all(assets)


def _seed_kakao_rules(db: Session, user_id: str) -> None:
    db.add_all(
        KakaoAlertRule(user_id=user_id, rule_id=rule_id, icon=icon, label=label, enabled=True)
        for rule_id, icon, label in DEFAULT_KAKAO_RULES
    )
