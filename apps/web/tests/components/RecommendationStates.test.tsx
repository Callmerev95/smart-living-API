import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { RecommendationEmpty } from "@/components/recommendations/RecommendationEmpty";
import { RecommendationError } from "@/components/recommendations/RecommendationError";
import { RecommendationSkeleton } from "@/components/recommendations/RecommendationSkeleton";
import { content, fill } from "@/lib/constants/content";

describe("RecommendationSkeleton", () => {
  it("menampilkan 3 placeholder card", () => {
    const { container } = render(<RecommendationSkeleton />);
    const grid = container.querySelector('[aria-hidden="true"]');
    expect(grid?.children).toHaveLength(3);
  });

  it("grid disembunyikan dari screen reader; status diumumkan satu kali", () => {
    const { container } = render(<RecommendationSkeleton />);
    expect(screen.getByRole("status")).toHaveTextContent(content.results.loading.label);
    expect(container.querySelector('[aria-hidden="true"]')).not.toBeNull();
    expect(screen.getAllByRole("status")).toHaveLength(1);
  });
});

describe("RecommendationEmpty", () => {
  it("state kosong biasa memakai copy §B.5.4", () => {
    render(<RecommendationEmpty />);
    expect(screen.getByText(content.results.empty.title)).toBeInTheDocument();
    expect(screen.getByText(content.results.empty.body)).toBeInTheDocument();
  });

  it("varian allUnknown memakai copy §B.5.5 dengan interpolasi daftar bahan", () => {
    render(<RecommendationEmpty unknownIngredients={["kangkung", "durian"]} allUnknown />);
    expect(screen.getByText(content.results.allUnknown.title)).toBeInTheDocument();
    expect(
      screen.getByText(
        fill(content.results.allUnknown.body, { list: "kangkung, durian" }),
      ),
    ).toBeInTheDocument();
  });

  it("varian allUnknown tanpa true tetap memakai copy biasa", () => {
    render(<RecommendationEmpty unknownIngredients={["kangkung"]} />);
    expect(screen.getByText(content.results.empty.title)).toBeInTheDocument();
  });
});

describe("RecommendationError", () => {
  it("menampilkan copy §B.5.6 beserta tombol retry", () => {
    const onRetry = vi.fn();
    render(<RecommendationError onRetry={onRetry} />);
    expect(screen.getByText(content.results.error.title)).toBeInTheDocument();
    expect(screen.getByText(content.results.error.body)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: content.results.error.retry })).toBeInTheDocument();
  });

  it("tombol retry memanggil onRetry", async () => {
    const onRetry = vi.fn();
    render(<RecommendationError onRetry={onRetry} />);
    await userEvent.click(screen.getByRole("button", { name: content.results.error.retry }));
    expect(onRetry).toHaveBeenCalledOnce();
  });
});
