export type MyPageAlertId = "email" | "daily-briefing" | "red-signal" | "portfolio-news" | "news-guard";
export type MyPageConnectionStatus = "normal" | "connected";
export type MyPageShortcutTarget = "portfolio" | "guard" | "industry";

export interface MyPageProfile {
  username: string;
  email: string;
  joinedAt: string;
  lastLoginAt: string;
  language: "한국어" | "English";
  alertChannel: string;
  channelConnected: boolean;
}

export interface MyPageMetric {
  id: string;
  icon: string;
  label: string;
  value: string;
  helper: string;
  delta?: string;
}

export interface MyPageAlertSetting {
  id: MyPageAlertId;
  icon: string;
  title: string;
  description: string;
  enabled: boolean;
  emphasis?: boolean;
}

export interface MyPageConnection {
  id: string;
  icon: string;
  label: string;
  status: MyPageConnectionStatus;
  statusLabel: string;
}

export interface MyPageActivity {
  id: string;
  icon: string;
  title: string;
  timestamp: string;
}

export interface MyPageShortcut {
  id: MyPageShortcutTarget;
  icon: string;
  title: string;
  description: string;
}

export interface MyPageGuide {
  title: string;
  body: string;
  ctaLabel: string;
}

export interface MyPageResponse {
  profile: MyPageProfile;
  metrics: MyPageMetric[];
  alertSettings: MyPageAlertSetting[];
  interests: string[];
  connections: MyPageConnection[];
  activities: MyPageActivity[];
  shortcuts: MyPageShortcut[];
  guide: MyPageGuide;
}
