import type { MyPageResponse } from "../types/myPage";

export const myPageMock: MyPageResponse = {
  profile: {
    username: "ufinlight_user",
    email: "ufinlight@example.com",
    joinedAt: "2025.02.10",
    lastLoginAt: "2025.05.24 09:31 (KST)",
    language: "한국어",
    alertChannel: "이메일 · 이메일 승인 대기",
    channelConnected: true,
  },
  metrics: [
    { id: "weekly-alerts", icon: "●", label: "이번 주 알림", value: "18건", helper: "지난 주 대비", delta: "+20%" },
    { id: "industries", icon: "★", label: "관심 산업", value: "6개", helper: "맞춤 모니터링 중" },
    { id: "keywords", icon: "◆", label: "저장한 키워드", value: "12개", helper: "맞춤 검색 키워드" },
    { id: "activity", icon: "◷", label: "최근 활동", value: "7건", helper: "최근 7일 기준" },
  ],
  alertSettings: [
    { id: "email", icon: "✉", title: "이메일 레터", description: "중요 신호와 브리핑을 이메일로 받아요", enabled: true },
    { id: "daily-briefing", icon: "☆", title: "일일 AI 브리핑", description: "매일 아침 AI 브리핑 리포트를 받아요", enabled: true },
    { id: "red-signal", icon: "◇", title: "RED 신호 알림", description: "시장 위험 신호 감지 시 즉시 알려드려요", enabled: true, emphasis: true },
    { id: "portfolio-news", icon: "◇", title: "내 포트폴리오 관련 뉴스", description: "보유 자산 관련 주요 뉴스를 받아요", enabled: true },
    { id: "news-guard", icon: "⚙", title: "뉴스 가드 주의 알림", description: "뉴스 가드에서 포착한 주의 신호를 받아요", enabled: true },
  ],
  interests: ["반도체", "AI", "정책/규제", "전기차", "에너지", "바이오"],
  connections: [
    { id: "email", icon: "MAIL", label: "이메일 레터", status: "connected", statusLabel: "수신 준비" },
    { id: "api", icon: "FL", label: "FinLightAI API", status: "connected", statusLabel: "연결됨" },
    { id: "news", icon: "▤", label: "뉴스 수집기", status: "normal", statusLabel: "정상" },
  ],
  activities: [
    { id: "a1", icon: "♧", title: "알림 설정 변경: RED 신호 알림 활성화", timestamp: "2025.05.24 09:15" },
    { id: "a2", icon: "♤", title: "관심 산업 추가: 바이오", timestamp: "2025.05.23 16:42" },
    { id: "a3", icon: "☆", title: "뉴스 가드 확인: AI 반도체 규제 이슈", timestamp: "2025.05.23 10:08" },
    { id: "a4", icon: "◷", title: "포트폴리오 자산 수정: 엔비디아 비중 조정", timestamp: "2025.05.22 14:33" },
    { id: "a5", icon: "◇", title: "키워드 저장: 전력 인프라", timestamp: "2025.05.21 11:27" },
  ],
  shortcuts: [
    { id: "portfolio", icon: "▰", title: "포트폴리오 관리", description: "자산 현황 및 성과" },
    { id: "guard", icon: "◆", title: "뉴스 가드 보기", description: "주의 신호 확인" },
    { id: "industry", icon: "▥", title: "산업 영향도 보기", description: "산업 트렌드 분석" },
  ],
  guide: {
    title: "튜토리얼 / 도움말",
    body: "RED / YELLOW / GREEN 신호는 시장 상태를 나타내는 지표입니다. 알림은 투자 추천이 아닌 정보 제공을 목적으로 합니다.",
    ctaLabel: "가이드 보기",
  },
};
