export interface AuthUser {
  id: string;
  provider: string;
  email: string;
  nickname: string;
  profileImageUrl?: string | null;
}

export interface AuthMeResponse {
  authenticated: boolean;
  user: AuthUser | null;
}

export interface UserPreferenceResponse {
  userId: string;
  interestedMarkets: string[];
  interestedIndustries: string[];
  alertEnabled: boolean;
  notificationChannels: string[];
  updatedAt: string;
}

export type UserPreferenceUpdate = Partial<
  Pick<UserPreferenceResponse, "interestedMarkets" | "interestedIndustries" | "alertEnabled" | "notificationChannels">
>;
