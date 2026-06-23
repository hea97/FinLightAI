import type { Locale, ViewId } from "../i18n/translations";

export type MarketTab = "korea" | "global" | "watched";
export type NewsFilter = "all" | "verified" | "watch" | "rumor";

export type Metric = {
  label: string;
  value: string;
  description: string;
  tone: "up" | "down" | "neutral" | "teal" | "blue";
};

export type Industry = {
  id: string;
  name: string;
  score: number;
  state: string;
  tone: "good" | "ok" | "neutral" | "warn" | "bad";
  description: string;
  reason: string;
  assets: string[];
  risks: string[];
};

export type NewsItem = {
  id: string;
  status: NewsFilter;
  source: string;
  title: string;
  summary: string;
  impact: number;
  trust: "높음" | "보통" | "낮음";
  reason: string;
  relatedView: ViewId;
};

export type PortfolioAsset = {
  id: string;
  name: string;
  sector: string;
  weight: number;
  signal: string;
  newsCount: number;
};

export const marketTabs: Record<Locale, { id: MarketTab; label: string }[]> = {
  ko: [
    { id: "korea", label: "국내 시장" },
    { id: "global", label: "해외 시장" },
    { id: "watched", label: "관심 산업" },
  ],
  en: [
    { id: "korea", label: "Korea" },
    { id: "global", label: "Overseas" },
    { id: "watched", label: "Watched Industries" },
  ],
};

export const marketCopy: Record<Locale, Record<MarketTab, { headline: string; summary: string }>> = {
  ko: {
    korea: {
      headline: "국내 증시는 반도체가 방어하고 금융이 부담입니다.",
      summary: "원화 변동성과 금리 발언을 함께 보며, 대형 수출주 중심의 방어 신호가 우세합니다.",
    },
    global: {
      headline: "해외 시장은 AI 수요와 금리 불확실성이 동시에 움직입니다.",
      summary: "미국 기술주는 강하지만, 공급망 뉴스와 연준 발언의 신뢰도를 나눠 볼 필요가 있습니다.",
    },
    watched: {
      headline: "관심 산업은 반도체, 방산, 항공의 온도 차가 큽니다.",
      summary: "관심 산업 탭은 포트폴리오와 연결될 산업만 추려서 리스크를 빠르게 확인하는 영역입니다.",
    },
  },
  en: {
    korea: {
      headline: "Korea is supported by semiconductors while financials stay pressured.",
      summary: "Currency volatility and rate comments matter, but exporters are still cushioning the tape.",
    },
    global: {
      headline: "Overseas markets balance AI demand with rate uncertainty.",
      summary: "Large-cap tech remains firm, while supply-chain reports need careful trust checks.",
    },
    watched: {
      headline: "Watched sectors show a wide gap between chips, defense, and airlines.",
      summary: "This tab narrows the dashboard to sectors that can affect the registered portfolio.",
    },
  },
};

export const metrics: Record<MarketTab, Metric[]> = {
  korea: [
    { label: "KOSPI", value: "+0.8%", description: "대형 수출주 강세", tone: "up" },
    { label: "원/달러", value: "1,383", description: "변동성 확대", tone: "neutral" },
    { label: "기관 수급", value: "+2,140억", description: "전기전자 순매수", tone: "teal" },
    { label: "리스크", value: "52", description: "주의권 하단", tone: "neutral" },
  ],
  global: [
    { label: "NASDAQ", value: "+1.1%", description: "AI 인프라주 견인", tone: "up" },
    { label: "VIX", value: "18.4", description: "보통 수준", tone: "neutral" },
    { label: "미 10년물", value: "4.31%", description: "금리 부담 지속", tone: "down" },
    { label: "리스크", value: "61", description: "변동성 주의", tone: "neutral" },
  ],
  watched: [
    { label: "반도체", value: "+78", description: "AI 서버 수요", tone: "up" },
    { label: "방산", value: "+38", description: "수출 계약 기대", tone: "teal" },
    { label: "항공", value: "-58", description: "유가와 환율 부담", tone: "down" },
    { label: "금융", value: "-45", description: "금리 경로 불확실", tone: "down" },
  ],
};

