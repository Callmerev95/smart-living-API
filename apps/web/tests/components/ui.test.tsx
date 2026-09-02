import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { Alert } from "@/components/ui/Alert";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { Skeleton } from "@/components/ui/Skeleton";
import { Spinner } from "@/components/ui/Spinner";

describe("Button", () => {
  it("merender label dan memanggil onClick", async () => {
    const onClick = vi.fn();
    render(<Button onClick={onClick}>Simpan</Button>);
    await userEvent.click(screen.getByRole("button", { name: "Simpan" }));
    expect(onClick).toHaveBeenCalledOnce();
  });

  it("tidak bisa diklik saat disabled", async () => {
    const onClick = vi.fn();
    render(
      <Button disabled onClick={onClick}>
        Simpan
      </Button>,
    );
    await userEvent.click(screen.getByRole("button"));
    expect(onClick).not.toHaveBeenCalled();
  });

  it("state loading menandai aria-busy dan menonaktifkan tombol", () => {
    render(<Button loading>Mencari</Button>);
    const button = screen.getByRole("button");
    expect(button).toBeDisabled();
    expect(button).toHaveAttribute("aria-busy", "true");
  });

  it("mempertahankan focus ring", () => {
    render(<Button>Fokus</Button>);
    expect(screen.getByRole("button").className).toContain("focus-visible:outline");
  });
});

describe("Input", () => {
  it("menghubungkan label dengan field", () => {
    render(<Input label="Bahan" />);
    expect(screen.getByLabelText("Bahan")).toBeInTheDocument();
  });

  it("menampilkan pesan error sebagai alert dan menandai aria-invalid", () => {
    render(<Input label="Bahan" error="Wajib diisi" />);
    expect(screen.getByRole("alert")).toHaveTextContent("Wajib diisi");
    expect(screen.getByLabelText("Bahan")).toHaveAttribute("aria-invalid", "true");
  });

  it("menghubungkan help text via aria-describedby", () => {
    render(<Input label="Bahan" helpText="Pisahkan dengan koma." />);
    const input = screen.getByLabelText("Bahan");
    const describedBy = input.getAttribute("aria-describedby");
    expect(describedBy).toBeTruthy();
    expect(screen.getByText("Pisahkan dengan koma.")).toHaveAttribute("id", describedBy);
  });

  it("error menggantikan help text agar tidak membingungkan", () => {
    render(<Input label="Bahan" error="Wajib diisi" helpText="Pisahkan dengan koma." />);
    expect(screen.queryByText("Pisahkan dengan koma.")).not.toBeInTheDocument();
  });

  it("menerima input teks", async () => {
    render(<Input label="Bahan" />);
    await userEvent.type(screen.getByLabelText("Bahan"), "telur");
    expect(screen.getByLabelText("Bahan")).toHaveValue("telur");
  });
});

describe("Badge", () => {
  it("merender konten", () => {
    render(<Badge tone="success">100% cocok</Badge>);
    expect(screen.getByText("100% cocok")).toBeInTheDocument();
  });
});

describe("Alert", () => {
  it("error memakai role alert", () => {
    render(<Alert tone="error" title="Gagal" />);
    expect(screen.getByRole("alert")).toHaveTextContent("Gagal");
  });

  it("info memakai role status", () => {
    render(<Alert tone="info" title="Info" />);
    expect(screen.getByRole("status")).toHaveTextContent("Info");
  });

  it("merender action", () => {
    render(<Alert title="Gagal" tone="error" action={<Button>Coba lagi</Button>} />);
    expect(screen.getByRole("button", { name: "Coba lagi" })).toBeInTheDocument();
  });
});

describe("Card", () => {
  it("merender children", () => {
    render(<Card>Isi kartu</Card>);
    expect(screen.getByText("Isi kartu")).toBeInTheDocument();
  });
});

describe("Skeleton", () => {
  it("disembunyikan dari screen reader", () => {
    const { container } = render(<Skeleton className="h-4" />);
    expect(container.firstChild).toHaveAttribute("aria-hidden", "true");
  });
});

describe("Spinner", () => {
  it("punya label yang terbaca screen reader", () => {
    render(<Spinner />);
    expect(screen.getByRole("status", { name: "Memuat" })).toBeInTheDocument();
  });
});

describe("UI primitives tetap generik", () => {
  it("tidak ada komponen domain di folder ui", async () => {
    const modules = import.meta.glob("../../components/ui/*.tsx");
    const names = Object.keys(modules).map((path) => path.split("/").pop());
    expect(names).toEqual(
      expect.arrayContaining([
        "Alert.tsx",
        "Badge.tsx",
        "Button.tsx",
        "Card.tsx",
        "Input.tsx",
        "Skeleton.tsx",
        "Spinner.tsx",
      ]),
    );
    for (const name of names) {
      expect(name).not.toMatch(/Recipe|Ingredient|Recommendation|Match/);
    }
  });
});
