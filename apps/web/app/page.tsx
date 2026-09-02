"use client";

import { useState } from "react";

import { HeroSection } from "@/components/HeroSection";
import { IngredientInput } from "@/components/ingredients/IngredientInput";
import { RecommendationSection } from "@/components/recommendations/RecommendationSection";
import { useIngredients } from "@/hooks/useIngredients";
import { useRecommendations } from "@/hooks/useRecommendations";

/**
 * Halaman utama — hanya komposisi dan wiring state
 * (`docs/component-architecture.md` §5.1). Tidak ada algoritma di sini.
 */
export default function Home() {
  const { status, state, submit, reset } = useRecommendations();
  const { displayNames } = useIngredients();
  const [lastIngredients, setLastIngredients] = useState<string[]>([]);

  function handleSubmit(ingredients: string[]) {
    setLastIngredients(ingredients);
    void submit(ingredients);
  }

  function handleRetry() {
    if (lastIngredients.length > 0) {
      void submit(lastIngredients);
      return;
    }
    reset();
  }

  return (
    <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col gap-10 px-6 py-12">
      <HeroSection />
      <IngredientInput onSubmit={handleSubmit} loading={status === "loading"} />
      <RecommendationSection
        status={status}
        data={state.status === "success" ? state.data : undefined}
        displayNames={displayNames}
        onRetry={handleRetry}
      />
    </main>
  );
}
