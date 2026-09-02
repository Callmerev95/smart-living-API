import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { RecommendationSection } from "@/components/recommendations/RecommendationSection";
import { content } from "@/lib/constants/content";
import type { RecommendationResponse } from "@/types/api";

function result(id: string, matchPercentage: number) {
  return {
    id,
    name: `Resep ${id}`,
    description: "Deskripsi.",
    matchPercentage,
    availableIngredients: ["egg"],
    missingIngredients: ["onion"],
    cookingTimeMinutes: 15,
    difficulty: "easy" as const,
    servings: 2,
    ingredients: ["egg", "onion"],
    steps: ["a", "b", "c"],
    tags: ["praktis"],
  };
}

function response(overrides: Partial<RecommendationResponse> = {}): RecommendationResponse {
  return {
    query: { raw: ["telur", "ayam"], ingredients: ["egg", "chicken"] },
    unknownIngredients: [],
    results: [result("recipe_001", 100), result("recipe_002", 50)],
    meta: { count: 2, limit: 5, threshold: 30 },
    ...overrides,
  };
}

describe("RecommendationSection", () => {
  it("status idle merender initial state", () => {
    render(<RecommendationSection status="idle" onRetry={vi.fn()} />);
    expect(screen.getByText(content.results.initial.title)).toBeInTheDocument();
  });

  it("status loading merender skeleton", () => {
    render(<RecommendationSection status="loading" onRetry={vi.fn()} />);
    expect(screen.getByRole("status")).toHaveTextContent(content.results.loading.label);
  });

  it("status error merender error state dengan tombol retry", () => {
    render(<RecommendationSection status="error" onRetry={vi.fn()} />);
    expect(screen.getByText(content.results.error.title)).toBeInTheDocument();
  });

  it("status success merender heading jumlah dan list", () => {
    const data = response();
    render(<RecommendationSection status="success" data={data} onRetry={vi.fn()} />);
    expect(
      screen.getByText(content.results.success.heading.replace("{count}", "2")),
    ).toBeInTheDocument();
    expect(screen.getAllByRole("heading", { name: /Resep/ })).toHaveLength(2);
  });

  it("hasil 1 memakai headingSingle", () => {
    const data = response({ results: [result("recipe_001", 100)], meta: { count: 1, limit: 5, threshold: 30 } });
    render(<RecommendationSection status="success" data={data} onRetry={vi.fn()} />);
    expect(screen.getByText(content.results.success.headingSingle)).toBeInTheDocument();
  });

  it("success dengan hasil kosong merender empty state biasa", () => {
    const data = response({
      results: [],
      meta: { count: 0, limit: 5, threshold: 30 },
    });
    render(<RecommendationSection status="success" data={data} onRetry={vi.fn()} />);
    expect(screen.getByText(content.results.empty.title)).toBeInTheDocument();
  });

  it("success kosong dan semua unknown merender varian allUnknown", () => {
    const data = response({
      query: { raw: ["kangkung", "durian"], ingredients: [] },
      unknownIngredients: ["kangkung", "durian"],
      results: [],
      meta: { count: 0, limit: 5, threshold: 30 },
    });
    render(<RecommendationSection status="success" data={data} onRetry={vi.fn()} />);
    expect(screen.getByText(content.results.allUnknown.title)).toBeInTheDocument();
  });

  it("urutan hasil dari API dipertahankan", () => {
    const data = response({
      results: [result("recipe_b", 50), result("recipe_a", 100)],
    });
    render(<RecommendationSection status="success" data={data} onRetry={vi.fn()} />);
    const cards = screen.getAllByRole("heading", { name: /Resep/ });
    expect(cards[0]).toHaveTextContent("Resep recipe_b");
    expect(cards[1]).toHaveTextContent("Resep recipe_a");
  });

  it("chip normalisasi ditampilkan", () => {
    const data = response();
    render(<RecommendationSection status="success" data={data} onRetry={vi.fn()} />);
    const chips = screen.getByLabelText("Bahan yang dicari");
    expect(chips.textContent).toContain("telur");
    expect(chips.textContent).toContain("egg");
  });

  it("chip unknown ditampilkan", () => {
    const data = response({
      query: { raw: ["telur", "kangkung"], ingredients: ["egg"] },
      unknownIngredients: ["kangkung"],
    });
    render(<RecommendationSection status="success" data={data} onRetry={vi.fn()} />);
    const chips = screen.getByLabelText("Bahan yang dicari");
    expect(chips.textContent).toContain("kangkung");
    expect(chips.textContent).toContain(content.chip.unknownSuffix);
  });

  it("heading hasil diumumkan ke screen reader", () => {
    const data = response();
    render(<RecommendationSection status="success" data={data} onRetry={vi.fn()} />);
    const announcement = screen.getByRole("status");
    expect(announcement).toHaveTextContent(content.results.success.sortNote);
  });
});
