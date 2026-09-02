import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import Home from "@/app/page";
import { content } from "@/lib/constants/content";

const RESPONSE = {
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

describe("Halaman utama", () => {
  it("merender hero, input, dan initial state", () => {
    render(<Home />);
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(content.hero.title);
    expect(screen.getByLabelText(content.input.label)).toBeInTheDocument();
    expect(screen.getByText(content.results.initial.title)).toBeInTheDocument();
  });

  it("submit menghubungkan input ke hook dan menampilkan hasil", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse(RESPONSE)));

    render(<Home />);

    await userEvent.type(screen.getByLabelText(content.input.label), "telur, ayam");
    await userEvent.click(screen.getByRole("button", { name: content.input.submit }));

    await waitFor(() =>
      expect(screen.getByText(content.results.success.headingSingle)).toBeInTheDocument(),
    );
    expect(screen.getByRole("heading", { name: "Omelet Ayam Wortel" })).toBeInTheDocument();
  });

  it("error state muncul saat request gagal, retry mengulang request", async () => {
    const fetchMock = vi
      .fn()
      .mockRejectedValueOnce(new TypeError("Failed to fetch"))
      .mockResolvedValueOnce(jsonResponse(RESPONSE));
    vi.stubGlobal("fetch", fetchMock);

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
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });

  it("chip normalisasi tampil setelah hasil diterima", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse(RESPONSE)));

    render(<Home />);
    await userEvent.type(screen.getByLabelText(content.input.label), "telur, ayam");
    await userEvent.click(screen.getByRole("button", { name: content.input.submit }));

    await waitFor(() => {
      const chips = screen.getByLabelText("Bahan yang dicari");
      expect(chips.textContent).toContain("telur");
      expect(chips.textContent).toContain("egg");
    });
  });

  it("bahan tak dikenali tampil sebagai chip unknown", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        jsonResponse({
          ...RESPONSE,
          query: { raw: ["telur", "kangkung"], ingredients: ["egg"] },
          unknownIngredients: ["kangkung"],
        }),
      ),
    );

    render(<Home />);
    await userEvent.type(screen.getByLabelText(content.input.label), "telur, kangkung");
    await userEvent.click(screen.getByRole("button", { name: content.input.submit }));

    await waitFor(() => {
      const chips = screen.getByLabelText("Bahan yang dicari");
      expect(chips.textContent).toContain("kangkung");
      expect(chips.textContent).toContain(content.chip.unknownSuffix);
    });
  });

  it("input kosong tidak memicu request", async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);

    render(<Home />);
    await userEvent.click(screen.getByRole("button", { name: content.input.submit }));

    expect(fetchMock).not.toHaveBeenCalled();
    expect(screen.getByRole("alert")).toHaveTextContent(content.input.validation.empty);
  });

  it("page tidak memanggil fetch langsung", () => {
    expect(Home.toString()).not.toContain("fetch(");
  });
});
