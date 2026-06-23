export type SettingsStatusTone = "normal" | "warning" | "strict" | "connected";
export type SettingsToggleId =
  | "low-trust-filter"
  | "duplicate-news"
  | "major-event"
  | "yellow-signal"
  | "portfolio-risk"
  | "daily-briefing"
  | "weekly-report";
export type NewsGuardMode = "basic" | "strict" | "flexible";

export interface SettingsStatusCard {
  id: string;
  icon: string;
  title: string;
  value: string;
  description: string;
  tone: SettingsStatusTone;
}

export interface DataCollectionSettings {
  newsInterval: string;
  newsRetention: string;
  marketDataRetention: string;
  keywords: string[];
  lowTrustFilter: boolean;
  duplicateNewsRemoval: boolean;
}

export interface NewsGuardSettings {
  minimumSourceTrust: number;
  sensationalThreshold: number;
  minimumReportScore: number;
  sensitivity: "낮음" | "보통" | "높음";
  mode: NewsGuardMode;
}

export interface NotificationSetting {
  id: SettingsToggleId;
  label: string;
  description: string;
  enabled: boolean;
}

export interface KakaoChannelReceiveSettings {
  botName: string;
  statusLabel: string;
  description: string;
}

export interface ApiConnection {
  id: string;
  name: string;
  connected: boolean;
}

export interface DisplaySettings {
  language: string;
  theme: string;
  numberFormat: string;
  timezone: string;
}

export interface MiscSettings {
  searchLogRetention: string;
  sessionTimeout: string;
  kakaoNotice: string;
}

export interface SettingsResponse {
  statusCards: SettingsStatusCard[];
  dataCollection: DataCollectionSettings;
  newsGuard: NewsGuardSettings;
  notifications: NotificationSetting[];
  kakaoChannel: KakaoChannelReceiveSettings;
  apiConnections: ApiConnection[];
  display: DisplaySettings;
  misc: MiscSettings;
}
