import type { PortfolioAsset, PortfolioResponse } from "../types/portfolio";
import { apiFetch } from "./apiClient";

export type PortfolioAssetInput = Omit<PortfolioAsset, "id" | "relatedNewsCount" | "cautionNewsCount" | "updatedAt">;

export function fetchPortfolioData(): Promise<PortfolioResponse> {
  return apiFetch("/api/portfolio");
}

export function createPortfolioAsset(payload: PortfolioAssetInput): Promise<PortfolioAsset> {
  return apiFetch("/api/portfolio", { method: "POST", body: JSON.stringify(payload) });
}

export function updatePortfolioAsset(assetId: string, payload: PortfolioAssetInput): Promise<PortfolioAsset> {
  return apiFetch(`/api/portfolio/${encodeURIComponent(assetId)}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function deletePortfolioAsset(assetId: string): Promise<void> {
  return apiFetch(`/api/portfolio/${encodeURIComponent(assetId)}`, { method: "DELETE" });
}
