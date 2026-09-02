import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import {
  IngredientInput,
  parseIngredients,
  validateIngredients,
} from "@/components/ingredients/IngredientInput";
import { content } from "@/lib/constants/content";

describe("parseIngredients", () => {
  it("memecah comma-separated", () => {
    expect(parseIngredients("telur, ayam, wortel")).toEqual(["telur", "ayam", "wortel"]);
  });

  it("membuang whitespace dan token kosong", () => {
    expect(parseIngredients("telur, , ayam,")).toEqual(["telur", "ayam"]);
  });

  it("mendukung newline sebagai pemisah", () => {
    expect(parseIngredients("telur\nayam")).toEqual(["telur", "ayam"]);
  });

  it("input kosong menghasilkan array kosong", () => {
    expect(parseIngredients("   ")).toEqual([]);
  });

  it("tidak melakukan normalisasi canonical — itu tugas server", () => {
    expect(parseIngredients("TELUR")).toEqual(["TELUR"]);
  });
});

describe("validateIngredients", () => {
  it("kosong -> pesan empty", () => {
    expect(validateIngredients([])).toBe(content.input.validation.empty);
  });

  it("lebih dari 30 bahan -> pesan tooMany dengan angka terinterpolasi", () => {
    const message = validateIngredients(Array.from({ length: 31 }, (_, i) => `b${i}`));
    expect(message).toContain("30");
    expect(message).not.toContain("{max}");
  });

  it("tepat 30 bahan diterima", () => {
    expect(validateIngredients(Array.from({ length: 30 }, (_, i) => `b${i}`))).toBeNull();
  });

  it("nama lebih dari 60 karakter -> pesan tooLong", () => {
    expect(validateIngredients(["x".repeat(61)])).toBe(content.input.validation.tooLong);
  });

  it("nama tepat 60 karakter diterima", () => {
    expect(validateIngredients(["x".repeat(60)])).toBeNull();
  });

  it("input valid -> null", () => {
    expect(validateIngredients(["telur", "ayam"])).toBeNull();
  });
});

describe("IngredientInput", () => {
  it("merender label yang terasosiasi dengan field", () => {
    render(<IngredientInput onSubmit={vi.fn()} />);
    expect(screen.getByLabelText(content.input.label)).toBeInTheDocument();
  });

  it("submit lewat tombol mengirim daftar bahan", async () => {
    const onSubmit = vi.fn();
    render(<IngredientInput onSubmit={onSubmit} />);

    await userEvent.type(screen.getByLabelText(content.input.label), "telur, ayam");
    await userEvent.click(screen.getByRole("button", { name: content.input.submit }));

    expect(onSubmit).toHaveBeenCalledWith(["telur", "ayam"]);
  });

  it("submit lewat Enter mengirim daftar bahan", async () => {
    const onSubmit = vi.fn();
    render(<IngredientInput onSubmit={onSubmit} />);

    await userEvent.type(screen.getByLabelText(content.input.label), "telur, wortel{Enter}");

    expect(onSubmit).toHaveBeenCalledWith(["telur", "wortel"]);
  });

  it("input kosong memblokir submit dan menampilkan pesan", async () => {
    const onSubmit = vi.fn();
    render(<IngredientInput onSubmit={onSubmit} />);

    await userEvent.click(screen.getByRole("button", { name: content.input.submit }));

    expect(onSubmit).not.toHaveBeenCalled();
    expect(screen.getByRole("alert")).toHaveTextContent(content.input.validation.empty);
  });

  it("bahan terlalu panjang memblokir submit", async () => {
    const onSubmit = vi.fn();
    render(<IngredientInput onSubmit={onSubmit} />);

    await userEvent.type(screen.getByLabelText(content.input.label), "x".repeat(61));
    await userEvent.click(screen.getByRole("button", { name: content.input.submit }));

    expect(onSubmit).not.toHaveBeenCalled();
    expect(screen.getByRole("alert")).toHaveTextContent(content.input.validation.tooLong);
  });

  it("pesan error terhubung ke input via aria-describedby", async () => {
    render(<IngredientInput onSubmit={vi.fn()} />);
    await userEvent.click(screen.getByRole("button", { name: content.input.submit }));

    const input = screen.getByLabelText(content.input.label);
    expect(input).toHaveAttribute("aria-invalid", "true");
    const describedBy = input.getAttribute("aria-describedby");
    expect(describedBy).toContain("error");
  });

  it("tombol contoh mengisi field", async () => {
    render(<IngredientInput onSubmit={vi.fn()} />);
    const example = content.input.examples[0];

    await userEvent.click(screen.getByRole("button", { name: example }));

    expect(screen.getByLabelText(content.input.label)).toHaveValue(example);
  });

  it("tombol clear mengosongkan field", async () => {
    render(<IngredientInput onSubmit={vi.fn()} />);
    await userEvent.type(screen.getByLabelText(content.input.label), "telur");

    await userEvent.click(screen.getByRole("button", { name: content.input.clear }));

    expect(screen.getByLabelText(content.input.label)).toHaveValue("");
  });

  it("tombol clear hanya muncul saat ada isi", async () => {
    render(<IngredientInput onSubmit={vi.fn()} />);
    expect(
      screen.queryByRole("button", { name: content.input.clear }),
    ).not.toBeInTheDocument();

    await userEvent.type(screen.getByLabelText(content.input.label), "telur");
    expect(screen.getByRole("button", { name: content.input.clear })).toBeInTheDocument();
  });

  it("state loading menonaktifkan submit dan mengganti label", () => {
    render(<IngredientInput onSubmit={vi.fn()} loading />);
    const button = screen.getByRole("button", { name: content.input.submitLoading });
    expect(button).toBeDisabled();
  });

  it("error hilang setelah input valid dikirim", async () => {
    render(<IngredientInput onSubmit={vi.fn()} />);
    await userEvent.click(screen.getByRole("button", { name: content.input.submit }));
    expect(screen.getByRole("alert")).toBeInTheDocument();

    await userEvent.type(screen.getByLabelText(content.input.label), "telur");
    await userEvent.click(screen.getByRole("button", { name: content.input.submit }));

    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });

  it("bisa dioperasikan penuh dengan keyboard", async () => {
    const onSubmit = vi.fn();
    render(<IngredientInput onSubmit={onSubmit} />);

    await userEvent.tab();
    expect(screen.getByLabelText(content.input.label)).toHaveFocus();

    await userEvent.keyboard("telur, ayam");
    await userEvent.tab();
    expect(screen.getByRole("button", { name: content.input.submit })).toHaveFocus();
    await userEvent.keyboard("{Enter}");

    expect(onSubmit).toHaveBeenCalledWith(["telur", "ayam"]);
  });
});
