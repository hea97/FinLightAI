export type MarketTab = "domestic" | "global" | "watchIndustry";

export type Tone = "positive" | "negative" | "warning" | "neutral" | "blue" | "green";

export type Metric = {
  label: string;
  value: string;
  change?: string;
  note: string;
  tone: Tone;
};

export type BriefingPoint = {
  tone: "green" | "yellow" | "blue";
  text: string;
};

export type NewsImpact = {
  title: string;
  impact: number;
  trust: "신뢰 높음" | "신뢰 보통" | "신뢰 낮음";
  sector: string;
};

export type MarketViewData = {
  title: string;
  description: string;
  risk: number;
  updatedAt: string;
  metrics: Metric[];
  briefing: BriefingPoint[];
  news: NewsImpact[];
  highlightedIndustries: string[];
};

export type IndustryImpact = {
  id: string;
  name: string;
  score: number;
  note: string;
};

export const tabs: { key: MarketTab; label: string }[] = [
  { key: "domestic", label: "국내 시장" },
  { key: "global", label: "해외 시장" },
  { key: "watchIndustry", label: "관심 산업" },
];

export const marketData: Record<MarketTab, MarketViewData> = {
  domestic: {
    title: "국내 시장은 주의가 필요하지만, 해외 시장은 안정적인 흐름을 보이고 있습니다.",
    description:
      "국내 시장은 금리 불확실성과 외국인 수급 이슈로 변동성이 확대될 수 있습니다. 해외 시장은 기술주 중심의 반등이 이어지며 비교적 안정적인 흐름을 보입니다.",
    risk: 68,
    updatedAt: "2026.06.23 09:30 KST",
    briefing: [
      { tone: "green", text: "국내 시장은 금리 불확실성과 외국인 수급 이슈로 주의가 필요합니다." },
      { tone: "yellow", text: "외국인 순매수 전환 여부와 환율 흐름을 함께 확인해야 합니다." },
      { tone: "blue", text: "반도체와 바이오 업종의 긍정 요인이 뉴스에서 확인되고 있습니다." },
    ],
    metrics: [
      { label: "KOSPI", value: "2,671.45", change: "+0.34%", note: "대형 수출주 방어", tone: "positive" },
      { label: "KOSDAQ", value: "842.18", change: "+0.12%", note: "바이오 일부 강세", tone: "positive" },
      { label: "USD/KRW", value: "1,382", change: "-0.15%", note: "환율 부담 완화", tone: "warning" },
      { label: "국고채 3Y", value: "3.28%", change: "-0.02%", note: "금리 경로 확인", tone: "warning" },
      { label: "국내 뉴스", value: "24건", note: "저신뢰 3건 포함", tone: "blue" },
    ],
    news: [
      { title: "연준 발언 이후 금리 불확실성 확대", impact: 82, trust: "신뢰 높음", sector: "금융" },
      { title: "AI 반도체 수요 증가 전망", impact: 76, trust: "신뢰 보통", sector: "반도체" },
      { title: "출처불명 급등 확정성 기사 확산", impact: -71, trust: "신뢰 낮음", sector: "주의" },
      { title: "유가 상승에 따른 항공업 비용 증가 우려", impact: -65, trust: "신뢰 보통", sector: "항공" },
      { title: "바이오 임상 결과 발표 임박", impact: 61, trust: "신뢰 높음", sector: "바이오" },
    ],
    highlightedIndustries: ["semiconductor", "finance", "bio"],
  },
  global: {
    title: "해외 시장은 기술주 중심의 반등이 이어지지만 변동성 확인이 필요합니다.",
    description:
      "미국 기술주는 AI 인프라 수요 기대가 이어지고 있으나, 금리 발언과 에너지 가격 변화가 단기 위험 요인으로 남아 있습니다.",
    risk: 54,
    updatedAt: "2026.06.23 09:30 KST",
    briefing: [
      { tone: "green", text: "나스닥과 S&P 500은 기술주 중심으로 안정적인 흐름을 보입니다." },
      { tone: "yellow", text: "VIX와 장기금리 변화를 함께 보며 변동성 확대 여부를 점검해야 합니다." },
      { tone: "blue", text: "글로벌 반도체 공급망 뉴스는 영향도와 신뢰도를 분리해 확인합니다." },
    ],
    metrics: [
      { label: "NASDAQ", value: "16,432", change: "+0.58%", note: "AI 인프라주 견인", tone: "positive" },
      { label: "S&P 500", value: "5,428", change: "+0.21%", note: "대형주 중심 안정", tone: "positive" },
      { label: "DOW", value: "39,112", change: "-0.08%", note: "방어주 혼조", tone: "neutral" },
      { label: "VIX", value: "18.2", change: "+1.4p", note: "변동성 감시", tone: "warning" },
      { label: "WTI", value: "78.4", change: "+0.7%", note: "에너지 비용 확인", tone: "warning" },
    ],
    news: [
      { title: "미국 기술주 실적 기대감 지속", impact: 79, trust: "신뢰 높음", sector: "기술주" },
      { title: "VIX 상승에 따른 위험회피 심리", impact: -62, trust: "신뢰 보통", sector: "시장" },
      { title: "WTI 가격 안정 가능성 보도", impact: 48, trust: "신뢰 보통", sector: "에너지" },
      { title: "글로벌 반도체 공급망 재편 이슈", impact: 69, trust: "신뢰 높음", sector: "반도체" },
      { title: "달러 강세와 신흥국 수급 부담", impact: -55, trust: "신뢰 보통", sector: "환율" },
    ],
    highlightedIndustries: ["it", "semiconductor", "energy"],
  },
  watchIndustry: {
    title: "관심 산업은 반도체와 IT가 긍정적이고, 항공과 금융은 주의가 필요합니다.",
    description:
      "관심 산업별 뉴스 영향도와 신뢰도 차이가 크므로 업종별 근거 확인이 우선입니다. 알림 조건은 카카오 채널 전송 대상으로 관리됩니다.",
    risk: 61,
    updatedAt: "2026.06.23 09:30 KST",
    briefing: [
      { tone: "green", text: "반도체와 IT 업종은 수요와 투자 뉴스에서 긍정 신호가 확인됩니다." },
      { tone: "yellow", text: "항공은 유가와 환율 부담으로 부정 신호가 이어지고 있습니다." },
      { tone: "blue", text: "관심 산업 5개 조건이 카카오 알림 발송 대상으로 대기 중입니다." },
    ],
    metrics: [
      { label: "반도체", value: "+78", note: "강한 긍정 · 뉴스 12건", tone: "positive" },
      { label: "항공", value: "-58", note: "유가와 환율 부담", tone: "negative" },
      { label: "금융", value: "-45", note: "금리 발언 주의", tone: "warning" },
      { label: "바이오", value: "+21", note: "임상 뉴스 확인", tone: "positive" },
      { label: "알림 조건", value: "5개", note: "카카오 채널 대기", tone: "blue" },
    ],
    news: [
      { title: "AI 반도체 수요 증가 전망", impact: 78, trust: "신뢰 보통", sector: "반도체" },
      { title: "항공업 비용 증가 우려", impact: -58, trust: "신뢰 보통", sector: "항공" },
      { title: "금융주 금리 발언 부담", impact: -45, trust: "신뢰 높음", sector: "금융" },
      { title: "바이오 임상 뉴스 확산", impact: 21, trust: "신뢰 보통", sector: "바이오" },
      { title: "소비재 업종 중립 흐름", impact: 4, trust: "신뢰 보통", sector: "소비재" },
    ],
    highlightedIndustries: ["semiconductor", "airline", "finance", "bio"],
  },
};

export const industries: IndustryImpact[] = [
  { id: "semiconductor", name: "반도체", score: 78, note: "강한 긍정 · 뉴스 12건" },
  { id: "finance", name: "금융", score: -45, note: "주의 · 뉴스 9건" },
  { id: "it", name: "IT", score: 51, note: "긍정 · 뉴스 8건" },
  { id: "auto", name: "자동차", score: 12, note: "약한 긍정" },
  { id: "energy", name: "에너지", score: -30, note: "주의" },
  { id: "bio", name: "바이오", score: 21, note: "약한 긍정" },
  { id: "airline", name: "항공", score: -58, note: "부정" },
  { id: "consumer", name: "소비재", score: 4, note: "중립" },
  { id: "oil", name: "정유", score: -22, note: "주의" },
  { id: "steel", name: "철강", score: -10, note: "약한 부정" },
];
