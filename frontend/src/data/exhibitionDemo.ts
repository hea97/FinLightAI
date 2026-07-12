import type { AuthMeResponse } from "../types/auth";
import type { BriefingResponse } from "../types/briefing";
import type { IndustryImpactResponse } from "../types/industryImpact";
import type { MyPageResponse } from "../types/myPage";
import type { NewsGuardFilter, NewsGuardViewModel } from "../types/newsGuard";
import type { PortfolioResponse } from "../types/portfolio";
import type { SettingsResponse } from "../types/settings";

export const exhibitionDemoMetadata = {
  dataSource: "exhibition_demo" as const,
  isDemo: true,
  isFallback: false,
  lastUpdated: "2026-07-13 09:00 KST",
  providers: ["전시용 샘플 데이터"],
  warnings: [
    "실시간 API 데이터가 아닌 전시용 샘플 데이터입니다.",
    "FinLightAI의 신호와 샘플 데이터는 투자 추천이나 매수/매도 지시가 아닌 서비스 시연 정보입니다.",
  ],
};

export const exhibitionDemoUser: AuthMeResponse = {
  authenticated: true,
  user: {
    id: "exhibition-demo-user",
    email: "demo@finlightai.local",
    nickname: "FinLightAI 데모 사용자",
    profileImageUrl: null,
    provider: "exhibition_demo",
  },
};

export const exhibitionDemoBriefing: BriefingResponse = {
  ...exhibitionDemoMetadata,
  asOf: "2026-07-13T09:00:00+09:00",
  signal: "YELLOW",
  riskScore: 68,
  headline: "AI 반도체 수출 규제와 주요 기술기업 실적 발표가 동시에 주목받는 전시용 브리핑입니다.",
  summary: [
    "AI 반도체 수출 규제 이슈로 변동성이 확대될 수 있는 상황을 가정한 샘플 브리핑입니다.",
    "관련 산업은 AI, 반도체, 로봇이며 실제 속보나 실시간 수치가 아닙니다.",
    "RED 1건, YELLOW 3건, GREEN 4건의 전시용 신호를 사용합니다.",
  ],
  keyNews: [
    {
      title: "전시 샘플: AI 반도체 수출 규제 추가 검토",
      source: "전시용 샘플",
      url: "",
      publishedAt: "2026-07-13 08:30 KST",
      reliabilityScore: 0.86,
    },
    {
      title: "전시 샘플: 주요 반도체 기업, AI 데이터센터 투자 전망 발표",
      source: "전시용 샘플",
      url: "",
      publishedAt: "2026-07-13 08:10 KST",
      reliabilityScore: 0.82,
    },
  ],
  providerStatus: { "Exhibition Demo": "demo" },
};

