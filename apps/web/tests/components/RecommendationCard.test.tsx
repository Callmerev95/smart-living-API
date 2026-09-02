import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { RecommendationCard } from "@/components/recommendations/RecommendationCard";
import { content } from "@/lib/constants/content";
import type { Recommendation } from "@/types/api";

function recommendation(overrides: Partial<Recommendation> = {}): Recommendation {
  return {
    id: "recipe_001",
    name: "Omelet Ayam Wortel",
    description: "Omelet praktis dengan ayam dan wortel.",
    matchPercentage: 100,
    availableIngredients: ["egg", "chicken", "carrot"],
    missingIngredients: [],
    cookingTimeMinutes: 15,
    difficulty: "easy",
    servings: 2,
    ingredients: ["egg", "chicken", "carrot", "salt", "cooking_oil"],
    steps: ["Kocok telur.", "Tumis ayam.", "Sajikan."],
    tags: ["sarapan", "praktis"],
    ...overrides,
  };
}

describe("RecommendationCard", () => {
  it("menampilkan nama resep sebagai heading", () => {
    render(<RecommendationCard recommendation={recommendation()} />);
    expect(
      screen.getByRole("heading", { name: "Omelet Ayam Wortel" }),
    ).toBeInTheDocument();
  });

  it("menampilkan badge kecocokan", () => {
    render(<RecommendationCard recommendation={recommendation({ matchPercentage: 75 })} />);
    expect(screen.getByText("75% cocok")).toBeInTheDocument();
  });

  it("menampilkan bahan yang sudah ada", () => {
    render(<RecommendationCard recommendation={recommendation()} />);
    expect(screen.getByText(content.card.availableLabel)).toBeInTheDocument();
    expect(screen.getByText("egg, chicken, carrot")).toBeInTheDocument();
  });

  it("missing kosong menampilkan pesan khusus, bukan list kosong", () => {
    render(<RecommendationCard recommendation={recommendation({ missingIngredients: [] })} />);
    expect(screen.getByText(content.card.missingEmpty)).toBeInTheDocument();
  });

  it("missing terisi menampilkan daftarnya", () => {
    render(
      <RecommendationCard recommendation={recommendation({ missingIngredients: ["onion"] })} />,
    );
    expect(screen.getByText("onion")).toBeInTheDocument();
    expect(screen.queryByText(content.card.missingEmpty)).not.toBeInTheDocument();
  });

  it("label available/missing berupa teks, bukan hanya warna", () => {
    render(<RecommendationCard recommendation={recommendation()} />);
    expect(screen.getByText(content.card.availableLabel)).toBeInTheDocument();
    expect(screen.getByText(content.card.missingLabel)).toBeInTheDocument();
  });

  it("menerjemahkan difficulty easy ke Mudah", () => {
    render(<RecommendationCard recommendation={recommendation({ difficulty: "easy" })} />);
    expect(screen.getByText(/Mudah/)).toBeInTheDocument();
  });

  it("menerjemahkan difficulty medium ke Sedang", () => {
    render(<RecommendationCard recommendation={recommendation({ difficulty: "medium" })} />);
    expect(screen.getByText(/Sedang/)).toBeInTheDocument();
  });

  it("menerjemahkan difficulty hard ke Sulit", () => {
    render(<RecommendationCard recommendation={recommendation({ difficulty: "hard" })} />);
    expect(screen.getByText(/Sulit/)).toBeInTheDocument();
  });

  it("menampilkan waktu dan porsi terinterpolasi", () => {
    render(
      <RecommendationCard
        recommendation={recommendation({ cookingTimeMinutes: 25, servings: 4 })}
      />,
    );
    const meta = screen.getByText(/25 menit/);
    expect(meta).toHaveTextContent("4 porsi");
    expect(meta.textContent).not.toContain("{minutes}");
  });

  it("CTA mengarah ke halaman detail resep", () => {
    render(<RecommendationCard recommendation={recommendation({ id: "recipe_042" })} />);
    expect(screen.getByRole("link", { name: content.card.cta })).toHaveAttribute(
      "href",
      "/recipes/recipe_042",
    );
  });

  it("tidak ada placeholder yang bocor", () => {
    const { container } = render(<RecommendationCard recommendation={recommendation()} />);
    expect(container.textContent).not.toMatch(/\{\w+\}/);
  });
});
