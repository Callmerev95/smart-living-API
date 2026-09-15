import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it } from "vitest";

import { ThemeToggle } from "@/components/ui/ThemeToggle";
import { content } from "@/lib/constants/content";

describe("ThemeToggle", () => {
  beforeEach(() => {
    document.documentElement.classList.remove("dark");
    window.localStorage.removeItem("sl-theme");
  });

  it("punya nama aksesibel dari content.ts", () => {
    render(<ThemeToggle />);
    expect(
      screen.getByRole("button", { name: content.theme.switchLabel }),
    ).toBeInTheDocument();
  });

  it("dari terang: menambah class dark dan menyimpan pilihan", async () => {
    render(<ThemeToggle />);
    await userEvent.click(screen.getByRole("button", { name: content.theme.switchLabel }));

    expect(document.documentElement).toHaveClass("dark");
    expect(window.localStorage.getItem("sl-theme")).toBe("dark");
  });

  it("dari gelap: menghapus class dark dan menyimpan pilihan", async () => {
    document.documentElement.classList.add("dark");
    render(<ThemeToggle />);

    await userEvent.click(screen.getByRole("button", { name: content.theme.switchLabel }));

    expect(document.documentElement).not.toHaveClass("dark");
    expect(window.localStorage.getItem("sl-theme")).toBe("light");
  });
});
