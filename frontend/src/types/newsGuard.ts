export type NewsGuardFilter = "all" | "trusted" | "watch" | "blocked";

export type ReliabilityLevel = "trusted" | "watch" | "blocked";

export type ProviderStatus = "connected" | "timeout" | "rate_limited" | "disabled" | "fallback" | "error";

export interface ProviderHealth {
  provider: "GDELT" | "NewsAPI" | "Guardian" | "Finnhub" | "BBC RSS";
  status: ProviderStatus;
  message: string;
  lastCheckedAt?: string;
}

export interface NewsGuardStats {
  collectedNewsCount: number;
  trustedNewsCount: number;
  watchNewsCount: number;
  blockedNewsCount: number;
  averageReliabilityScore: number;
  deltaCollectedNewsCount: number;
}

export interface ReliabilityDistributionItem {
  count: number;
  ratio: number;
}

export interface ReliabilityDistribution {
  trusted: ReliabilityDistributionItem;
  watch: ReliabilityDistributionItem;
  blocked: ReliabilityDistributionItem;
}

export interface BlockReason {
  rank: number;
  reason: string;
  count: number;
  ratio: number;
}

export interface NewsArticle {
  id: string;
  title: string;
  source: string;
  publishedAgo: string;
  summary: string;
  reliabilityLevel: ReliabilityLevel;
  reliabilityScore: number;
  impactScore: number;
  sentimentScore: number;
  industries: string[];
  tags: string[];
  originalUrl?: string;
  reasons: string[];
  qualityStatus: "verified" | "low_confidence" | "seed_fallback";
}

export interface QuickFilter {
  id: string;
  label: string;
  count: number;
}

export interface NewsGuardViewModel {
  stats: NewsGuardStats;
  distribution: ReliabilityDistribution;
  blockReasons: BlockReason[];
  quickFilters: QuickFilter[];
  providerHealth: ProviderHealth[];
  articles: NewsArticle[];
  dataSource?: "real" | "mixed" | "seed_fallback";
  providers?: string[];
  isFallback?: boolean;
  lastUpdated?: string;
  warnings?: string[];
}
