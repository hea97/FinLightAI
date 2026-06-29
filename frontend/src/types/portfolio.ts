export type AssetStatus = "holding" | "partial_sold" | "watching";
export type AssetMarket = "KR" | "US" | "TW" | "OTHER";
export type AssetCurrency = "KRW" | "USD" | "TWD";
export type LinkedSignalTone = "positive" | "neutral" | "caution" | "negative";

export interface PortfolioAsset {
  id: string;
  assetName: string;
  symbol: string;
  market: AssetMarket;
  industry: string;
  quantity: number;
  averageBuyPrice: number;
  currentPrice: number;
  recentSellPrice?: number;
  currency: AssetCurrency;
  status: AssetStatus;
  decisionMemo?: string;
  relatedNewsCount: number;
  cautionNewsCount: number;
  updatedAt: string;
  priceDataSource?: "real" | "mock" | "not_connected";
  priceAsOf?: string;
}

export interface PortfolioSummary {
  assetCount: number;
  totalInputAmount: number;
  totalCurrentAmount: number;
  valuationGap: number;
  valuationGapRate: number;
  linkedIndustryCount: number;
  cautionAlertCount: number;
  normalAlertCount: number;
  updatedAt: string;
}

export interface IndustryConnection {
  id: string;
  industryName: string;
  connectedAssetCount: number;
  signalLabel: "긍정" | "주의" | "중립" | "부정";
}

export interface LinkedSignal {
  id: string;
  industryName: string;
  time: string;
  title: string;
  summary: string;
  relatedAssetCount: number;
  tone: LinkedSignalTone;
}

export interface PortfolioResponse {
  summary: PortfolioSummary;
  assets: PortfolioAsset[];
  industryConnections: IndustryConnection[];
  linkedSignals: LinkedSignal[];
}
