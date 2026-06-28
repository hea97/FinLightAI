from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
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
    bbc_rss_url: str = "https://feeds.bbci.co.uk/news/world/rss.xml"
    discord_webhook_url: str | None = None
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from: str | None = None
    alert_email_to: str | None = None
    log_level: str = "INFO"

    min_reliability_score: float = Field(default=0.65, ge=0, le=1)
    min_source_score: float = Field(default=0.8, ge=0, le=1)
    min_keyword_score: int = Field(default=2, ge=0)
    min_content_length: int = Field(default=200, ge=0)
    red_volume_ratio: float = 2.0
    red_sentiment_score: float = -0.3
    volatility_multiplier: float = 2.0

    project_root: Path = Path(__file__).resolve().parents[1]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
