import { request } from "@/lib/api/client";
import type { Ingredient } from "@/types/api";

type IngredientListResponse = {
  ingredients: Ingredient[];
  meta: { count: number };
};

export function getIngredients(
  options: { signal?: AbortSignal } = {},
): Promise<IngredientListResponse> {
  return request<IngredientListResponse>("/api/v1/ingredients", {
    signal: options.signal,
  });
}
