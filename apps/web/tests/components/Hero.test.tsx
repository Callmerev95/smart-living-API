import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { Footer } from "@/components/Footer";
import { HeroSection } from "@/components/HeroSection";
import { content } from "@/lib/constants/content";

describe("HeroSection", () => {
  it("judul memakai copy PRD §8.6 sebagai h1", () => {
    render(<HeroSection />);
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(content.hero.title);
  });

  it("menampilkan subtitle dan badge", () => {
    render(<HeroSection />);
    expect(screen.getByText(content.hero.subtitle)).toBeInTheDocument();
    expect(screen.getByText(content.hero.badge)).toBeInTheDocument();
  });

  it("hanya satu h1", () => {
    render(<HeroSection />);
    expect(screen.getAllByRole("heading", { level: 1 })).toHaveLength(1);
  });
});

describe("Footer", () => {
  it("menampilkan tagline visi produk", () => {
    render(<Footer />);
    expect(screen.getByText(content.footer.tagline)).toBeInTheDocument();
  });

  it("menyediakan tautan repo", () => {
    render(<Footer />);
    const link = screen.getByRole("link", { name: content.footer.repoLabel });
    expect(link).toHaveAttribute("href", expect.stringContaining("github.com"));
  });
});
