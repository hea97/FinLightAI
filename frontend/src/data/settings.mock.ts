import type { SettingsResponse } from "../types/settings";

export const settingsMock: SettingsResponse = {
  statusCards: [
    { id: "data", icon: "DATA", title: "데이터 수집 상태", value: "정상", description: "뉴스와 시장 데이터 수집이 작동 중입니다.", tone: "normal" },
    { id: "email", icon: "MAIL", title: "이메일 알림", value: "구독 활성", description: "일일 요약과 RED/YELLOW 알림을 이메일로 받을 수 있습니다.", tone: "connected" },
    { id: "guard", icon: "NEWS", title: "뉴스 가드 필터", value: "엄격", description: "저신뢰 뉴스 차단 수준: 높음", tone: "strict" },
    { id: "api", icon: "API", title: "API 연동", value: "6 / 6 연결", description: "전시 화면에 필요한 API 상태를 확인합니다.", tone: "normal" },
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
    { id: "major-event", label: "주요 이벤트 이메일", description: "중요 시장 이벤트 발생 시 이메일로 알립니다.", enabled: true },
    { id: "yellow-signal", label: "YELLOW 신호 이메일", description: "주의 신호 발생 시 이메일로 알립니다.", enabled: true },
    { id: "portfolio-risk", label: "포트폴리오 위험 이메일", description: "보유 자산 관련 위험 신호를 이메일로 받습니다.", enabled: true },
    { id: "daily-briefing", label: "일일 시장 요약", description: "매일 한 번 시장 요약 이메일을 제공합니다.", enabled: true },
    { id: "weekly-report", label: "주간 리포트", description: "주간 시장 요약 리포트를 이메일로 발송합니다.", enabled: true },
  ],
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
  },
};
