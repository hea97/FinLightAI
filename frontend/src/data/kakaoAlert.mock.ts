import type { KakaoAlertResponse } from "../types/kakaoAlert";

export const kakaoAlertMock: KakaoAlertResponse = {
  badges: ["카카오 채널 승인 대기", "이메일 레터 수신 가능", "n8n Webhook 정상"],
  rules: [
    { id: "market-risk", icon: "▥", label: "시장 위험도 70 이상", enabled: true },
    { id: "industry-impact", icon: "▣", label: "관심 산업 영향도 ±60 이상", enabled: true },
    { id: "low-trust-news", icon: "▤", label: "신뢰도 낮은 뉴스 감지", enabled: true },
    { id: "portfolio-news", icon: "▰", label: "내 포트폴리오 관련 부정 뉴스 발생", enabled: true },
    { id: "red-signal", icon: "⚑", label: "RED 신호 발생", enabled: true },
    { id: "daily-briefing", icon: "▧", label: "일일 AI 브리핑 요약", enabled: true },
  ],
  questions: [
    { id: "q1", label: "오늘 시장 신호 알려줘" },
    { id: "q2", label: "주의 뉴스 있어?" },
    { id: "q3", label: "반도체 영향도 보여줘" },
    { id: "q4", label: "내 포트폴리오 리스크 알려줘" },
    { id: "q5", label: "RED 신호 이유가 뭐야?" },
  ],
  integrations: [
    { id: "email", icon: "✉", label: "이메일 레터", value: "수신 가능", health: "connected" },
    { id: "channel", icon: "☁", label: "카카오 채널", value: "승인 대기", health: "recent" },
    { id: "bot", icon: "☻", label: "챗봇", value: "준비 완료", health: "ready" },
    { id: "webhook", icon: "⌁", label: "n8n Webhook", value: "정상", health: "normal" },
    { id: "api", icon: "▣", label: "FinLightAI API", value: "정상", health: "normal" },
    { id: "test", icon: "◷", label: "마지막 테스트", value: "2분 전", health: "recent" },
  ],
  history: [
    { id: "h1", sentAt: "09:30", type: "YELLOW 신호", trigger: "반도체 + 뉴스 가드 주의 2건", status: "발송 완료", tone: "yellow" },
    { id: "h2", sentAt: "08:00", type: "일일 AI 브리핑", trigger: "시장 요약", status: "발송 완료", tone: "blue" },
    { id: "h3", sentAt: "07:42", type: "포트폴리오 리스크", trigger: "반도체 비중 높음 + 정책 뉴스", status: "발송 완료", tone: "purple" },
  ],
  flow: [
    { id: "user", icon: "♙", title: "사용자", subtitle: "질문/조건 감지" },
    { id: "channel", icon: "K", title: "카카오 채널 챗봇", subtitle: "요청 수신" },
    { id: "n8n", icon: "⌁", title: "n8n Webhook", subtitle: "자동화 트리거" },
    { id: "api", icon: "FL", title: "FinLightAI API", subtitle: "시장/뉴스 분석" },
    { id: "response", icon: "</>", title: "응답 가공", subtitle: "메시지 포맷" },
    { id: "message", icon: "K", title: "카카오톡 메시지", subtitle: "사용자에게 발송" },
  ],
  previewMessages: [
    {
      id: "m1",
      sender: "bot",
      time: "09:30",
      body:
        "[FinLightAI] 🟡 주의 신호\n기준: 2026.06.23 09:30\n대상: 해외 시장 / 반도체\n시장 위험도: 68/100\n산업 영향도: 반도체 +78\n뉴스 가드: 주의 뉴스 2건\n\n확인 포인트\n- 금리 발언 불확실성\n- 저신뢰 뉴스 확산 여부\n- VIX 변동성 상승",
      actionLabel: "대시보드에서 자세히 보기",
    },
    {
      id: "m2",
      sender: "user",
      time: "09:31",
      body: "오늘 시장 신호 알려줘",
    },
    {
      id: "m3",
      sender: "bot",
      time: "09:31",
      body:
        "[FinLightAI] 오늘 시장 상태 요약\n신호: YELLOW (주의)\n시장 위험도: 68/100\n주요 이슈: 금리 불확실성, 반도체 강세\n뉴스 가드: 주의 뉴스 2건 감지",
      actionLabel: "자세히 보기",
    },
  ],
};
