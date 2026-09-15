import type { ReactNode } from "react";
import { cn } from "@/lib/utils/cn";

export function Card({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <div
      className={cn(
        // Tanpa shadow: kartu duduk rata di permukaan, struktur dari border
        // (DESIGN.md bentuk). Shadow hanya untuk elemen yang melayang.
        "rounded-xl border border-line bg-surface p-5",
        className,
      )}
    >
      {children}
    </div>
  );
}
