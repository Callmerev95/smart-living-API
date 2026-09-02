import { useCallback, useEffect, useRef, useState } from "react";

import { getRecommendations } from "@/lib/api/recommendations";
import type { RecommendationResponse } from "@/types/api";

export type RecommendationStatus = "idle" | "loading" | "success" | "error";

type RecommendationErrorState = {
  message: string;
};

type State =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "success"; data: RecommendationResponse }
  | { status: "error"; error: RecommendationErrorState };

const initialState: State = { status: "idle" };

/**
 * State request rekomendasi (`docs/component-architecture.md` §12).
 *
 * Empat status eksplisit, bukan kombinasi boolean `isLoading`/`isError` yang bisa
 * inkonsisten. Hook TIDAK menghitung/menormalisasi/mengurutkan apa pun — semua
 * hasil berasal dari API. Request berurutan dijaga dengan AbortController.
 */
export function useRecommendations() {
  const [state, setState] = useState<State>(initialState);
  const abortRef = useRef<AbortController | null>(null);

  // Batalkan request yang masih berjalan saat komponen unmount.
  useEffect(() => {
    return () => {
      abortRef.current?.abort();
    };
  }, []);

  const submit = useCallback(async (ingredients: string[]) => {
    // Batalkan request lama agar hasilnya tidak menimpa request baru (race condition).
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setState({ status: "loading" });

    try {
      const data = await getRecommendations(ingredients, { signal: controller.signal });
      if (!controller.signal.aborted) {
        setState({ status: "success", data });
      }
    } catch (error) {
      if (controller.signal.aborted) return;
      setState({
        status: "error",
        error: {
          message:
            error instanceof Error && "userMessage" in error
              ? String((error as { userMessage: string }).userMessage)
              : "Terjadi kesalahan. Coba lagi.",
        },
      });
    }
  }, []);

  const reset = useCallback(() => {
    abortRef.current?.abort();
    abortRef.current = null;
    setState(initialState);
  }, []);

  return { status: state.status, state, submit, reset };
}