export const industries: Industry[] = [
  {
    id: "semiconductor",
    name: "반도체",
    score: 78,
    state: "강한 긍정",
    tone: "good",
    description: "HBM, AI 서버, 파운드리 투자 뉴스가 동시에 우호적으로 작용하고 있습니다.",
    reason: "고객사 장기 공급 계약과 데이터센터 증설 보도가 수요 기대를 높였습니다.",
    assets: ["삼성전자", "SK하이닉스", "NVIDIA"],
    risks: ["공급 병목 과장 보도", "환율 민감도", "미국 규제 발언"],
  },
  {
    id: "finance",
    name: "금융",
    score: -45,
    state: "주의",
    tone: "warn",
    description: "금리 경로 불확실성과 경기 둔화 우려가 은행, 증권주에 부담입니다.",
    reason: "연준 발언 해석이 엇갈리며 순이자마진과 투자 심리에 동시에 영향을 주고 있습니다.",
    assets: ["KB금융", "신한지주", "미래에셋증권"],
    risks: ["부동산 PF", "예대마진 둔화", "미국 금리 경로"],
  },
  {
    id: "auto",
    name: "자동차",
    score: 12,
    state: "약한 긍정",
    tone: "ok",
    description: "수출 기대는 남아 있지만 전기차 수요 둔화 보도가 일부 부담입니다.",
    reason: "환율 효과와 신차 믹스 개선은 긍정적이나 가격 경쟁 뉴스가 상쇄하고 있습니다.",
    assets: ["현대차", "기아", "현대모비스"],
    risks: ["전기차 가격 경쟁", "미국 재고", "원자재 비용"],
  },
  {
    id: "airline",
    name: "항공",
    score: -58,
    state: "부정",
    tone: "bad",
    description: "유가 상승과 환율 부담이 비용 리스크를 키우고 있습니다.",
    reason: "여객 수요는 견조하지만 비용 변수의 영향도가 더 크게 반영됐습니다.",
    assets: ["대한항공", "제주항공", "진에어"],
    risks: ["유류비 헤지", "환율", "예약률 둔화"],
  },
  {
    id: "defense",
    name: "방산",
    score: 38,
    state: "긍정",
    tone: "good",
    description: "수출 계약 기대와 지정학적 긴장이 수주 전망을 지지합니다.",
    reason: "장기 프로젝트 성격상 단기 뉴스보다 계약 확정 여부를 따로 확인해야 합니다.",
    assets: ["한화에어로스페이스", "현대로템", "LIG넥스원"],
    risks: ["계약 지연", "환율", "정책 변화"],
  },
  {
    id: "consumer",
    name: "소비재",
    score: 4,
    state: "중립",
    tone: "neutral",
    description: "소비심리 둔화와 방어주 성격이 엇갈려 방향성이 약합니다.",
    reason: "가격 전가력과 재고 부담을 기업별로 구분해 볼 필요가 있습니다.",
    assets: ["CJ제일제당", "이마트", "아모레퍼시픽"],
    risks: ["내수 둔화", "재고 부담", "원가 상승"],
  },
];

export const newsItems: NewsItem[] = [
  {
    id: "fed-rate",
    status: "verified",
    source: "Reuters",
    title: "미 연준, 금리 동결 가능성 시사",
    summary: "정책 발언은 확인된 출처이나 시장 해석은 과도할 수 있습니다.",
    impact: 82,
    trust: "높음",
    reason: "원문 출처가 명확하고 복수 매체가 같은 방향으로 확인했습니다.",
    relatedView: "market",
  },
  {
    id: "nvidia-supply",
    status: "watch",
    source: "Bloomberg",
    title: "NVIDIA 공급 병목 지연 보도",
    summary: "반도체 수요 기대에는 긍정적이나 병목 기간은 추정치입니다.",
    impact: 74,
    trust: "보통",
    reason: "공신력 있는 보도이지만 익명 관계자와 추정 표현이 포함되어 있습니다.",
    relatedView: "industry",
  },
  {
    id: "theme-rumor",
    status: "rumor",
    source: "Community",
    title: "테마주 급등 확정 루머 확산",
    summary: "출처가 불명확하고 확정 표현이 강해 뉴스 가드 주의 대상입니다.",
    impact: 39,
    trust: "낮음",
    reason: "원문 링크와 공식 공시가 없고 같은 문장이 여러 채널에 반복됩니다.",
    relatedView: "guard",
  },
];

export const initialPortfolio: PortfolioAsset[] = [
  { id: "samsung", name: "삼성전자", sector: "반도체", weight: 38, signal: "긍정", newsCount: 12 },
  { id: "sk-hynix", name: "SK하이닉스", sector: "반도체", weight: 24, signal: "강한 긍정", newsCount: 9 },
  { id: "kakao", name: "카카오", sector: "IT", weight: 14, signal: "중립", newsCount: 4 },
];

export const searchIndex: { type: string; title: string; description: string; view: ViewId }[] = [
  { type: "뉴스", title: "미 연준 금리 동결", description: "시장 신호와 뉴스 가드", view: "guard" },
  { type: "산업", title: "반도체", description: "영향도 +78, AI 서버 수요", view: "industry" },
  { type: "산업", title: "항공", description: "영향도 -58, 유가와 환율 부담", view: "industry" },
  { type: "자산", title: "삼성전자", description: "등록 자산, 반도체 연결", view: "portfolio" },
  { type: "알림", title: "카카오 채널", description: "로그인과 채널 알림 흐름", view: "kakao" },
  { type: "설정", title: "관심 산업", description: "관심 탭과 알림 기준", view: "settings" },
];
