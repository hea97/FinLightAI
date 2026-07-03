import type { AuthMeResponse, UserPreferenceResponse, UserPreferenceUpdate } from "../types/auth";
import { apiFetch, apiUrl } from "./apiClient";

export function redirectToGoogleLogin(): void {
  window.location.href = apiUrl("/api/auth/google/login");
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
