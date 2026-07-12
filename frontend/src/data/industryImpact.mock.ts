import type { IndustryDetail, IndustryImpactResponse, IndustrySummary, IndustryTone } from "../types/industryImpact";

const summaries: IndustrySummary[] = [
  { id: "semiconductor", name: "반도체", score: 78, tone: "positive", toneLabel: "강한 긍정", newsCount: 12, icon: "▣" },
  { id: "finance", name: "금융", score: -45, tone: "caution", toneLabel: "주의", newsCount: 9, icon: "¤" },
  { id: "it", name: "IT", score: 51, tone: "positive", toneLabel: "긍정", newsCount: 8, icon: "▤" },
  { id: "auto", name: "자동차", score: 12, tone: "weak_positive", toneLabel: "약한 긍정", newsCount: 7, icon: "IT" },
  { id: "energy", name: "에너지", score: -30, tone: "caution", toneLabel: "주의", newsCount: 6, icon: "ϟ" },
  { id: "bio", name: "바이오", score: 21, tone: "weak_positive", toneLabel: "약한 긍정", newsCount: 6, icon: "⌬" },
  { id: "airline", name: "항공", score: -58, tone: "negative", toneLabel: "부정", newsCount: 5, icon: "✈" },
  { id: "consumer", name: "소비재", score: 4, tone: "neutral", toneLabel: "중립", newsCount: 5, icon: "▱" },
  { id: "oil", name: "정유", score: -22, tone: "caution", toneLabel: "주의", newsCount: 5, icon: "◌" },
  { id: "steel", name: "철강", score: -10, tone: "negative", toneLabel: "약한 부정", newsCount: 4, icon: "▰" },
];

const baseNews = [
  { id: "n1", rank: 1, title: "삼성전자, HBM3E 12단 양산 본격화...AI 메모리 시장 공략 가속", source: "연합뉴스", sentimentLabel: "긍정" as const, impactScore: 0.92 },
  { id: "n2", rank: 2, title: "SK하이닉스, 엔비디아 차세대 GPU 공급 확대 논의", source: "한국경제", sentimentLabel: "긍정" as const, impactScore: 0.72 },
  { id: "n3", rank: 3, title: "미국, CHIPS Act 보조금 2차 지급 계획 발표...삼성·SK 수혜 기대", source: "Bloomberg", sentimentLabel: "긍정" as const, impactScore: 0.63 },
  { id: "n4", rank: 4, title: "글로벌 메모리 가격 반등세 지속...D램 5개월 연속 상승", source: "이데일리", sentimentLabel: "중립" as const, impactScore: 0.18 },
  { id: "n5", rank: 5, title: "중국 반도체 자립 가속...국내 기업 중장기 경쟁 부담", source: "매일경제", sentimentLabel: "부정" as const, impactScore: -0.31 },
];

function makeDetail(summary: IndustrySummary): IndustryDetail {
  const positive = summary.score >= 10;
  const negative = summary.score <= -10;
  const name = summary.name;

  return {
    industryId: summary.id,
    title: `${name} 상세`,
    score: summary.score,
    statusLabel: positive ? "긍정" : negative ? "주의" : "중립",
    description: positive
      ? `${name} 산업은 관련 뉴스와 수급 기대가 함께 확인되며 긍정적인 시장 영향이 나타나고 있습니다. 다만 개별 뉴스의 신뢰도와 위험 요인을 함께 확인해야 합니다.`
      : negative
        ? `${name} 산업은 비용 부담, 정책 불확실성, 수요 둔화 관련 뉴스가 확인되어 주의가 필요합니다. 단기 반응보다 근거 뉴스의 신뢰도를 먼저 확인합니다.`
        : `${name} 산업은 긍정과 부정 요인이 혼재되어 중립적인 흐름을 보입니다. 추가 뉴스와 업데이트 시점을 함께 확인해야 합니다.`,
    relatedStocks: relatedStocksByIndustry(summary.id),
    newsCount: summary.newsCount,
    averageSentiment: Number((summary.score / 126).toFixed(2)),
    riskPoints: summary.score < 0 ? 3 : summary.score < 30 ? 2 : 1,
    updatedAt: "2025.05.24 09:30",
    reasons: {
      positive: positive ? ["AI 수요 확대", "업황 개선", "정책 지원 기대"] : ["일부 반등 신호 확인"],
      caution: negative ? ["글로벌 경기 둔화 우려", "비용 부담 확대"] : ["글로벌 경기 둔화 우려"],
    },
    topNews: baseNews.map((item) => ({
      ...item,
      id: `${summary.id}-${item.id}`,
      title: summary.id === "semiconductor" ? item.title : `${name} 관련 ${item.title}`,
      impactScore: Number((item.impactScore * (Math.abs(summary.score) / 78 || 0.2)).toFixed(2)),
    })),
  };
}

function relatedStocksByIndustry(id: string) {
  const map: Record<string, string[]> = {
    semiconductor: ["삼성전자", "SK하이닉스", "NVIDIA", "TSMC"],
    finance: ["KB금융", "신한지주", "미래에셋증권"],
    it: ["NAVER", "이메일", "Microsoft"],
    auto: ["현대차", "기아", "현대모비스"],
    energy: ["한국전력", "두산에너빌리티", "LS"],
    bio: ["삼성바이오", "셀트리온", "유한양행"],
    airline: ["대한항공", "제주항공", "진에어"],
    consumer: ["CJ제일제당", "이마트", "아모레퍼시픽"],
    oil: ["S-Oil", "SK이노베이션", "GS"],
    steel: ["POSCO홀딩스", "현대제철", "동국제강"],
  };

  return map[id] ?? ["관심 종목"];
}

export function getIndustryTone(score: number): IndustryTone {
  if (score >= 40) return "positive";
  if (score >= 10) return "weak_positive";
  if (score > -10) return "neutral";
  if (score > -40) return "caution";
  return "negative";
}

export const industryImpactMock: IndustryImpactResponse = {
  industries: summaries,
  details: Object.fromEntries(summaries.map((summary) => [summary.id, makeDetail(summary)])),
};
