import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { ApiClientError, userMessageFor } from "@/lib/api/client";
import { getIngredients } from "@/lib/api/ingredients";
import { getRecipe } from "@/lib/api/recipes";
import { getRecommendations } from "@/lib/api/recommendations";
import { content } from "@/lib/constants/content";

const BASE_URL = "http://api.test";

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

function apiErrorResponse(code: string, message: string, status: number): Response {
  return jsonResponse({ error: { code, message, details: null } }, status);
}

const SUCCESS_PAYLOAD = {
  query: { raw: ["telur"], ingredients: ["egg"] },
  unknownIngredients: [],
  results: [],
  meta: { count: 0, limit: 5, threshold: 30 },
};

beforeEach(() => {
  vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", BASE_URL);
});

afterEach(() => {
  vi.unstubAllEnvs();
  vi.restoreAllMocks();
});

describe("base URL", () => {
  it("dibaca dari env, bukan hardcode", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(SUCCESS_PAYLOAD));
    vi.stubGlobal("fetch", fetchMock);

    await getRecommendations(["telur"]);

    expect(fetchMock.mock.calls[0][0]).toBe(`${BASE_URL}/api/v1/recommendations`);
  });

  it("trailing slash pada env tidak menghasilkan URL ganda", async () => {
    vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", `${BASE_URL}/`);
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(SUCCESS_PAYLOAD));
    vi.stubGlobal("fetch", fetchMock);

    await getRecommendations(["telur"]);

    expect(fetchMock.mock.calls[0][0]).toBe(`${BASE_URL}/api/v1/recommendations`);
  });

  it("env kosong menghasilkan error yang jelas", async () => {
    vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "");
    vi.stubGlobal("fetch", vi.fn());

    await expect(getRecommendations(["telur"])).rejects.toBeInstanceOf(ApiClientError);
  });
});

describe("getRecommendations", () => {
  it("mengirim POST dengan body JSON", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(SUCCESS_PAYLOAD));
    vi.stubGlobal("fetch", fetchMock);

    await getRecommendations(["telur", "ayam"], { limit: 3 });

    const [, init] = fetchMock.mock.calls[0];
    expect(init.method).toBe("POST");
    expect(init.headers["Content-Type"]).toBe("application/json");
    expect(JSON.parse(init.body)).toEqual({ ingredients: ["telur", "ayam"], limit: 3 });
  });

  it("limit dihilangkan bila tidak diberikan", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(SUCCESS_PAYLOAD));
    vi.stubGlobal("fetch", fetchMock);

    await getRecommendations(["telur"]);

    expect(JSON.parse(fetchMock.mock.calls[0][1].body)).toEqual({ ingredients: ["telur"] });
  });

  it("mengembalikan payload sukses", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse(SUCCESS_PAYLOAD)));
    await expect(getRecommendations(["telur"])).resolves.toEqual(SUCCESS_PAYLOAD);
  });
});

