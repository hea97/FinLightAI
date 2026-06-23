import { myPageMock } from "../data/myPage.mock";
import type { MyPageResponse } from "../types/myPage";

const USE_MOCK = true;

export async function fetchMyPageData(): Promise<MyPageResponse> {
  if (USE_MOCK) {
    return myPageMock;
  }

  const response = await fetch("/api/my-page");
  if (!response.ok) {
    throw new Error("마이페이지 데이터를 불러오지 못했습니다.");
  }

  return response.json();
}
