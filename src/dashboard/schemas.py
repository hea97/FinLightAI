from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ApiModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)


class BriefingNews(ApiModel):
    title: str
    source: str
    url: str = ""
    published_at: str = Field(alias="publishedAt")
    reliability_score: float = Field(alias="reliabilityScore")


class BriefingResponse(ApiModel):
    as_of: str = Field(alias="asOf")
    signal: Literal["RED", "YELLOW", "GREEN"]
    risk_score: int = Field(alias="riskScore", ge=0, le=100)
    headline: str
    summary: list[str]
    key_news: list[BriefingNews] = Field(alias="keyNews")
    provider_status: dict[str, str] = Field(alias="providerStatus")


class NewsGuardStats(ApiModel):
    collected_news_count: int = Field(alias="collectedNewsCount")
    trusted_news_count: int = Field(alias="trustedNewsCount")
    watch_news_count: int = Field(alias="watchNewsCount")
    blocked_news_count: int = Field(alias="blockedNewsCount")
    average_reliability_score: float = Field(alias="averageReliabilityScore")
    delta_collected_news_count: int = Field(alias="deltaCollectedNewsCount")


class DistributionItem(ApiModel):
    count: int
    ratio: float


class ReliabilityDistribution(ApiModel):
    trusted: DistributionItem
    watch: DistributionItem
    blocked: DistributionItem


class BlockReason(ApiModel):
    rank: int
    reason: str
    count: int
    ratio: float


class QuickFilter(ApiModel):
    id: str
    label: str
    count: int


class ProviderHealth(ApiModel):
    provider: str
    status: Literal["healthy", "partial", "disabled", "failed"]
    message: str
    last_checked_at: str | None = Field(default=None, alias="lastCheckedAt")


class NewsGuardArticle(ApiModel):
    id: str
    title: str
    source: str
    published_ago: str = Field(alias="publishedAgo")
    summary: str
    reliability_level: Literal["trusted", "watch", "blocked"] = Field(alias="reliabilityLevel")
    reliability_score: float = Field(alias="reliabilityScore")
    impact_score: int = Field(alias="impactScore")
    sentiment_score: float = Field(alias="sentimentScore")
    industries: list[str]
    tags: list[str]
    original_url: str = Field(default="", alias="originalUrl")
    reasons: list[str]


class NewsGuardResponse(ApiModel):
    stats: NewsGuardStats
    distribution: ReliabilityDistribution
    block_reasons: list[BlockReason] = Field(alias="blockReasons")
    quick_filters: list[QuickFilter] = Field(alias="quickFilters")
    provider_health: list[ProviderHealth] = Field(alias="providerHealth")
    articles: list[NewsGuardArticle]


class IndustrySummary(ApiModel):
    id: str
    name: str
    score: int
    tone: Literal["positive", "weak_positive", "neutral", "caution", "negative"]
    tone_label: str = Field(alias="toneLabel")
    news_count: int = Field(alias="newsCount")
    icon: str


class IndustryReasons(ApiModel):
    positive: list[str]
    caution: list[str]


class RelatedNews(ApiModel):
    id: str
    rank: int
    title: str
    source: str
    sentiment_label: str = Field(alias="sentimentLabel")
    impact_score: float = Field(alias="impactScore")


class IndustryDetail(ApiModel):
    industry_id: str = Field(alias="industryId")
    title: str
    score: int
    status_label: str = Field(alias="statusLabel")
    description: str
    related_stocks: list[str] = Field(alias="relatedStocks")
    news_count: int = Field(alias="newsCount")
    average_sentiment: float = Field(alias="averageSentiment")
    risk_points: int = Field(alias="riskPoints")
    updated_at: str = Field(alias="updatedAt")
    reasons: IndustryReasons
    top_news: list[RelatedNews] = Field(alias="topNews")


class IndustryImpactResponse(ApiModel):
    industries: list[IndustrySummary]
    details: dict[str, IndustryDetail]


