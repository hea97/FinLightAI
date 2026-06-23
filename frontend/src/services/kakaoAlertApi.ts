import { kakaoAlertMock } from "../data/kakaoAlert.mock";
import type { KakaoAlertResponse } from "../types/kakaoAlert";

const USE_MOCK = true;

export async function fetchKakaoAlertData(): Promise<KakaoAlertResponse> {
  if (USE_MOCK) {
    return kakaoAlertMock;
  }

  const response = await fetch("/api/kakao-alert");
  if (!response.ok) {
    throw new Error("카카오 알림 데이터를 불러오지 못했습니다.");
  }

  return response.json();
}
