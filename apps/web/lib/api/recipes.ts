import { request } from "@/lib/api/client";
import type { Recipe } from "@/types/api";

export function getRecipe(
  recipeId: string,
  options: { signal?: AbortSignal } = {},
): Promise<Recipe> {
  return request<Recipe>(`/api/v1/recipes/${encodeURIComponent(recipeId)}`, {
    signal: options.signal,
  });
}
