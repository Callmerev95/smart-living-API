import { request } from "@/lib/api/client";
import type { RecommendationResponse } from "@/types/api";

export function getRecommendations(
  ingredients: string[],
  options: { limit?: number; signal?: AbortSignal } = {},
): Promise<RecommendationResponse> {
  return request<RecommendationResponse>("/api/v1/recommendations", {
    method: "POST",
    body: options.limit ? { ingredients, limit: options.limit } : { ingredients },
    signal: options.signal,
  });
}
