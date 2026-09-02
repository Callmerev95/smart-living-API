import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { ApiShowcase } from "@/components/showcase/ApiShowcase";
import { ArchitectureDiagram } from "@/components/showcase/ArchitectureDiagram";
import { RequestExample } from "@/components/showcase/RequestExample";
import { ResponseExample } from "@/components/showcase/ResponseExample";
import { TechStack } from "@/components/showcase/TechStack";
import { TechnicalDecisions } from "@/components/showcase/TechnicalDecisions";
import {
  API_EXAMPLE_REQUEST,
  API_EXAMPLE_REQUEST_TEXT,
  API_EXAMPLE_RESPONSE,
  API_EXAMPLE_RESPONSE_TEXT,
} from "@/lib/constants/apiExample";
import { content } from "@/lib/constants/content";

const writeText = vi.fn().mockResolvedValue(undefined);

beforeEach(() => {
  // jsdom tidak menyediakan Clipboard API.
  Object.defineProperty(navigator, "clipboard", {
    value: { writeText },
    configurable: true,
    writable: true,
  });
  vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "http://api.test");
});

afterEach(() => {
  writeText.mockClear();
  vi.unstubAllEnvs();
});

describe("RequestExample", () => {
  it("menampilkan method, path, dan body", () => {
    render(<RequestExample />);
    const block = screen.getByText(/POST \/api\/v1\/recommendations/);
    expect(block).toBeInTheDocument();
    expect(block).toHaveTextContent("Content-Type: application/json");
    expect(block).toHaveTextContent("telur");
  });

  it("tombol copy menyalin teks request", async () => {
    render(<RequestExample />);
    await userEvent.click(screen.getByRole("button"));
    expect(writeText).toHaveBeenCalledWith(API_EXAMPLE_REQUEST_TEXT);
  });

  it("label tombol copy menyebut konteksnya", () => {
    render(<RequestExample />);
    expect(
      screen.getByRole("button", {
        name: `${content.showcase.copyLabel} ${content.showcase.requestHeading}`,
      }),
    ).toBeInTheDocument();
  });

  it("label berubah menjadi Tersalin setelah copy", async () => {
    render(<RequestExample />);
    const button = screen.getByRole("button");
    expect(button).toHaveTextContent(content.showcase.copyLabel);

    await userEvent.click(button);

    await waitFor(() => expect(button).toHaveTextContent(content.showcase.copiedLabel));
  });
});

describe("ResponseExample", () => {
  it("menampilkan JSON response terformat", () => {
    render(<ResponseExample />);
    const block = screen.getByText(/"matchPercentage": 100/);
    expect(block).toBeInTheDocument();
  });

  it("menampilkan field Contract Delta v1.1", () => {
    render(<ResponseExample />);
    const block = screen.getByText(/"unknownIngredients"/);
    expect(block).toHaveTextContent('"raw"');
    expect(block).toHaveTextContent('"threshold"');
  });

  it("tombol copy menyalin teks response", async () => {
    render(<ResponseExample />);
    await userEvent.click(screen.getByRole("button"));
    expect(writeText).toHaveBeenCalledWith(API_EXAMPLE_RESPONSE_TEXT);
  });
});

describe("ArchitectureDiagram", () => {
  it("punya deskripsi alur untuk screen reader", () => {
    render(<ArchitectureDiagram />);
    expect(screen.getByLabelText(content.showcase.diagramAlt)).toBeInTheDocument();
  });

  it("menampilkan seluruh langkah alur", () => {
    render(<ArchitectureDiagram />);
    for (const step of content.showcase.diagramFlow) {
      expect(screen.getByText(step.label)).toBeInTheDocument();
    }
  });

  it("panah penghubung disembunyikan dari screen reader", () => {
    const { container } = render(<ArchitectureDiagram />);
    const arrows = container.querySelectorAll('[aria-hidden="true"]');
    expect(arrows.length).toBe(content.showcase.diagramFlow.length - 1);
  });

  it("bukan blok pre — agar tidak pecah di layar kecil", () => {
    const { container } = render(<ArchitectureDiagram />);
    expect(container.querySelector("pre")).toBeNull();
  });
});

