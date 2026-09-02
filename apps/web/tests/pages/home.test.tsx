import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import Home from "@/app/page";
import { content } from "@/lib/constants/content";

const RECOMMENDATIONS = {
  query: { raw: ["telur", "ayam"], ingredients: ["egg", "chicken"] },
  unknownIngredients: [],
  results: [
    {
      id: "recipe_001",
      name: "Omelet Ayam Wortel",
      description: "Omelet praktis.",
      matchPercentage: 100,
      availableIngredients: ["egg", "chicken"],
      missingIngredients: [],
      cookingTimeMinutes: 15,
      difficulty: "easy",
      servings: 2,
      ingredients: ["egg", "chicken", "salt"],
      steps: ["a", "b", "c"],
      tags: ["sarapan"],
    },
  ],
  meta: { count: 1, limit: 5, threshold: 30 },
};

const DICTIONARY = {
  ingredients: [
    {
      name: "egg",
      displayName: "Telur",
      aliases: ["telur"],
      category: "protein",
      staple: false,
    },
    {
      name: "chicken",
      displayName: "Ayam",
      aliases: ["ayam"],
      category: "protein",
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

/**
 * Halaman memanggil dua endpoint: kamus bahan (untuk chip) dan rekomendasi.
 * Mock dipilih berdasarkan URL agar mencerminkan perilaku nyata.
 */
function mockRoutes(options: {
  recommendations?: () => Promise<Response> | Response;
  dictionary?: () => Promise<Response> | Response;
}) {
  const fetchMock = vi.fn().mockImplementation((url: string) => {
    if (url.includes("/ingredients")) {
      return Promise.resolve(
        options.dictionary ? options.dictionary() : jsonResponse(DICTIONARY),
      );
    }
    return Promise.resolve(
      options.recommendations ? options.recommendations() : jsonResponse(RECOMMENDATIONS),
    );
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

beforeEach(() => {
  vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "http://api.test");
});

afterEach(() => {
  vi.unstubAllEnvs();
  vi.restoreAllMocks();
});

describe("Halaman utama", () => {
  it("merender hero, input, dan initial state", () => {
    mockRoutes({});
    render(<Home />);
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(content.hero.title);
    expect(screen.getByLabelText(content.input.label)).toBeInTheDocument();
    expect(screen.getByText(content.results.initial.title)).toBeInTheDocument();
  });

  it("submit menghubungkan input ke hook dan menampilkan hasil", async () => {
    mockRoutes({});

    render(<Home />);

    await userEvent.type(screen.getByLabelText(content.input.label), "telur, ayam");
    await userEvent.click(screen.getByRole("button", { name: content.input.submit }));

    await waitFor(() =>
      expect(screen.getByText(content.results.success.headingSingle)).toBeInTheDocument(),
    );
    expect(screen.getByRole("heading", { name: "Omelet Ayam Wortel" })).toBeInTheDocument();
  });

  it("error state muncul saat request gagal, retry mengulang request", async () => {
    let attempt = 0;
    const fetchMock = mockRoutes({
      recommendations: () => {
        attempt += 1;
        if (attempt === 1) return Promise.reject(new TypeError("Failed to fetch"));
        return jsonResponse(RECOMMENDATIONS);
      },
    });

    render(<Home />);

    await userEvent.type(screen.getByLabelText(content.input.label), "telur, ayam");
    await userEvent.click(screen.getByRole("button", { name: content.input.submit }));

    await waitFor(() =>
      expect(screen.getByText(content.results.error.title)).toBeInTheDocument(),
    );

    await userEvent.click(screen.getByRole("button", { name: content.results.error.retry }));

    await waitFor(() =>
      expect(screen.getByText(content.results.success.headingSingle)).toBeInTheDocument(),
    );
    expect(attempt).toBe(2);
    expect(fetchMock).toHaveBeenCalled();
  });

  it("chip normalisasi memakai displayName dari kamus", async () => {
    mockRoutes({});

    render(<Home />);
    await userEvent.type(screen.getByLabelText(content.input.label), "telur, ayam");
    await userEvent.click(screen.getByRole("button", { name: content.input.submit }));

    await waitFor(() => {
      const chips = screen.getByLabelText(content.results.chipsLabel);
      expect(chips.textContent).toContain("Telur");
      expect(chips.textContent).toContain("Ayam");
    });
  });

  it("kamus gagal dimuat tidak menghalangi hasil", async () => {
    mockRoutes({
      dictionary: () => Promise.reject(new TypeError("Failed to fetch")),
    });

    render(<Home />);
    await userEvent.type(screen.getByLabelText(content.input.label), "telur, ayam");
    await userEvent.click(screen.getByRole("button", { name: content.input.submit }));

    await waitFor(() =>
      expect(screen.getByText(content.results.success.headingSingle)).toBeInTheDocument(),
    );
    const chips = screen.getByLabelText(content.results.chipsLabel);
    expect(chips.textContent).toContain("egg");
  });

  it("bahan tak dikenali tampil sebagai chip unknown", async () => {
    mockRoutes({
      recommendations: () =>
        jsonResponse({
          ...RECOMMENDATIONS,
          query: { raw: ["telur", "kangkung"], ingredients: ["egg"] },
          unknownIngredients: ["kangkung"],
        }),
    });

    render(<Home />);
    await userEvent.type(screen.getByLabelText(content.input.label), "telur, kangkung");
    await userEvent.click(screen.getByRole("button", { name: content.input.submit }));

    await waitFor(() => {
      const chips = screen.getByLabelText(content.results.chipsLabel);
      expect(chips.textContent).toContain("kangkung");
      expect(chips.textContent).toContain(content.chip.unknownSuffix);
    });
  });

  it("input kosong tidak memicu request rekomendasi", async () => {
    const fetchMock = mockRoutes({});

    render(<Home />);
    await userEvent.click(screen.getByRole("button", { name: content.input.submit }));

    const recommendationCalls = fetchMock.mock.calls.filter(([url]) =>
      String(url).includes("/recommendations"),
    );
    expect(recommendationCalls).toHaveLength(0);
    expect(screen.getByRole("alert")).toHaveTextContent(content.input.validation.empty);
  });

  it("page tidak memanggil fetch langsung", () => {
    expect(Home.toString()).not.toContain("fetch(");
  });
});
