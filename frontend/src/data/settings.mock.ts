import type { SettingsResponse } from "../types/settings";

export const settingsMock: SettingsResponse = {
  statusCards: [
    { id: "data", icon: "☁", title: "데이터 수집 상태", value: "정상", description: "모든 데이터 소스가 정상 작동 중", tone: "normal" },
    {
      id: "kakao",
      icon: "♢",
      title: "카카오톡 채널 수신 방식",
      value: "채널 봇 추가",
      description: "FinLightAI 카카오 채널 봇을 추가하면 알림을 받을 수 있습니다.",
      tone: "connected",
    },
    { id: "guard", icon: "◇", title: "뉴스 가드 필터", value: "엄격", description: "저신뢰 뉴스 차단 수준: 높음", tone: "strict" },
    { id: "api", icon: "</>", title: "API 연동", value: "7 / 10 연결", description: "일부 API가 비활성화되어 있습니다.", tone: "warning" },
  ],
  dataCollection: {
    newsInterval: "15분",
    newsRetention: "90일",
    marketDataRetention: "2년",
    keywords: ["AI", "반도체", "정책", "수출규제", "엔비디아", "삼성전자"],
    lowTrustFilter: true,
    duplicateNewsRemoval: true,
  },
  newsGuard: {
    minimumSourceTrust: 0.8,
    sensationalThreshold: 0.7,
    minimumReportScore: 22,
    sensitivity: "높음",
    mode: "strict",
  },
  notifications: [
    { id: "major-event", label: "주요 이벤트 알림", description: "FRED, 기업공시, 실적 등", enabled: true },
    { id: "yellow-signal", label: "YELLOW 신호 알림", description: "YELLOW 신호 발생 시", enabled: true },
    { id: "portfolio-risk", label: "포트폴리오 리스크 알림", description: "보유 자산 리스크 관련 경고", enabled: true },
    { id: "daily-briefing", label: "일일 AI 브리핑", description: "하루 한 번 핵심 뉴스 요약 제공", enabled: true },
    { id: "weekly-report", label: "주간 리포트", description: "주간 시장 요약 리포트 발송", enabled: true },
  ],
  kakaoChannel: {
    botName: "FinLightAI 카카오 채널 봇",
    statusLabel: "추가됨",
    description: "카카오톡에서 FinLightAI 채널 봇을 추가하면 주요 시장 상태 알림을 받아볼 수 있습니다.",
  },
  apiConnections: [
    { id: "gdelt", name: "GDELT DOC 2.0 API", connected: true },
    { id: "guardian", name: "The Guardian API", connected: true },
    { id: "newsapi", name: "NewsAPI", connected: true },
    { id: "bbc", name: "BBC RSS", connected: true },
    { id: "finnhub", name: "Finnhub News API", connected: true },
    { id: "yfinance", name: "yfinance / pykrx", connected: true },
  ],
  display: {
    language: "한국어",
    theme: "다크 모드",
    numberFormat: "한국 (KRW)",
    timezone: "(UTC+09:00) 서울",
  },
  misc: {
    searchLogRetention: "180일",
    sessionTimeout: "30분",
    kakaoNotice: "카카오 알림은 직접 연결형 푸시가 아니라, FinLightAI 카카오 채널 봇 추가 후 카카오톡 채널을 통해 발송됩니다.",
  },
};
