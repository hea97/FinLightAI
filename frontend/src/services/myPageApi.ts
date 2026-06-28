import type { MyPageAlertSetting, MyPageResponse } from "../types/myPage";
import { apiFetch } from "./apiClient";

export function fetchMyPageData(): Promise<MyPageResponse> {
  return apiFetch("/api/mypage");
}

export function updateMyPageData(payload: {
  alertSettings?: MyPageAlertSetting[];
  interests?: string[];
}): Promise<MyPageResponse> {
  return apiFetch("/api/mypage", { method: "PATCH", body: JSON.stringify(payload) });
}
