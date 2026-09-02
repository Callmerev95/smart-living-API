import { cn } from "@/lib/utils/cn";

export function Spinner({ className }: { className?: string }) {
  return (
    <span
      role="status"
      aria-label="Memuat"
      className={cn(
        "inline-block size-4 animate-spin rounded-full border-2 border-zinc-400 border-t-transparent",
        className,
      )}
    />
  );
}
