"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { RecipeDetail } from "@/components/recipes/RecipeDetail";
import { Alert } from "@/components/ui/Alert";
import { Spinner } from "@/components/ui/Spinner";
import { ApiClientError } from "@/lib/api/client";
import { getRecipe } from "@/lib/api/recipes";
import { content } from "@/lib/constants/content";
import type { Recipe } from "@/types/api";

type State =
  | { status: "loading" }
  | { status: "success"; recipe: Recipe }
  | { status: "not-found" }
  | { status: "error"; message: string };

/**
 * Pemuat detail resep.
 *
 * Data diambil lewat `lib/api/recipes.ts` — bukan `fetch` langsung di komponen
 * (`docs/component-architecture.md` §11).
 */
export function RecipeDetailLoader({ recipeId }: { recipeId: string }) {
  const [state, setState] = useState<State>({ status: "loading" });

  useEffect(() => {
    const controller = new AbortController();

    getRecipe(recipeId, { signal: controller.signal })
      .then((recipe) => {
        if (!controller.signal.aborted) {
          setState({ status: "success", recipe });
        }
      })
      .catch((error: unknown) => {
        if (controller.signal.aborted) return;

        if (error instanceof ApiClientError && error.code === "RECIPE_NOT_FOUND") {
          setState({ status: "not-found" });
          return;
        }

        setState({
          status: "error",
          message:
            error instanceof ApiClientError ? error.userMessage : content.errors.unknown,
        });
      });

    return () => controller.abort();
  }, [recipeId]);

  return (
    <div className="flex flex-col gap-6">
      <Link
        href="/"
        className="inline-flex w-fit items-center text-sm font-medium text-zinc-600 underline-offset-4 hover:underline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-amber-500"
      >
        {content.detail.back}
      </Link>

      {state.status === "loading" && (
        <p className="flex items-center gap-2 text-sm text-zinc-600">
          <Spinner />
          {content.detail.loading}
        </p>
      )}

      {state.status === "not-found" && (
        <Alert tone="info" title={content.detail.notFound.title}>
          {content.detail.notFound.body}
        </Alert>
      )}

      {state.status === "error" && (
        <Alert tone="error" title={content.results.error.title}>
          {state.message}
        </Alert>
      )}

      {state.status === "success" && <RecipeDetail recipe={state.recipe} />}
    </div>
  );
}
