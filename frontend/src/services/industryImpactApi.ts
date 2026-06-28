import type { IndustryImpactResponse } from "../types/industryImpact";
import { apiFetch } from "./apiClient";

export function fetchIndustryImpactData(): Promise<IndustryImpactResponse> {
  return apiFetch("/api/industry-impact");
}
