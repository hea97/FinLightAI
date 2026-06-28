import type { KakaoAlertResponse, KakaoAlertRule } from "../types/kakaoAlert";
import { apiFetch } from "./apiClient";

export function fetchKakaoAlertData(): Promise<KakaoAlertResponse> {
  return apiFetch("/api/kakao-alert");
}

export function updateKakaoAlertRule(ruleId: string, enabled: boolean): Promise<KakaoAlertRule> {
  return apiFetch(`/api/kakao-alert/rules/${encodeURIComponent(ruleId)}`, {
    method: "PATCH",
    body: JSON.stringify({ enabled }),
  });
}
