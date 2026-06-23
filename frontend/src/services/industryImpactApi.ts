import { industryImpactMock } from "../data/industryImpact.mock";
import type { IndustryImpactResponse } from "../types/industryImpact";

const USE_MOCK = true;

export async function fetchIndustryImpactData(): Promise<IndustryImpactResponse> {
  if (USE_MOCK) {
    return industryImpactMock;
  }

  const response = await fetch("/api/industry-impact");

  if (!response.ok) {
    throw new Error("산업 영향도 데이터를 불러오지 못했습니다.");
  }

  return response.json();
}
