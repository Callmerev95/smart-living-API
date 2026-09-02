import { act, renderHook, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { useIngredients } from "@/hooks/useIngredients";

const DICTIONARY = {
  ingredients: [
    {
      name: "egg",
      displayName: "Telur",
      aliases: ["telur", "telor"],
      category: "protein",
      staple: false,
    },
    {
      name: "long_bean",
      displayName: "Kacang Panjang",
      aliases: ["kacang panjang"],
      category: "vegetable",
      staple: false,
    },
  ],
  meta: { count: 2 },
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

describe("useIngredients", () => {
  it("membangun peta canonical -> displayName", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse(DICTIONARY)));

    const { result } = renderHook(() => useIngredients());

    await waitFor(() => expect(result.current.ready).toBe(true));
    expect(result.current.displayNames).toEqual({
      egg: "Telur",
      long_bean: "Kacang Panjang",
    });
  });

  it("memanggil endpoint ingredients lewat lib/api", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(DICTIONARY));
    vi.stubGlobal("fetch", fetchMock);

    const { result } = renderHook(() => useIngredients());

    await waitFor(() => expect(result.current.ready).toBe(true));
    expect(fetchMock.mock.calls[0][0]).toBe("http://api.test/api/v1/ingredients");
  });

  it("hanya satu request per mount", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(DICTIONARY));
    vi.stubGlobal("fetch", fetchMock);

    const { result, rerender } = renderHook(() => useIngredients());
    await waitFor(() => expect(result.current.ready).toBe(true));

    rerender();
    rerender();

    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("kegagalan fetch tidak merusak halaman — peta kosong", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("Failed to fetch")));

    const { result } = renderHook(() => useIngredients());

    await waitFor(() => expect(result.current.ready).toBe(true));
    expect(result.current.displayNames).toEqual({});
  });

  it("error HTTP juga ditoleransi", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        jsonResponse({ error: { code: "INTERNAL_ERROR", message: "boom", details: null } }, 500),
      ),
    );

    const { result } = renderHook(() => useIngredients());

    await waitFor(() => expect(result.current.ready).toBe(true));
    expect(result.current.displayNames).toEqual({});
  });

  it("peta kosong sebelum fetch selesai", () => {
    vi.stubGlobal("fetch", vi.fn().mockReturnValue(new Promise<Response>(() => {})));

    const { result } = renderHook(() => useIngredients());

    expect(result.current.ready).toBe(false);
    expect(result.current.displayNames).toEqual({});
  });

  it("request dibatalkan saat unmount", async () => {
    let capturedSignal: AbortSignal | undefined;
    vi.stubGlobal(
      "fetch",
      vi.fn().mockImplementation((_url: string, init: RequestInit) => {
        capturedSignal = init.signal ?? undefined;
        return new Promise<Response>(() => {});
      }),
    );

    const { unmount } = renderHook(() => useIngredients());
    await act(async () => {
      unmount();
    });

    expect(capturedSignal?.aborted).toBe(true);
  });
});
