import type { ReactNode } from "react";
import { cn } from "@/lib/utils/cn";

type AlertTone = "error" | "info";

const tones: Record<AlertTone, { wrapper: string; title: string; role: string }> = {
  error: {
    wrapper: "border-brick/40 bg-brick-soft",
    title: "text-brick",
    role: "alert",
  },
  info: {
    wrapper: "border-olive/40 bg-olive-soft",
    title: "text-olive",
    role: "status",
  },
};

export function Alert({
  title,
  children,
  tone = "info",
  action,
  className,
}: {
  title: string;
  children?: ReactNode;
  tone?: AlertTone;
  action?: ReactNode;
  className?: string;
}) {
  const t = tones[tone];
  return (
    <div
      role={t.role}
      className={cn("rounded-xl border p-4", t.wrapper, className)}
    >
      <p className={cn("text-sm font-semibold", t.title)}>{title}</p>
      {children && <div className="mt-1 text-sm text-ink-soft">{children}</div>}
      {action && <div className="mt-3">{action}</div>}
    </div>
  );
}
