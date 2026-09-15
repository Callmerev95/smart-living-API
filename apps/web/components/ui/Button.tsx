import type { ButtonHTMLAttributes, ReactNode } from "react";
import { cn } from "@/lib/utils/cn";

type ButtonVariant = "primary" | "secondary" | "ghost";

const variants: Record<ButtonVariant, string> = {
  primary: "bg-clay text-on-clay hover:bg-clay/90 focus-visible:outline-turmeric",
  secondary:
    "bg-surface text-ink border border-line-strong hover:bg-surface-muted focus-visible:outline-turmeric",
  ghost:
    "bg-transparent text-ink-soft hover:bg-surface-muted hover:text-ink focus-visible:outline-turmeric",
};

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: ButtonVariant;
  loading?: boolean;
  children: ReactNode;
};

export function Button({
  variant = "primary",
  loading = false,
  disabled,
  className,
  children,
  type = "button",
  ...props
}: ButtonProps) {
  return (
    <button
      type={type}
      className={cn(
        "inline-flex items-center justify-center gap-2 rounded-lg px-4 font-medium whitespace-nowrap transition-colors",
        // Tinggi minimum 44px (tap target R-03) berlaku untuk semua varian.
        "min-h-11",
        "focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-solid",
        "disabled:cursor-not-allowed disabled:opacity-60",
        variants[variant],
        className,
      )}
      disabled={disabled || loading}
      aria-busy={loading || undefined}
      {...props}
    >
      {loading && (
        <span
          aria-hidden="true"
          className="size-3 animate-spin rounded-full border-2 border-current border-t-transparent"
        />
      )}
      {children}
    </button>
  );
}
