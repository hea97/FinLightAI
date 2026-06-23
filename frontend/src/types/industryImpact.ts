export type IndustryTone = "positive" | "weak_positive" | "neutral" | "caution" | "negative";

export interface IndustrySummary {
  id: string;
  name: string;
  score: number;
  tone: IndustryTone;
  toneLabel: string;
  newsCount: number;
  icon: string;
}

export interface IndustryReasonSet {
  positive: string[];
  caution: string[];
}

export interface RelatedNewsItem {
  id: string;
  rank: number;
  title: string;
  source: string;
  sentimentLabel: "긍정" | "중립" | "부정";
  impactScore: number;
}

export interface IndustryDetail {
  industryId: string;
  title: string;
  score: number;
  statusLabel: string;
  description: string;
  relatedStocks: string[];
  newsCount: number;
  averageSentiment: number;
  riskPoints: number;
  updatedAt: string;
  reasons: IndustryReasonSet;
  topNews: RelatedNewsItem[];
}

export interface IndustryImpactResponse {
  industries: IndustrySummary[];
  details: Record<string, IndustryDetail>;
}