export const exhibitionDemoNewsGuard: NewsGuardViewModel = {
  ...exhibitionDemoMetadata,
  stats: {
    collectedNewsCount: 8,
    trustedNewsCount: 3,
    watchNewsCount: 3,
    blockedNewsCount: 2,
    averageReliabilityScore: 72,
    deltaCollectedNewsCount: 8,
  },
  distribution: {
    trusted: { count: 3, ratio: 37.5 },
    watch: { count: 3, ratio: 37.5 },
    blocked: { count: 2, ratio: 25 },
  },
  blockReasons: [
    { rank: 1, reason: "출처가 확인되지 않은 인수설", count: 1, ratio: 50 },
    { rank: 2, reason: "과거 기사를 새 제목으로 재공개", count: 1, ratio: 50 },
  ],
  quickFilters: [
    { id: "ai", label: "AI", count: 4 },
    { id: "semiconductor", label: "Semiconductor", count: 4 },
    { id: "policy", label: "Policy", count: 2 },
    { id: "portfolio", label: "Portfolio", count: 3 },
  ],
  providerHealth: [
    { provider: "Exhibition Demo", status: "connected", message: "전시용 샘플 데이터", lastCheckedAt: "2026-07-13 09:00 KST" },
  ],
  articles: [
    {
      id: "demo-news-1",
      title: "전시 샘플: 한국 AI 반도체 수출 규제 추가 검토",
      source: "전시용 샘플",
      provider: "Exhibition Demo",
      publishedAgo: "30분 전",
      summary: "정책 변화가 AI 반도체와 데이터센터 공급망에 미칠 영향을 보여주기 위한 샘플 기사입니다.",
      reliabilityLevel: "trusted",
      reliabilityScore: 88,
      impactScore: 81,
      sentimentScore: -0.22,
      industries: ["AI", "Semiconductor", "Policy"],
      tags: ["수출 규제", "AI 반도체"],
      originalUrl: undefined,
      reasons: ["전시용 샘플 출처", "정책 영향 예시"],
      qualityStatus: "verified",
    },
    {
      id: "demo-news-2",
      title: "전시 샘플: 주요 반도체 기업, AI 데이터센터 투자 전망 발표",
      source: "전시용 샘플",
      provider: "Exhibition Demo",
      publishedAgo: "45분 전",
      summary: "AI 인프라 투자 기대가 포트폴리오 관련 종목에 연결되는 흐름을 시연합니다.",
      reliabilityLevel: "trusted",
      reliabilityScore: 84,
      impactScore: 74,
      sentimentScore: 0.36,
      industries: ["AI", "Semiconductor"],
      tags: ["데이터센터", "실적"],
      reasons: ["샘플 기준 시각 고정", "관련 산업 매핑"],
      qualityStatus: "verified",
    },
    {
      id: "demo-news-3",
      title: "전시 샘플: 로봇 산업 지원 정책 논의 확대",
      source: "전시용 샘플",
      provider: "Exhibition Demo",
      publishedAgo: "1시간 전",
      summary: "정책 기대가 로봇 산업 점수에 반영되는 예시입니다.",
      reliabilityLevel: "watch",
      reliabilityScore: 69,
      impactScore: 55,
      sentimentScore: 0.14,
      industries: ["Robotics", "Policy"],
      tags: ["로봇", "정책"],
      reasons: ["정책 일정 불확실성", "샘플 기사"],
      qualityStatus: "verified",
    },
    {
      id: "demo-news-4",
      title: "전시 샘플: 출처가 확인되지 않은 AI 기업 인수설 확산",
      source: "전시용 샘플",
      provider: "Exhibition Demo",
      publishedAgo: "1시간 전",
      summary: "낮은 신뢰도 뉴스를 차단하는 기능을 보여주기 위한 샘플입니다.",
      reliabilityLevel: "blocked",
      reliabilityScore: 28,
      impactScore: 47,
      sentimentScore: 0.05,
      industries: ["AI"],
      tags: ["인수설", "미확인"],
      reasons: ["원문 출처 불명", "확인되지 않은 주장"],
      qualityStatus: "low_confidence",
    },
    {
      id: "demo-news-5",
      title: "전시 샘플: 과거 반도체 뉴스를 새 제목으로 재공개",
      source: "전시용 샘플",
      provider: "Exhibition Demo",
      publishedAgo: "2시간 전",
      summary: "중복/재게시 의심 뉴스를 차단 상태로 분류하는 샘플입니다.",
      reliabilityLevel: "blocked",
      reliabilityScore: 22,
      impactScore: 33,
      sentimentScore: -0.11,
      industries: ["Semiconductor"],
      tags: ["중복", "재공개"],
      reasons: ["과거 기사 재가공", "원문 기준 시각 불명"],
      qualityStatus: "low_confidence",
    },
    {
      id: "demo-news-6",
      title: "전시 샘플: GPU 공급 병목 완화 가능성 점검",
      source: "전시용 샘플",
      provider: "Exhibition Demo",
      publishedAgo: "3시간 전",
      summary: "공급망 이슈와 포트폴리오 종목 연결을 보여주는 전시용 뉴스입니다.",
      reliabilityLevel: "watch",
      reliabilityScore: 66,
      impactScore: 62,
      sentimentScore: 0.18,
      industries: ["AI", "Semiconductor"],
      tags: ["GPU", "공급망"],
      reasons: ["일부 수치 미확정", "샘플 데이터"],
      qualityStatus: "verified",
    },
    {
      id: "demo-news-7",
      title: "전시 샘플: AI 서버 수요 전망 상향",
      source: "전시용 샘플",
      provider: "Exhibition Demo",
      publishedAgo: "4시간 전",
      summary: "AI 서버 수요 기대가 신뢰 뉴스로 분류되는 흐름을 보여주는 전시용 기사입니다.",
      reliabilityLevel: "trusted",
      reliabilityScore: 82,
      impactScore: 69,
      sentimentScore: 0.31,
      industries: ["AI", "Semiconductor"],
      tags: ["AI 서버", "수요"],
      reasons: ["전시용 샘플 출처", "관련 산업 매핑"],
      qualityStatus: "verified",
    },
    {
      id: "demo-news-8",
      title: "전시 샘플: 정책 발표 전 반도체 변동성 확대",
      source: "전시용 샘플",
      provider: "Exhibition Demo",
      publishedAgo: "5시간 전",
      summary: "정책 발표 전 변동성 확대를 주의 상태로 분류하는 전시용 기사입니다.",
      reliabilityLevel: "watch",
      reliabilityScore: 63,
      impactScore: 58,
      sentimentScore: -0.09,
      industries: ["Policy", "Semiconductor"],
      tags: ["정책", "변동성"],
      reasons: ["발표 전 정보", "샘플 데이터"],
      qualityStatus: "verified",
    },
  ],
};

