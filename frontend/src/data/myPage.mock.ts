import type { MyPageResponse } from "../types/myPage";

export const myPageMock: MyPageResponse = {
  profile: {
    username: "finlight_user",
    email: "finlight@example.com",
    joinedAt: "2026.07.01",
    lastLoginAt: "2026.07.13 09:31 (KST)",
    language: "한국어",
    alertChannel: "이메일 구독 활성",
    channelConnected: true,
  },
  metrics: [
    { id: "weekly-alerts", icon: "MAIL", label: "이번 주 이메일", value: "18건", helper: "지난 주 대비", delta: "+20%" },
    { id: "industries", icon: "IND", label: "관심 산업", value: "6개", helper: "맞춤 모니터링 중" },
    { id: "keywords", icon: "KEY", label: "저장한 키워드", value: "12개", helper: "맞춤 검색 키워드" },
    { id: "activity", icon: "LOG", label: "최근 활동", value: "7건", helper: "최근 7일 기준" },
  ],
  alertSettings: [
    { id: "email", icon: "MAIL", title: "이메일 구독 활성", description: "일일 요약과 선택한 RED/YELLOW 알림을 이메일로 받을 수 있습니다.", enabled: true },
    { id: "daily-briefing", icon: "DAY", title: "일일 시장 요약", description: "매일 주요 시장 상태와 뉴스 근거를 이메일로 받습니다.", enabled: true },
    { id: "red-signal", icon: "RED", title: "RED/YELLOW 즉시 알림", description: "주요 위험 신호는 설정에 따라 즉시 이메일로 발송됩니다.", enabled: true, emphasis: true },
    { id: "portfolio-news", icon: "PORT", title: "포트폴리오 관련 뉴스", description: "보유 자산과 관련된 주요 뉴스를 이메일로 받습니다.", enabled: true },
    { id: "news-guard", icon: "NEWS", title: "뉴스 가드 주의 알림", description: "저신뢰 또는 과장 가능성이 있는 뉴스 주의 신호를 받습니다.", enabled: true },
  ],
  interests: ["반도체", "AI", "정책/규제", "전기차", "에너지", "바이오"],
  connections: [
    { id: "email", icon: "MAIL", label: "이메일 알림", status: "connected", statusLabel: "구독 활성" },
    { id: "api", icon: "FL", label: "FinLightAI API", status: "connected", statusLabel: "연결됨" },
    { id: "news", icon: "NEWS", label: "뉴스 수집기", status: "normal", statusLabel: "정상" },
  ],
  activities: [
    { id: "a1", icon: "MAIL", title: "이메일 알림 설정 변경: RED/YELLOW 즉시 알림 활성화", timestamp: "2026.07.13 09:15" },
    { id: "a2", icon: "IND", title: "관심 산업 추가: 바이오", timestamp: "2026.07.12 16:42" },
    { id: "a3", icon: "NEWS", title: "뉴스 가드 확인: AI 반도체 규제 이슈", timestamp: "2026.07.12 10:08" },
    { id: "a4", icon: "PORT", title: "포트폴리오 자산 수정", timestamp: "2026.07.11 14:33" },
    { id: "a5", icon: "KEY", title: "키워드 저장: 전력 인프라", timestamp: "2026.07.10 11:27" },
  ],
  shortcuts: [
    { id: "portfolio", icon: "PORT", title: "포트폴리오 관리", description: "자산 현황 및 성과" },
    { id: "guard", icon: "NEWS", title: "뉴스 가드 보기", description: "주의 신호 확인" },
    { id: "industry", icon: "IND", title: "산업 영향도 보기", description: "산업 흐름 분석" },
  ],
  guide: {
    title: "이메일 알림 안내",
    body: "GREEN 신호는 즉시 이메일 알림 대상이 아닙니다. FinLightAI의 신호와 이메일 알림은 투자 추천이나 매수·매도 지시가 아니라 참고용 시장 상태 정보입니다.",
    ctaLabel: "가이드 보기",
  },
};
