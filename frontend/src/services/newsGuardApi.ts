import type { NewsGuardFilter, NewsGuardViewModel } from "../types/newsGuard";
import { apiFetch } from "./apiClient";

export function fetchNewsGuardData(filter: NewsGuardFilter = "all"): Promise<NewsGuardViewModel> {
  return apiFetch(`/api/news-guard?filter=${encodeURIComponent(filter)}`);
}