export function getExhibitionDemoNewsGuard(filter: NewsGuardFilter): NewsGuardViewModel {
  if (filter === "all") return exhibitionDemoNewsGuard;
  return {
    ...exhibitionDemoNewsGuard,
    articles: exhibitionDemoNewsGuard.articles.filter((article) => article.reliabilityLevel === filter),
  };
}

export const exhibitionDemoIndustryImpact: IndustryImpactResponse = {
  ...exhibitionDemoMetadata,
  industries: [
    { id: "ai", name: "AI", score: 72, tone: "caution", toneLabel: "YELLOW", newsCount: 4, icon: "AI" },
    { id: "semiconductor", name: "Semiconductor", score: 64, tone: "caution", toneLabel: "YELLOW", newsCount: 5, icon: "CHIP" },
    { id: "robotics", name: "Robotics", score: 58, tone: "positive", toneLabel: "GREEN", newsCount: 2, icon: "BOT" },
    { id: "policy", name: "Policy", score: 79, tone: "negative", toneLabel: "RED", newsCount: 3, icon: "LAW" },
  ],
  details: {
    ai: {
      industryId: "ai",
      title: "AI",
      score: 72,
      statusLabel: "YELLOW",
      description: "AI 데이터센터 투자 기대와 수출 규제 리스크가 동시에 반영된 전시용 상태 점수입니다.",
      relatedStocks: ["NVDA", "MSFT"],
      newsCount: 4,
      averageSentiment: 0.18,
      riskPoints: 3,
      updatedAt: "2026-07-13 09:00 KST",
      reasons: { positive: ["데이터센터 투자 전망"], caution: ["수출 규제 검토", "실적 발표 전 변동성"] },
      topNews: [
        { id: "ai-news-1", rank: 1, title: "전시 샘플: AI 데이터센터 투자 전망 발표", source: "전시용 샘플", sentimentLabel: "긍정" as never, impactScore: 74 },
      ],
    },
    semiconductor: {
      industryId: "semiconductor",
      title: "Semiconductor",
      score: 64,
      statusLabel: "YELLOW",
      description: "AI 반도체 수요와 정책 불확실성이 함께 움직이는 전시용 점수입니다.",
      relatedStocks: ["NVDA", "AMD", "005930.KS", "000660.KS"],
      newsCount: 4,
      averageSentiment: 0.06,
      riskPoints: 3,
      updatedAt: "2026-07-13 09:00 KST",
      reasons: { positive: ["AI 가속기 수요"], caution: ["수출 규제", "공급망 병목"] },
      topNews: [
        { id: "semi-news-1", rank: 1, title: "전시 샘플: AI 반도체 수출 규제 추가 검토", source: "전시용 샘플", sentimentLabel: "중립" as never, impactScore: 81 },
      ],
    },
    robotics: {
      industryId: "robotics",
      title: "Robotics",
      score: 58,
      statusLabel: "GREEN",
      description: "로봇 산업 지원 정책 논의를 가정한 전시용 샘플입니다.",
      relatedStocks: ["sample only"],
      newsCount: 2,
      averageSentiment: 0.14,
      riskPoints: 1,
      updatedAt: "2026-07-13 09:00 KST",
      reasons: { positive: ["정책 지원 기대"], caution: ["상용화 일정 불확실"] },
      topNews: [
        { id: "robot-news-1", rank: 1, title: "전시 샘플: 로봇 산업 지원 정책 논의 확대", source: "전시용 샘플", sentimentLabel: "긍정" as never, impactScore: 55 },
      ],
    },
    policy: {
      industryId: "policy",
      title: "Policy",
      score: 79,
      statusLabel: "RED",
      description: "AI·반도체 관련 정책 이벤트를 강조하기 위한 전시용 위험 점수입니다.",
      relatedStocks: ["AI·반도체 관련 샘플"],
      newsCount: 2,
      averageSentiment: -0.22,
      riskPoints: 4,
      updatedAt: "2026-07-13 09:00 KST",
      reasons: { positive: ["정책 명확화 가능성"], caution: ["규제 검토", "지역별 기준 차이"] },
      topNews: [
        { id: "policy-news-1", rank: 1, title: "전시 샘플: 수출 규제 추가 검토", source: "전시용 샘플", sentimentLabel: "부정" as never, impactScore: 81 },
      ],
    },
  },
};

