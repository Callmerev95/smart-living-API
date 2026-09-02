import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { IngredientTag } from "@/components/ingredients/IngredientTag";
import { content } from "@/lib/constants/content";

describe("varian plain", () => {
  it("menampilkan display name saja", () => {
    render(<IngredientTag variant="plain" displayName="Telur" />);
    expect(screen.getByText("Telur")).toBeInTheDocument();
  });
});

describe("varian normalized (Delta 3)", () => {
  it("menampilkan mapping input ke display name", () => {
    render(<IngredientTag variant="normalized" raw="telur" displayName="Telur" />);
    expect(screen.getByText("telur")).toBeInTheDocument();
    expect(screen.getByText("Telur")).toBeInTheDocument();
  });

  it("menyertakan penjelasan untuk screen reader", () => {
    render(<IngredientTag variant="normalized" raw="telor" displayName="Telur" />);
    expect(screen.getByText("Kami mengenali bahan ini sebagai Telur.")).toBeInTheDocument();
  });

  it("panah dekoratif disembunyikan dari screen reader", () => {
    const { container } = render(
      <IngredientTag variant="normalized" raw="telur" displayName="Telur" />,
    );
    const arrow = container.querySelector('[aria-hidden="true"]');
    expect(arrow).toHaveTextContent("→");
  });
});

describe("varian unknown (Delta 2)", () => {
  it("menampilkan token asli dan suffix tidak dikenali", () => {
    render(<IngredientTag variant="unknown" raw="kangkung" />);
    expect(screen.getByText("kangkung")).toBeInTheDocument();
    expect(screen.getByText(content.chip.unknownSuffix)).toBeInTheDocument();
  });

  it("menyertakan penjelasan untuk screen reader", () => {
    render(<IngredientTag variant="unknown" raw="kangkung" />);
    expect(screen.getByText(content.chip.unknownTooltip)).toBeInTheDocument();
  });

  it("perbedaan tidak hanya lewat warna — ada teks pembeda", () => {
    const { container: unknown } = render(<IngredientTag variant="unknown" raw="kangkung" />);
    expect(unknown.textContent).toContain(content.chip.unknownSuffix);
  });

  it("memakai border dashed agar terbedakan tanpa warna", () => {
    const { container } = render(<IngredientTag variant="unknown" raw="kangkung" />);
    expect(container.firstElementChild?.className).toContain("border-dashed");
  });
});
