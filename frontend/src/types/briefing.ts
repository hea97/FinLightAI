export interface BriefingNews {
  title: string;
  source: string;
  url: string;
  publishedAt: string;
  reliabilityScore: number;
}

export interface BriefingResponse {
  asOf: string;
  signal: "RED" | "YELLOW" | "GREEN";
  riskScore: number;
  headline: string;
  summary: string[];
  keyNews: BriefingNews[];
  providerStatus: Record<string, string>;
  dataSource?: "real" | "mixed" | "seed_fallback" | "exhibition_demo";
  isDemo?: boolean;
  providers?: string[];
  isFallback?: boolean;
  lastUpdated?: string;
  warnings?: string[];
}
