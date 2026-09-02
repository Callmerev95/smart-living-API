import type { RecommendationRequest, RecommendationResponse } from "@/types/api";

/**
 * Contoh request/response untuk API showcase (`docs/content-schema.md` §B.10.1–§B.10.2).
 *
 * Satu sumber: ditulis sekali di sini, dipakai oleh `RequestExample` dan
 * `ResponseExample`. Response di-annotate `RecommendationResponse` sehingga
 * perubahan kontrak membuat `pnpm typecheck` gagal — bukan diam-diam basi
 * (mitigasi contract drift, `docs/technical-architecture.md` §28).
 *
 * Isi diambil dari response nyata `POST /api/v1/recommendations` untuk input
 * `["telur", "ayam", "wortel"]`, dipangkas ke satu hasil dan dua langkah agar
 * enak dibaca.
 */

export const API_EXAMPLE_METHOD = "POST";
export const API_EXAMPLE_PATH = "/api/v1/recommendations";
export const API_EXAMPLE_HEADERS = "Content-Type: application/json";

export const API_EXAMPLE_REQUEST: RecommendationRequest = {
  ingredients: ["telur", "ayam", "wortel"],
  limit: 5,
};

export const API_EXAMPLE_RESPONSE: RecommendationResponse = {
  query: {
    raw: ["telur", "ayam", "wortel"],
    ingredients: ["egg", "chicken", "carrot"],
  },
  unknownIngredients: [],
  results: [
    {
      id: "recipe_001",
      name: "Omelet Ayam Wortel",
      description:
        "Omelet berisi ayam dan wortel, cukup satu wajan untuk sarapan yang mengenyangkan.",
      matchPercentage: 100,
      availableIngredients: ["egg", "chicken", "carrot"],
      missingIngredients: [],
      cookingTimeMinutes: 15,
      difficulty: "easy",
      servings: 2,
      ingredients: ["egg", "chicken", "carrot", "shallot", "salt", "pepper", "cooking_oil"],
      steps: [
        "Potong ayam dan wortel menjadi dadu kecil agar cepat matang.",
        "Kocok telur dalam wadah, bumbui dengan garam dan lada.",
      ],
      tags: ["sarapan", "praktis", "indonesian"],
    },
  ],
  meta: {
    count: 1,
    limit: 5,
    threshold: 30,
  },
};

/** Teks request lengkap yang ditampilkan (dan bisa di-copy) di showcase. */
export const API_EXAMPLE_REQUEST_TEXT = [
  `${API_EXAMPLE_METHOD} ${API_EXAMPLE_PATH}`,
  API_EXAMPLE_HEADERS,
  "",
  JSON.stringify(API_EXAMPLE_REQUEST, null, 2),
].join("\n");

/** Teks response lengkap yang ditampilkan (dan bisa di-copy) di showcase. */
export const API_EXAMPLE_RESPONSE_TEXT = JSON.stringify(API_EXAMPLE_RESPONSE, null, 2);