export const exhibitionDemoPortfolio: PortfolioResponse = {
  summary: {
    assetCount: 4,
    totalInputAmount: 46390000,
    totalCurrentAmount: 49880000,
    valuationGap: 3490000,
    valuationGapRate: 7.52,
    linkedIndustryCount: 2,
    cautionAlertCount: 3,
    normalAlertCount: 5,
    updatedAt: "2026-07-13 09:00 KST",
  },
  assets: [
    { id: "demo-nvda", assetName: "NVIDIA", symbol: "NVDA", market: "US", industry: "Semiconductor", quantity: 12, averageBuyPrice: 118, currentPrice: 131, currency: "USD", status: "holding", relatedNewsCount: 3, cautionNewsCount: 1, updatedAt: "2026-07-13 09:00 KST", priceDataSource: "mock", priceProvider: "Exhibition Demo", priceStatusLabel: "전시용 샘플 가격" },
    { id: "demo-amd", assetName: "AMD", symbol: "AMD", market: "US", industry: "Semiconductor", quantity: 18, averageBuyPrice: 142, currentPrice: 149, currency: "USD", status: "holding", relatedNewsCount: 2, cautionNewsCount: 1, updatedAt: "2026-07-13 09:00 KST", priceDataSource: "mock", priceProvider: "Exhibition Demo", priceStatusLabel: "전시용 샘플 가격" },
    { id: "demo-samsung", assetName: "삼성전자", symbol: "005930.KS", market: "KR", industry: "Semiconductor", quantity: 40, averageBuyPrice: 73000, currentPrice: 75800, currency: "KRW", status: "holding", relatedNewsCount: 2, cautionNewsCount: 1, updatedAt: "2026-07-13 09:00 KST", priceDataSource: "mock", priceProvider: "Exhibition Demo", priceStatusLabel: "전시용 샘플 가격" },
    { id: "demo-hynix", assetName: "SK하이닉스", symbol: "000660.KS", market: "KR", industry: "Semiconductor", quantity: 15, averageBuyPrice: 221000, currentPrice: 234000, currency: "KRW", status: "watching", relatedNewsCount: 1, cautionNewsCount: 0, updatedAt: "2026-07-13 09:00 KST", priceDataSource: "mock", priceProvider: "Exhibition Demo", priceStatusLabel: "전시용 샘플 가격" },
  ],
  industryConnections: [
    { id: "semiconductor", industryName: "Semiconductor", connectedAssetCount: 4, signalLabel: "주의" as never },
  ],
  linkedSignals: [
    { id: "demo-signal-1", industryName: "Semiconductor", time: "09:00", title: "전시 샘플: AI 반도체 규제 이슈", summary: "샘플 포트폴리오 보유 종목 4개와 연결된 전시용 신호입니다.", relatedAssetCount: 4, tone: "caution" },
  ],
};

