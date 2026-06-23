export type KakaoAlertRuleId =
  | "market-risk"
  | "industry-impact"
  | "low-trust-news"
  | "portfolio-news"
  | "red-signal"
  | "daily-briefing";

export type IntegrationHealth = "connected" | "ready" | "normal" | "recent";
export type KakaoAlertTone = "yellow" | "blue" | "purple" | "green";

export interface KakaoAlertRule {
  id: KakaoAlertRuleId;
  icon: string;
  label: string;
  enabled: boolean;
}

export interface KakaoChatQuestion {
  id: string;
  label: string;
}

export interface KakaoIntegrationStatus {
  id: string;
  icon: string;
  label: string;
  value: string;
  health: IntegrationHealth;
}

export interface KakaoAlertHistoryItem {
  id: string;
  sentAt: string;
  type: string;
  trigger: string;
  status: string;
  tone: KakaoAlertTone;
}

export interface KakaoFlowStep {
  id: string;
  icon: string;
  title: string;
  subtitle: string;
}

export interface KakaoPreviewMessage {
  id: string;
  sender: "bot" | "user";
  time: string;
  body: string;
  actionLabel?: string;
}

export interface KakaoAlertResponse {
  badges: string[];
  rules: KakaoAlertRule[];
  questions: KakaoChatQuestion[];
  integrations: KakaoIntegrationStatus[];
  history: KakaoAlertHistoryItem[];
  flow: KakaoFlowStep[];
  previewMessages: KakaoPreviewMessage[];
}
