import type { InputHTMLAttributes } from "react";
import { cn } from "@/lib/utils/cn";

type InputProps = InputHTMLAttributes<HTMLInputElement> & {
  label?: string;
  error?: string | null;
  helpText?: string;
};

export function Input({
  label,
  error,
  helpText,
  id,
  className,
  "aria-describedby": ariaDescribedBy,
  ...props
}: InputProps) {
  const inputId = id ?? (label ? `input-${label.replace(/\s+/g, "-").toLowerCase()}` : undefined);
  const errorId = error ? `${inputId}-error` : undefined;
  const helpId = helpText ? `${inputId}-help` : undefined;
  const describedBy = [ariaDescribedBy, errorId, helpId].filter(Boolean).join(" ") || undefined;

  return (
    <div className="flex flex-col gap-1.5">
      {label && (
        <label htmlFor={inputId} className="text-sm font-medium text-ink">
          {label}
        </label>
      )}
      <input
        id={inputId}
        className={cn(
          "w-full min-h-11 rounded-lg border bg-surface px-3 text-sm text-ink",
          "placeholder:text-ink-soft/70",
          "focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-solid focus-visible:outline-turmeric",
          error ? "border-brick" : "border-line-strong",
          className,
        )}
        aria-invalid={error ? true : undefined}
        aria-describedby={describedBy}
        {...props}
      />
      {error && (
        <p id={errorId} className="text-sm text-brick" role="alert">
          {error}
        </p>
      )}
      {!error && helpText && (
        <p id={helpId} className="text-sm text-ink-soft">
          {helpText}
        </p>
      )}
    </div>
  );
}
