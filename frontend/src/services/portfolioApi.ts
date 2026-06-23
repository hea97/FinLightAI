import { portfolioMock } from "../data/portfolio.mock";
import type { PortfolioResponse } from "../types/portfolio";

const USE_MOCK = true;

export async function fetchPortfolioData(): Promise<PortfolioResponse> {
  if (USE_MOCK) {
    return portfolioMock;
  }

  const response = await fetch("/api/portfolio");
  if (!response.ok) {
    throw new Error("포트폴리오 데이터를 불러오지 못했습니다.");
  }

  return response.json();
}
