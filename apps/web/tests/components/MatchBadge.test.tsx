import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { MatchBadge } from "@/components/recommendations/MatchBadge";
import { content, matchTier } from "@/lib/constants/content";

describe("matchTier", () => {
  it("batas tier sesuai docs §B.6.2", () => {
    expect(matchTier(100)).toBe("perfect");
    expect(matchTier(99)).toBe("high");
    expect(matchTier(70)).toBe("high");
    expect(matchTier(69)).toBe("medium");
    expect(matchTier(50)).toBe("medium");
    expect(matchTier(49)).toBe("low");
    expect(matchTier(30)).toBe("low");
  });
});

describe("MatchBadge", () => {
  it("menampilkan persentase sebagai integer", () => {
    render(<MatchBadge percentage={75} />);
    expect(screen.getByText("75% cocok")).toBeInTheDocument();
  });

  it("tier perfect pada 100%", () => {
    render(<MatchBadge percentage={100} />);
    expect(screen.getByText(content.card.tier.perfect)).toBeInTheDocument();
  });

  it("tier high pada 70-99%", () => {
    render(<MatchBadge percentage={85} />);
    expect(screen.getByText(content.card.tier.high)).toBeInTheDocument();
  });

  it("tier medium pada 50-69%", () => {
    render(<MatchBadge percentage={60} />);
    expect(screen.getByText(content.card.tier.medium)).toBeInTheDocument();
  });

  it("tier low pada 30-49%", () => {
    render(<MatchBadge percentage={33} />);
    expect(screen.getByText(content.card.tier.low)).toBeInTheDocument();
  });

  it("label tier selalu berupa teks, bukan hanya warna", () => {
    const { container } = render(<MatchBadge percentage={100} />);
    expect(container.textContent).toContain(content.card.tier.perfect);
  });

  it("tidak ada placeholder yang bocor ke layar", () => {
    const { container } = render(<MatchBadge percentage={50} />);
    expect(container.textContent).not.toContain("{percentage}");
  });
});
