import { settingsMock } from "../data/settings.mock";
import type { SettingsResponse } from "../types/settings";

const USE_MOCK = true;

export async function fetchSettingsData(): Promise<SettingsResponse> {
  if (USE_MOCK) {
    return settingsMock;
  }

  const response = await fetch("/api/settings");
  if (!response.ok) {
    throw new Error("설정 데이터를 불러오지 못했습니다.");
  }

  return response.json();
}
