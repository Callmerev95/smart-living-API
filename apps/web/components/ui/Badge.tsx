import type { ReactNode } from "react";
import { cn } from "@/lib/utils/cn";

type BadgeTone = "neutral" | "success" | "warning" | "danger" | "info";

/**
 * Tone memakai pasangan chip-soft + teks dari token (DESIGN.md). Dipakai hanya
 * untuk label status kecil, bukan dekorasi.
 */
const tones: Record<BadgeTone, string> = {
  neutral: "bg-surface-muted text-ink-soft border-line",
  success: "bg-olive-soft text-olive border-line",
  warning: "bg-turmeric-soft text-turmeric border-line",
  danger: "bg-brick-soft text-brick border-line",
  info: "bg-clay-soft text-clay border-line",
};

export function Badge({
  children,
  tone = "neutral",
  className,
}: {
  children: ReactNode;
  tone?: BadgeTone;
  className?: string;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-medium",
        tones[tone],
        className,
      )}
    >
      {children}
    </span>
  );
}