describe("error mapping", () => {
  it("400 INVALID_INGREDIENTS memakai pesan dari content", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(apiErrorResponse("INVALID_INGREDIENTS", "kosong", 400)),
    );

    const error = await getRecommendations([]).catch((e: unknown) => e);
    expect(error).toBeInstanceOf(ApiClientError);
    expect((error as ApiClientError).code).toBe("INVALID_INGREDIENTS");
    expect((error as ApiClientError).status).toBe(400);
    expect((error as ApiClientError).userMessage).toBe(content.errors.INVALID_INGREDIENTS);
  });

  it("404 RECIPE_NOT_FOUND dipetakan", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(apiErrorResponse("RECIPE_NOT_FOUND", "tidak ada", 404)),
    );

    const error = await getRecipe("recipe_999").catch((e: unknown) => e);
    expect((error as ApiClientError).code).toBe("RECIPE_NOT_FOUND");
    expect((error as ApiClientError).userMessage).toBe(content.errors.RECIPE_NOT_FOUND);
  });

  it("422 VALIDATION_ERROR dipetakan", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(apiErrorResponse("VALIDATION_ERROR", "limit salah", 422)),
    );

    const error = await getRecommendations(["telur"]).catch((e: unknown) => e);
    expect((error as ApiClientError).userMessage).toBe(content.errors.VALIDATION_ERROR);
  });

  it("500 INTERNAL_ERROR dipetakan", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(apiErrorResponse("INTERNAL_ERROR", "boom", 500)),
    );

    const error = await getRecommendations(["telur"]).catch((e: unknown) => e);
    expect((error as ApiClientError).userMessage).toBe(content.errors.INTERNAL_ERROR);
  });

  it("network failure dipisahkan dari error HTTP", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("Failed to fetch")));

    const error = await getRecommendations(["telur"]).catch((e: unknown) => e);
    expect((error as ApiClientError).code).toBe("NETWORK_ERROR");
    expect((error as ApiClientError).status).toBeNull();
    expect((error as ApiClientError).userMessage).toBe(content.errors.network);
  });

  it("error code tak dikenal memakai pesan fallback", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(apiErrorResponse("SOMETHING_NEW", "?", 418)),
    );

    const error = await getRecommendations(["telur"]).catch((e: unknown) => e);
    expect((error as ApiClientError).userMessage).toBe(content.errors.unknown);
  });

  it("response error tanpa envelope tetap ditangani", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("<html>502</html>", { status: 502 })));

    const error = await getRecommendations(["telur"]).catch((e: unknown) => e);
    expect((error as ApiClientError).code).toBe("UNKNOWN_ERROR");
    expect((error as ApiClientError).status).toBe(502);
  });

  it("response 200 dengan body bukan JSON ditangani", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("bukan json", { status: 200 })));

    const error = await getRecommendations(["telur"]).catch((e: unknown) => e);
    expect((error as ApiClientError).code).toBe("UNKNOWN_ERROR");
  });
});

describe("userMessageFor", () => {
  it("memetakan semua error code kontrak", () => {
    expect(userMessageFor("INVALID_INGREDIENTS")).toBe(content.errors.INVALID_INGREDIENTS);
    expect(userMessageFor("VALIDATION_ERROR")).toBe(content.errors.VALIDATION_ERROR);
    expect(userMessageFor("RECIPE_NOT_FOUND")).toBe(content.errors.RECIPE_NOT_FOUND);
    expect(userMessageFor("INGREDIENT_NOT_FOUND")).toBe(content.errors.INGREDIENT_NOT_FOUND);
    expect(userMessageFor("INTERNAL_ERROR")).toBe(content.errors.INTERNAL_ERROR);
    expect(userMessageFor("NETWORK_ERROR")).toBe(content.errors.network);
    expect(userMessageFor("APA_PUN")).toBe(content.errors.unknown);
  });
});

describe("timeout & abort", () => {
  it("request dibatalkan setelah timeout", async () => {
    const fetchMock = vi.fn().mockImplementation((_url, init: RequestInit) => {
      return new Promise((_resolve, reject) => {
        init.signal?.addEventListener("abort", () => reject(new DOMException("aborted", "AbortError")));
      });
    });
    vi.stubGlobal("fetch", fetchMock);

    const error = await getRecommendations(["telur"]).catch((e: unknown) => e);
    expect((error as ApiClientError).code).toBe("NETWORK_ERROR");
  }, 20_000);

  it("signal dari caller diteruskan", async () => {
    const controller = new AbortController();
    const fetchMock = vi.fn().mockImplementation((_url, init: RequestInit) => {
      return new Promise((_resolve, reject) => {
        init.signal?.addEventListener("abort", () => reject(new DOMException("aborted", "AbortError")));
      });
    });
    vi.stubGlobal("fetch", fetchMock);

    const promise = getRecommendations(["telur"], { signal: controller.signal });
    controller.abort();

    const error = await promise.catch((e: unknown) => e);
    expect((error as ApiClientError).code).toBe("NETWORK_ERROR");
  });
});

describe("endpoint lain", () => {
  it("getRecipe menyusun path dengan encoding", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({ id: "recipe_001" }));
    vi.stubGlobal("fetch", fetchMock);

    await getRecipe("recipe 001");

    expect(fetchMock.mock.calls[0][0]).toBe(`${BASE_URL}/api/v1/recipes/recipe%20001`);
  });

  it("getIngredients memanggil endpoint yang benar", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValue(jsonResponse({ ingredients: [], meta: { count: 0 } }));
    vi.stubGlobal("fetch", fetchMock);

    await getIngredients();

    expect(fetchMock.mock.calls[0][0]).toBe(`${BASE_URL}/api/v1/ingredients`);
  });
});
