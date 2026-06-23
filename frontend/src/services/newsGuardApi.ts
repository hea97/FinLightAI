import { newsGuardMock } from "../data/newsGuard.mock";
import type { NewsGuardFilter, NewsGuardViewModel } from "../types/newsGuard";

const USE_MOCK = true;

export async function fetchNewsGuardData(filter: NewsGuardFilter = "all"): Promise<NewsGuardViewModel> {
  if (USE_MOCK) {
    const articles =
      filter === "all"
        ? newsGuardMock.articles
        : newsGuardMock.articles.filter((article) => article.reliabilityLevel === filter);

    return {
      ...newsGuardMock,
      articles,
    };
  }

  const response = await fetch(`/api/news-guard?filter=${filter}`);

  if (!response.ok) {
    throw new Error("뉴스 가드 데이터를 불러오지 못했습니다.");
  }

  return response.json();
}
