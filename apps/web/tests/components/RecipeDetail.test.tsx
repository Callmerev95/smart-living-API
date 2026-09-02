import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { RecipeDetail } from "@/components/recipes/RecipeDetail";
import { content } from "@/lib/constants/content";
import type { Recipe } from "@/types/api";

function recipe(overrides: Partial<Recipe> = {}): Recipe {
  return {
    id: "recipe_001",
    name: "Omelet Ayam Wortel",
    description: "Omelet praktis dengan ayam dan wortel.",
    ingredients: [
      { name: "egg", required: true },
      { name: "chicken", required: true },
      { name: "shallot", required: false },
      { name: "salt", required: true },
    ],
    cookingTimeMinutes: 15,
    difficulty: "easy",
    servings: 2,
    steps: ["Kocok telur.", "Tumis ayam.", "Sajikan hangat."],
    tags: ["sarapan", "praktis"],
    source: "original",
    ...overrides,
  };
}

describe("RecipeDetail", () => {
  it("menampilkan nama sebagai h1", () => {
    render(<RecipeDetail recipe={recipe()} />);
    expect(
      screen.getByRole("heading", { level: 1, name: "Omelet Ayam Wortel" }),
    ).toBeInTheDocument();
  });

  it("menampilkan deskripsi", () => {
    render(<RecipeDetail recipe={recipe()} />);
    expect(screen.getByText("Omelet praktis dengan ayam dan wortel.")).toBeInTheDocument();
  });

  it("menampilkan semua bahan", () => {
    render(<RecipeDetail recipe={recipe()} />);
    expect(screen.getByText("egg")).toBeInTheDocument();
    expect(screen.getByText("chicken")).toBeInTheDocument();
    expect(screen.getByText("salt")).toBeInTheDocument();
  });

  it("bahan opsional diberi suffix", () => {
    render(<RecipeDetail recipe={recipe()} />);
    expect(screen.getByText(content.detail.optionalSuffix)).toBeInTheDocument();
  });

  it("hanya bahan opsional yang diberi suffix", () => {
    render(<RecipeDetail recipe={recipe()} />);
    expect(screen.getAllByText(content.detail.optionalSuffix)).toHaveLength(1);
  });

  it("menampilkan staple note untuk transparansi Delta 1", () => {
    render(<RecipeDetail recipe={recipe()} />);
    expect(screen.getByText(content.detail.stapleNote)).toBeInTheDocument();
  });

  it("bahan dirender sebagai unordered list", () => {
    const { container } = render(<RecipeDetail recipe={recipe()} />);
    const lists = container.querySelectorAll("ul");
    expect(lists).toHaveLength(1);
    expect(lists[0].children).toHaveLength(4);
  });

  it("langkah dirender sebagai ordered list, nomor dari markup", () => {
    const { container } = render(<RecipeDetail recipe={recipe()} />);
    const ordered = container.querySelector("ol");
    expect(ordered).not.toBeNull();
    expect(ordered?.children).toHaveLength(3);
    expect(ordered?.textContent).not.toMatch(/^1\./);
  });

  it("menampilkan waktu, difficulty, dan porsi", () => {
    render(<RecipeDetail recipe={recipe({ cookingTimeMinutes: 25, servings: 3 })} />);
    const meta = screen.getByText(/25 menit/);
    expect(meta).toHaveTextContent("Mudah");
    expect(meta).toHaveTextContent("3 porsi");
  });

  it("menampilkan tags", () => {
    render(<RecipeDetail recipe={recipe()} />);
    expect(screen.getByText("sarapan")).toBeInTheDocument();
    expect(screen.getByText("praktis")).toBeInTheDocument();
  });

  it("heading section memakai level 2 — tidak melompat dari h1", () => {
    render(<RecipeDetail recipe={recipe()} />);
    const headings = screen.getAllByRole("heading", { level: 2 });
    expect(headings.map((h) => h.textContent)).toEqual([
      content.detail.metaHeading,
      content.detail.ingredientsHeading,
      content.detail.stepsHeading,
    ]);
  });

  it("tidak ada placeholder yang bocor", () => {
    const { container } = render(<RecipeDetail recipe={recipe()} />);
    expect(container.textContent).not.toMatch(/\{\w+\}/);
  });
});