AssetMarket = Literal["KR", "US", "TW", "OTHER"]
AssetCurrency = Literal["KRW", "USD", "TWD"]
AssetStatus = Literal["holding", "partial_sold", "watching"]


class PortfolioAssetInput(ApiModel):
    asset_name: str = Field(alias="assetName", min_length=1, max_length=120)
    symbol: str = Field(min_length=1, max_length=30)
    market: AssetMarket
    industry: str = Field(min_length=1, max_length=80)
    quantity: float = Field(ge=0)
    average_buy_price: float = Field(alias="averageBuyPrice", ge=0)
    current_price: float = Field(alias="currentPrice", ge=0)
    recent_sell_price: float | None = Field(default=None, alias="recentSellPrice", ge=0)
    currency: AssetCurrency
    status: AssetStatus = "holding"
    decision_memo: str | None = Field(default=None, alias="decisionMemo", max_length=1000)


class PortfolioAsset(PortfolioAssetInput):
    id: str
    related_news_count: int = Field(default=0, alias="relatedNewsCount")
    caution_news_count: int = Field(default=0, alias="cautionNewsCount")
    updated_at: str = Field(alias="updatedAt")


class PortfolioSummary(ApiModel):
    asset_count: int = Field(alias="assetCount")
    total_input_amount: float = Field(alias="totalInputAmount")
    total_current_amount: float = Field(alias="totalCurrentAmount")
    valuation_gap: float = Field(alias="valuationGap")
    valuation_gap_rate: float = Field(alias="valuationGapRate")
    linked_industry_count: int = Field(alias="linkedIndustryCount")
    caution_alert_count: int = Field(alias="cautionAlertCount")
    normal_alert_count: int = Field(alias="normalAlertCount")
    updated_at: str = Field(alias="updatedAt")


class IndustryConnection(ApiModel):
    id: str
    industry_name: str = Field(alias="industryName")
    connected_asset_count: int = Field(alias="connectedAssetCount")
    signal_label: str = Field(alias="signalLabel")


class LinkedSignal(ApiModel):
    id: str
    industry_name: str = Field(alias="industryName")
    time: str
    title: str
    summary: str
    related_asset_count: int = Field(alias="relatedAssetCount")
    tone: Literal["positive", "neutral", "caution", "negative"]


class PortfolioResponse(ApiModel):
    summary: PortfolioSummary
    assets: list[PortfolioAsset]
    industry_connections: list[IndustryConnection] = Field(alias="industryConnections")
    linked_signals: list[LinkedSignal] = Field(alias="linkedSignals")


class KakaoAlertRule(ApiModel):
    id: str
    icon: str
    label: str
    enabled: bool


class KakaoRuleUpdate(ApiModel):
    enabled: bool


class KakaoQuestion(ApiModel):
    id: str
    label: str


class KakaoIntegration(ApiModel):
    id: str
    icon: str
    label: str
    value: str
    health: str


class KakaoHistory(ApiModel):
    id: str
    sent_at: str = Field(alias="sentAt")
    type: str
    trigger: str
    status: str
    tone: str


class KakaoFlowStep(ApiModel):
    id: str
    icon: str
    title: str
    subtitle: str


class KakaoPreviewMessage(ApiModel):
    id: str
    sender: Literal["bot", "user"]
    time: str
    body: str
    action_label: str | None = Field(default=None, alias="actionLabel")


class KakaoAlertResponse(ApiModel):
    badges: list[str]
    rules: list[KakaoAlertRule]
    questions: list[KakaoQuestion]
    integrations: list[KakaoIntegration]
    history: list[KakaoHistory]
    flow: list[KakaoFlowStep]
    preview_messages: list[KakaoPreviewMessage] = Field(alias="previewMessages")


