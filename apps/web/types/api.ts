export type Difficulty = "easy" | "medium" | "hard";
export type IngredientCategory =
  | "protein"
  | "vegetable"
  | "fruit"
  | "grain"
  | "dairy"
  | "spice"
  | "condiment"
  | "staple"
  | "other";

export type ErrorCode =
  | "INVALID_INGREDIENTS"
  | "VALIDATION_ERROR"
  | "RECIPE_NOT_FOUND"
  | "INGREDIENT_NOT_FOUND"
  | "INTERNAL_ERROR";

export type RecommendationRequest = {
  ingredients: string[];
  limit?: number;
};

export type Query = {
  raw: string[];
  ingredients: string[];
};

export type Meta = {
  count: number;
  limit: number;
  threshold: number;
};

export type Recommendation = {
  id: string;
  name: string;
  description: string;
  matchPercentage: number;
  availableIngredients: string[];
  missingIngredients: string[];
  cookingTimeMinutes: number;
  difficulty: Difficulty;
  servings: number;
  ingredients: string[];
  steps: string[];
  tags: string[];
};

export type RecommendationResponse = {
  query: Query;
  unknownIngredients: string[];
  results: Recommendation[];
  meta: Meta;
};

export type RecipeIngredient = {
  name: string;
  required: boolean;
};

export type Recipe = {
  id: string;
  name: string;
  description: string;
  ingredients: RecipeIngredient[];
  cookingTimeMinutes: number;
  difficulty: Difficulty;
  servings: number;
  steps: string[];
  tags: string[];
  source: string;
};

export type Ingredient = {
  name: string;
  displayName: string;
  aliases: string[];
  category: IngredientCategory;
  staple: boolean;
};

export type ApiError = {
  error: {
    code: ErrorCode | string;
    message: string;
    details: unknown;
  };
};