export const exhibitionDemoMyPage: MyPageResponse = {
  profile: {
    username: "FinLightAI 데모 사용자",
    email: "demo@finlightai.local",
    joinedAt: "2026-07-13",
    lastLoginAt: "2026-07-13 09:00 KST",
    language: "한국어" as never,
    alertChannel: "이메일 알림 데모 활성화",
    channelConnected: true,
  },
  metrics: [
    { id: "markets", icon: "MK", label: "관심 시장", value: "한국, 미국", helper: "전시용 샘플" },
    { id: "industries", icon: "IN", label: "관심 산업", value: "AI, 반도체, 로봇", helper: "샘플 기준" },
    { id: "assets", icon: "AS", label: "관심 자산", value: "4", helper: "샘플 포트폴리오" },
  ],
  alertSettings: [
    { id: "email", icon: "EM", title: "이메일 알림 데모 활성화", description: "실제 메일 발송 상태가 아닌 전시용 상태입니다.", enabled: true, emphasis: true },
    { id: "daily-briefing", icon: "DB", title: "일일 요약", description: "전시용 설정", enabled: true },
    { id: "red-signal", icon: "RD", title: "RED 즉시 알림", description: "전시용 설정", enabled: true },
  ],
  interests: ["한국", "미국", "AI", "반도체", "로봇"],
  connections: [
    { id: "demo-user", icon: "DU", label: "데모 사용자", status: "connected", statusLabel: "전시 모드" },
    { id: "email", icon: "EM", label: "이메일 알림", status: "normal", statusLabel: "데모 활성화" },
  ],
  activities: [
    { id: "activity-1", icon: "BR", title: "전시 샘플 브리핑 확인", timestamp: "2026-07-13 09:00 KST" },
    { id: "activity-2", icon: "PF", title: "샘플 포트폴리오 조회", timestamp: "2026-07-13 09:00 KST" },
  ],
  shortcuts: [
    { id: "portfolio", icon: "PF", title: "포트폴리오", description: "샘플 보유 자산 확인" },
    { id: "guard", icon: "NG", title: "뉴스 가드", description: "샘플 뉴스 신뢰도 확인" },
    { id: "industry", icon: "IM", title: "산업 영향도", description: "전시용 산업 점수 확인" },
  ],
  guide: {
    title: "전시용 데모 사용자",
    body: "실제 계정이나 메일 구독 상태가 아닌 전시용 데모 사용자입니다. backend DB 또는 Google OAuth session을 생성하지 않는 frontend-only demo user 상태입니다.",
    ctaLabel: "데모 화면 확인",
  },
};

export const exhibitionDemoSettings: SettingsResponse = {
  statusCards: [
    { id: "demo", icon: "DM", title: "전시 모드", value: "활성", description: "브라우저 localStorage에만 저장됩니다.", tone: "connected" },
    { id: "email", icon: "EM", title: "이메일 알림", value: "데모", description: "실제 메일 발송 상태가 아닙니다.", tone: "warning" },
  ],
  dataCollection: {
    newsInterval: "전시용 고정",
    newsRetention: "샘플 기준",
    marketDataRetention: "샘플 기준",
    keywords: ["AI", "반도체", "로봇", "정책"],
    lowTrustFilter: true,
    duplicateNewsRemoval: true,
  },
  newsGuard: {
    minimumSourceTrust: 0.7,
    sensationalThreshold: 0.55,
    minimumReportScore: 0.62,
    sensitivity: "보통" as never,
    mode: "basic",
  },
  notifications: [
    { id: "daily-briefing", label: "일일 요약", description: "전시용 설정", enabled: true },
    { id: "major-event", label: "RED 즉시 알림", description: "전시용 설정", enabled: true },
    { id: "yellow-signal", label: "YELLOW 즉시 알림", description: "전시용 설정", enabled: true },
    { id: "portfolio-risk", label: "GREEN 즉시 알림", description: "GREEN 신호는 즉시 이메일 알림 대상이 아닙니다.", enabled: false },
  ],
  apiConnections: [
    { id: "exhibition_demo", name: "전시용 샘플 데이터", connected: true },
  ],
  display: {
    language: "한국어",
    theme: "다크 모드",
    numberFormat: "한국 (KRW)",
    timezone: "(UTC+09:00) 서울",
  },
  misc: {
    searchLogRetention: "전시 중 브라우저 저장",
    sessionTimeout: "브라우저 세션",
  },
};
