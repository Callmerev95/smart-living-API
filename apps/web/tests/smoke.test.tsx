import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import Home from "@/app/page";

describe("smoke", () => {
  it("merender teks sederhana", () => {
    render(<div>Halo Smart Living</div>);
    expect(screen.getByText("Halo Smart Living")).toBeInTheDocument();
  });

  it("alias @/ resolve dan component app bisa dirender", () => {
    render(<Home />);
    expect(screen.getByRole("heading", { name: "Smart Living" })).toBeInTheDocument();
  });
});