class MyPageProfile(ApiModel):
    username: str
    email: str
    joined_at: str = Field(alias="joinedAt")
    last_login_at: str = Field(alias="lastLoginAt")
    language: str
    alert_channel: str = Field(alias="alertChannel")
    channel_connected: bool = Field(alias="channelConnected")


class MyPageMetric(ApiModel):
    id: str
    icon: str
    label: str
    value: str
    helper: str
    delta: str | None = None


class MyPageAlertSetting(ApiModel):
    id: str
    icon: str
    title: str
    description: str
    enabled: bool
    emphasis: bool | None = None


class MyPageConnection(ApiModel):
    id: str
    icon: str
    label: str
    status: str
    status_label: str = Field(alias="statusLabel")


class MyPageActivity(ApiModel):
    id: str
    icon: str
    title: str
    timestamp: str


class MyPageShortcut(ApiModel):
    id: str
    icon: str
    title: str
    description: str


class MyPageGuide(ApiModel):
    title: str
    body: str
    cta_label: str = Field(alias="ctaLabel")


class MyPageResponse(ApiModel):
    profile: MyPageProfile
    metrics: list[MyPageMetric]
    alert_settings: list[MyPageAlertSetting] = Field(alias="alertSettings")
    interests: list[str]
    connections: list[MyPageConnection]
    activities: list[MyPageActivity]
    shortcuts: list[MyPageShortcut]
    guide: MyPageGuide


class MyPageUpdate(ApiModel):
    alert_settings: list[MyPageAlertSetting] | None = Field(default=None, alias="alertSettings")
    interests: list[str] | None = None


class SettingsStatusCard(ApiModel):
    id: str
    icon: str
    title: str
    value: str
    description: str
    tone: str


class DataCollectionSettings(ApiModel):
    news_interval: str = Field(alias="newsInterval")
    news_retention: str = Field(alias="newsRetention")
    market_data_retention: str = Field(alias="marketDataRetention")
    keywords: list[str]
    low_trust_filter: bool = Field(alias="lowTrustFilter")
    duplicate_news_removal: bool = Field(alias="duplicateNewsRemoval")


class NewsGuardSettings(ApiModel):
    minimum_source_trust: float = Field(alias="minimumSourceTrust", ge=0, le=1)
    sensational_threshold: float = Field(alias="sensationalThreshold", ge=0, le=1)
    minimum_report_score: int = Field(alias="minimumReportScore", ge=0)
    sensitivity: str
    mode: Literal["basic", "strict", "flexible"]


class NotificationSetting(ApiModel):
    id: str
    label: str
    description: str
    enabled: bool


class KakaoChannelSettings(ApiModel):
    bot_name: str = Field(alias="botName")
    status_label: str = Field(alias="statusLabel")
    description: str


class ApiConnection(ApiModel):
    id: str
    name: str
    connected: bool


class DisplaySettings(ApiModel):
    language: str
    theme: str
    number_format: str = Field(alias="numberFormat")
    timezone: str


class MiscSettings(ApiModel):
    search_log_retention: str = Field(alias="searchLogRetention")
    session_timeout: str = Field(alias="sessionTimeout")
    kakao_notice: str = Field(alias="kakaoNotice")


class SettingsResponse(ApiModel):
    status_cards: list[SettingsStatusCard] = Field(alias="statusCards")
    data_collection: DataCollectionSettings = Field(alias="dataCollection")
    news_guard: NewsGuardSettings = Field(alias="newsGuard")
    notifications: list[NotificationSetting]
    kakao_channel: KakaoChannelSettings = Field(alias="kakaoChannel")
    api_connections: list[ApiConnection] = Field(alias="apiConnections")
    display: DisplaySettings
    misc: MiscSettings


class SettingsUpdate(ApiModel):
    data_collection: DataCollectionSettings = Field(alias="dataCollection")
    news_guard: NewsGuardSettings = Field(alias="newsGuard")
    notifications: list[NotificationSetting]
    display: DisplaySettings
    misc: MiscSettings
