from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    frontend_url: str | None = None
    backend_url: str | None = None
    database_url: str = "sqlite:///./data/finlightai.db"
    cors_origins: str = "http://127.0.0.1:5173,http://localhost:5173"
    gdelt_base_url: str = "https://api.gdeltproject.org/api/v2/doc/doc"
    external_api_timeout_seconds: float = Field(default=10, gt=0, le=60)
    external_api_cache_seconds: int = Field(default=300, ge=0, le=3600)
    news_api_key: str | None = None
    guardian_api_key: str | None = None
    finnhub_api_key: str | None = None
    alpha_vantage_api_key: str | None = None
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"
    openai_api_key: str | None = None
    opendart_api_key: str | None = None
    kis_app_key: str | None = None
    kis_app_secret: str | None = None
    kis_account_no: str | None = None
    kakao_rest_api_key: str | None = None
    kakao_client_secret: str | None = None
    kakao_redirect_uri: str | None = None
    kakao_channel_id: str | None = None
    google_client_id: str | None = None
    google_client_secret: str | None = None
    google_redirect_uri: str | None = None
    jwt_secret_key: str | None = None
    jwt_expire_minutes: int = 1440
    auth_cookie_name: str = "finlight_session"
    auth_cookie_domain: str | None = None
    auth_cookie_samesite: Literal["lax", "strict", "none"] | None = None
    auth_cookie_secure: bool | None = None
    oauth_state_cookie_name: str = "finlight_oauth_state"
    bbc_rss_url: str = "https://feeds.bbci.co.uk/news/world/rss.xml"
    google_news_rss_url: str = "https://news.google.com/rss/search"
    discord_webhook_url: str | None = None
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from: str | None = None
    alert_email_to: str | None = None
    email_provider: Literal["smtp", "resend"] = "resend"
    resend_api_key: str | None = None
    email_webhook_secret: str | None = None
    notification_secret: str | None = None
    notification_token_secret: str | None = None
    n8n_kakao_webhook_url: str | None = None
    n8n_webhook_token: str | None = None
    kakao_channel_approved: bool = False
    log_level: str = "INFO"

    min_reliability_score: float = Field(default=0.65, ge=0, le=1)
    min_source_score: float = Field(default=0.8, ge=0, le=1)
    min_keyword_score: int = Field(default=2, ge=0)
    min_content_length: int = Field(default=200, ge=0)
    min_rss_content_length: int = Field(default=60, ge=0)
    red_volume_ratio: float = 2.0
    red_sentiment_score: float = -0.3
    volatility_multiplier: float = 2.0

    project_root: Path = Path(__file__).resolve().parents[1]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    def cors_origin_list(self) -> list[str]:
        configured_origins = [
            origin.strip().rstrip("/")
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]
        optional_origins = [
            origin.strip().rstrip("/")
            for origin in (self.frontend_url,)
            if origin and origin.strip()
        ]
        return list(dict.fromkeys([*configured_origins, *optional_origins]))

    def is_development(self) -> bool:
        return self.app_env.lower() in {"local", "development", "dev", "test"}

    def session_cookie_secure(self) -> bool:
        if not self.is_development():
            return True
        if self.auth_cookie_secure is not None:
            return self.auth_cookie_secure
        return False

    def session_cookie_samesite(self) -> Literal["lax", "strict", "none"]:
        if not self.is_development():
            return "none"
        if self.auth_cookie_samesite is not None:
            return self.auth_cookie_samesite
        return "lax"


@lru_cache
def get_settings() -> Settings:
    return Settings()
