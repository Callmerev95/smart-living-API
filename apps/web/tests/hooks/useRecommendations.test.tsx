import { act, renderHook } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { useRecommendations } from "@/hooks/useRecommendations";

const SUCCESS = {
  query: { raw: ["telur"], ingredients: ["egg"] },
  unknownIngredients: [],
  results: [{ id: "recipe_001", name: "Omelet" }],
  meta: { count: 1, limit: 5, threshold: 30 },
};

beforeEach(() => {
  vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "http://api.test");
});

afterEach(() => {
  vi.unstubAllEnvs();
  vi.restoreAllMocks();
});

describe("status transisi", () => {
  it("mulai dari idle", () => {
    const { result } = renderHook(() => useRecommendations());
    expect(result.current.status).toBe("idle");
  });

  it("loading saat submit, success setelah selesai", async () => {
    let resolveFetch!: (value: Response) => void;
    vi.stubGlobal(
      "fetch",
      vi.fn().mockReturnValue(
        new Promise<Response>((resolve) => {
          resolveFetch = resolve;
        }),
      ),
    );

    const { result } = renderHook(() => useRecommendations());

    let submitPromise!: Promise<void>;
    act(() => {
      submitPromise = result.current.submit(["telur"]);
    });

    expect(result.current.status).toBe("loading");

    await act(async () => {
      resolveFetch(new Response(JSON.stringify(SUCCESS), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }));
      await submitPromise;
    });

    expect(result.current.status).toBe("success");
    expect(result.current.state).toMatchObject({ status: "success" });
  });

  it("error saat request gagal", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockRejectedValue(new TypeError("Failed to fetch")),
    );

    const { result } = renderHook(() => useRecommendations());

    await act(async () => {
      await result.current.submit(["telur"]);
    });

    expect(result.current.status).toBe("error");
  });

  it("error memuat userMessage dari ApiClientError", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({ error: { code: "INVALID_INGREDIENTS", message: "x", details: null } }),
          { status: 400, headers: { "Content-Type": "application/json" } },
        ),
      ),
    );

    const { result } = renderHook(() => useRecommendations());

    await act(async () => {
      await result.current.submit([]);
    });

    expect(result.current.status).toBe("error");
    const errorState = result.current.state;
    if (errorState.status === "error") {
      expect(errorState.error.message).toBe(
        "Tambahkan setidaknya satu bahan untuk mencari resep.",
      );
    }
  });

  it("reset mengembalikan ke idle", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify(SUCCESS), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      ),
    );

    const { result } = renderHook(() => useRecommendations());

    await act(async () => {
      await result.current.submit(["telur"]);
    });
    expect(result.current.status).toBe("success");

    act(() => result.current.reset());
    expect(result.current.status).toBe("idle");
  });
});

describe("data Delta v1.1 sampai ke UI", () => {
  it("data memuat query, unknownIngredients, results", async () => {
    const payload = {
      query: { raw: ["telur", "kangkung"], ingredients: ["egg"] },
      unknownIngredients: ["kangkung"],
      results: [],
      meta: { count: 0, limit: 5, threshold: 30 },
    };
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify(payload), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      ),
    );

    const { result } = renderHook(() => useRecommendations());

    await act(async () => {
      await result.current.submit(["telur", "kangkung"]);
    });

    const state = result.current.state;
    if (state.status === "success") {
      expect(state.data.query.raw).toEqual(["telur", "kangkung"]);
      expect(state.data.unknownIngredients).toEqual(["kangkung"]);
    }
  });
});

describe("race condition", () => {
  it("hasil request lama tidak menimpa request baru", async () => {
    const resolvers: Array<(v: Response) => void> = [];
    vi.stubGlobal(
      "fetch",
      vi.fn().mockImplementation(
        () =>
          new Promise<Response>((resolve) => {
            resolvers.push(resolve);
          }),
      ),
    );

    const { result } = renderHook(() => useRecommendations());

    let first!: Promise<void>;
    act(() => {
      first = result.current.submit(["telur"]);
    });

    let second!: Promise<void>;
    act(() => {
      second = result.current.submit(["ayam"]);
    });

    // Request kedua selesai duluan (yang paling relevan).
    await act(async () => {
      resolvers[1](
        new Response(JSON.stringify({ ...SUCCESS, query: { raw: ["ayam"], ingredients: ["chicken"] } }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      );
      await second;
    });

    // Request pertama selesai belakangan — tidak boleh menimpa state success.
    await act(async () => {
      resolvers[0](
        new Response(JSON.stringify({ ...SUCCESS, query: { raw: ["telur"], ingredients: ["egg"] } }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      );
      await first;
    });

    const state = result.current.state;
    if (state.status === "success") {
      expect(state.data.query.ingredients).toEqual(["chicken"]);
    } else {
      expect(state.status).toBe("success");
    }
  });
});

describe("boundary", () => {
  it("hook tidak memanggil fetch langsung — lewat lib/api", () => {
    const source = useRecommendations.toString();
    expect(source).not.toContain("fetch(");
  });
});
