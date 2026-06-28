import type { BriefingResponse } from "../types/briefing";
import { apiFetch } from "./apiClient";

export function fetchBriefingData(): Promise<BriefingResponse> {
  return apiFetch("/api/briefing");
}
