import type { ReactNode } from "react";
import { cn } from "@/lib/utils/cn";

type AlertTone = "error" | "info";

const tones: Record<AlertTone, { wrapper: string; title: string; role: string }> = {
  error: {
    wrapper: "border-red-200 bg-red-50",
    title: "text-red-800",
    role: "alert",
  },
  info: {
    wrapper: "border-sky-200 bg-sky-50",
    title: "text-sky-800",
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
      className={cn("rounded-lg border p-4", t.wrapper, className)}
    >
      <p className={cn("text-sm font-semibold", t.title)}>{title}</p>
      {children && <div className="mt-1 text-sm text-zinc-600">{children}</div>}
      {action && <div className="mt-3">{action}</div>}
    </div>
  );
}