describe("TechStack", () => {
  it("menampilkan lima layer", () => {
    render(<TechStack />);
    for (const row of content.showcase.stack) {
      expect(screen.getByText(row.layer)).toBeInTheDocument();
      expect(screen.getByText(row.items)).toBeInTheDocument();
    }
  });

  it("memakai definition list", () => {
    const { container } = render(<TechStack />);
    expect(container.querySelector("dl")).not.toBeNull();
    expect(container.querySelectorAll("dt")).toHaveLength(content.showcase.stack.length);
  });
});

describe("TechnicalDecisions", () => {
  it("menampilkan tiga kartu keputusan", () => {
    render(<TechnicalDecisions />);
    expect(content.showcase.decisions).toHaveLength(3);
    for (const decision of content.showcase.decisions) {
      expect(screen.getByText(decision.title)).toBeInTheDocument();
    }
  });

  it("setiap kartu menyebut trade-off, bukan hanya keunggulan", () => {
    render(<TechnicalDecisions />);
    for (const decision of content.showcase.decisions) {
      expect(decision.body.toLowerCase()).toContain("trade-off");
    }
  });
});

describe("ApiShowcase", () => {
  it("menampilkan heading dan subheading", () => {
    render(<ApiShowcase />);
    expect(screen.getByRole("heading", { name: content.showcase.heading })).toBeInTheDocument();
    expect(screen.getByText(content.showcase.subheading)).toBeInTheDocument();
  });

  it("menggabungkan seluruh bagian", () => {
    render(<ApiShowcase />);
    expect(screen.getByText(content.showcase.requestHeading)).toBeInTheDocument();
    expect(screen.getByText(content.showcase.responseHeading)).toBeInTheDocument();
    expect(screen.getByText(content.showcase.architectureHeading)).toBeInTheDocument();
    expect(screen.getByText(content.showcase.stackHeading)).toBeInTheDocument();
    expect(screen.getByText(content.showcase.decisionsHeading)).toBeInTheDocument();
  });

  it("link OpenAPI dibangun dari base URL API", () => {
    render(<ApiShowcase />);
    expect(screen.getByRole("link", { name: content.showcase.docsLabel })).toHaveAttribute(
      "href",
      "http://api.test/docs",
    );
  });

  it("heading section memakai level 2, sub-bagian level 3", () => {
    render(<ApiShowcase />);
    expect(screen.getAllByRole("heading", { level: 2 })).toHaveLength(1);
    expect(screen.getAllByRole("heading", { level: 3 }).length).toBeGreaterThanOrEqual(5);
  });

  it("tidak ada placeholder yang bocor", () => {
    const { container } = render(<ApiShowcase />);
    expect(container.textContent).not.toMatch(/\{\w+\}/);
  });
});

describe("fixture contoh API", () => {
  it("request dan response berasal dari satu sumber", () => {
    for (const ingredient of API_EXAMPLE_REQUEST.ingredients) {
      expect(API_EXAMPLE_REQUEST_TEXT).toContain(ingredient);
    }
    expect(API_EXAMPLE_RESPONSE_TEXT).toContain(API_EXAMPLE_RESPONSE.results[0].id);
  });

  it("response memuat seluruh field kontrak Delta v1.1", () => {
    expect(API_EXAMPLE_RESPONSE.query.raw).toEqual(["telur", "ayam", "wortel"]);
    expect(API_EXAMPLE_RESPONSE.query.ingredients).toEqual(["egg", "chicken", "carrot"]);
    expect(API_EXAMPLE_RESPONSE.unknownIngredients).toEqual([]);
    expect(API_EXAMPLE_RESPONSE.meta.threshold).toBe(30);
  });

  it("staple tetap muncul di daftar bahan lengkap, tidak di missing (Delta 1)", () => {
    const item = API_EXAMPLE_RESPONSE.results[0];
    expect(item.ingredients).toContain("salt");
    expect(item.ingredients).toContain("cooking_oil");
    expect(item.missingIngredients).not.toContain("salt");
    expect(item.matchPercentage).toBe(100);
  });

  it("meta.count konsisten dengan jumlah hasil", () => {
    expect(API_EXAMPLE_RESPONSE.meta.count).toBe(API_EXAMPLE_RESPONSE.results.length);
  });
});
