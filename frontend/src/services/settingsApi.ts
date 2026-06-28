import type { SettingsResponse } from "../types/settings";
import { apiFetch } from "./apiClient";

export type SettingsUpdate = Pick<SettingsResponse, "dataCollection" | "newsGuard" | "notifications" | "display" | "misc">;

export function fetchSettingsData(): Promise<SettingsResponse> {
  return apiFetch("/api/settings");
}

export function saveSettingsData(payload: SettingsUpdate): Promise<SettingsResponse> {
  return apiFetch("/api/settings", { method: "PUT", body: JSON.stringify(payload) });
}
