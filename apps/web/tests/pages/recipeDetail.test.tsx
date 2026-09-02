import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { RecipeDetailLoader } from "@/components/recipes/RecipeDetailLoader";
import { content } from "@/lib/constants/content";

const RECIPE = {
  id: "recipe_001",
  name: "Omelet Ayam Wortel",
  description: "Omelet praktis.",
  ingredients: [{ name: "egg", required: true }],
  cookingTimeMinutes: 15,
  difficulty: "easy",
  servings: 2,
  steps: ["Kocok telur.", "Tumis ayam.", "Sajikan."],
  tags: ["sarapan"],
  source: "original",
};

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

beforeEach(() => {
  vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "http://api.test");
});

afterEach(() => {
  vi.unstubAllEnvs();
  vi.restoreAllMocks();
});

describe("RecipeDetailLoader", () => {
  it("menampilkan loading lalu detail resep", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse(RECIPE)));

    render(<RecipeDetailLoader recipeId="recipe_001" />);

    expect(screen.getByText(content.detail.loading)).toBeInTheDocument();

    await waitFor(() =>
      expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(
        "Omelet Ayam Wortel",
      ),
    );
  });

  it("mengambil data lewat lib/api dengan path yang benar", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(RECIPE));
    vi.stubGlobal("fetch", fetchMock);

    render(<RecipeDetailLoader recipeId="recipe_042" />);

    await waitFor(() =>
      expect(fetchMock.mock.calls[0][0]).toBe("http://api.test/api/v1/recipes/recipe_042"),
    );
  });

  it("404 menampilkan not-found dengan copy §B.7", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        jsonResponse(
          { error: { code: "RECIPE_NOT_FOUND", message: "tidak ada", details: null } },
          404,
        ),
      ),
    );

    render(<RecipeDetailLoader recipeId="recipe_999" />);

    await waitFor(() =>
      expect(screen.getByText(content.detail.notFound.title)).toBeInTheDocument(),
    );
    expect(screen.getByText(content.detail.notFound.body)).toBeInTheDocument();
  });

  it("network error menampilkan pesan koneksi", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("Failed to fetch")));

    render(<RecipeDetailLoader recipeId="recipe_001" />);

    await waitFor(() => expect(screen.getByText(content.errors.network)).toBeInTheDocument());
  });

  it("500 menampilkan pesan internal error", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        jsonResponse({ error: { code: "INTERNAL_ERROR", message: "boom", details: null } }, 500),
      ),
    );

    render(<RecipeDetailLoader recipeId="recipe_001" />);

    await waitFor(() =>
      expect(screen.getByText(content.errors.INTERNAL_ERROR)).toBeInTheDocument(),
    );
  });

  it("menyediakan tautan kembali ke hasil", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse(RECIPE)));

    render(<RecipeDetailLoader recipeId="recipe_001" />);

    const back = screen.getByRole("link", { name: content.detail.back });
    expect(back).toHaveAttribute("href", "/");
  });

  it("tautan kembali bisa difokus dengan keyboard", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse(RECIPE)));

    render(<RecipeDetailLoader recipeId="recipe_001" />);

    await userEvent.tab();
    expect(screen.getByRole("link", { name: content.detail.back })).toHaveFocus();
  });
});
