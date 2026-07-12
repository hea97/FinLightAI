import type { AuthMeResponse, UserPreferenceResponse, UserPreferenceUpdate } from "../types/auth";
import { apiFetch, apiUrl } from "./apiClient";

const TRUE_VALUES = new Set(["true", "1", "yes", "on"]);

export const isExhibitionDemoLoginVisible = TRUE_VALUES.has(
  String(import.meta.env.VITE_EXHIBITION_DEMO_LOGIN_ENABLED ?? "true").trim().toLowerCase(),
);

export function redirectToGoogleLogin(): void {
  window.location.href = apiUrl("/api/auth/google/login");
}

export function loginWithExhibitionDemo(accessCode?: string): Promise<AuthMeResponse> {
  return apiFetch("/api/auth/demo", {
    method: "POST",
    body: JSON.stringify(accessCode ? { accessCode } : {}),
  });
}

export function fetchCurrentUser(): Promise<AuthMeResponse> {
  return apiFetch("/api/auth/me");
}

export function logout(): Promise<void> {
  return apiFetch("/api/auth/logout", { method: "POST" });
}

export function fetchOnboardingPreferences(): Promise<UserPreferenceResponse> {
  return apiFetch("/api/onboarding/preferences");
}

export function saveOnboardingPreferences(payload: UserPreferenceUpdate): Promise<UserPreferenceResponse> {
  return apiFetch("/api/onboarding/preferences", {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}
