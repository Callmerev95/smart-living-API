import { content, fill } from "@/lib/constants/content";
import { cn } from "@/lib/utils/cn";

type IngredientTagProps =
  | { variant: "plain"; displayName: string }
  | { variant: "normalized"; raw: string; displayName: string }
  | { variant: "unknown"; raw: string };

/**
 * Chip hasil normalisasi (`docs/content-schema.md` §B.4).
 *
 * Implementasi UI untuk Contract Delta v1.1: Delta 3 (mapping input -> canonical)
 * dan Delta 2 (penanda bahan tak dikenali). Perbedaan varian tidak hanya lewat
 * warna — ada teks yang terbaca screen reader.
 */
export function IngredientTag(props: IngredientTagProps) {
  if (props.variant === "unknown") {
    return (
      <span
        className={cn(
          "inline-flex items-center gap-1.5 rounded-full border border-dashed",
          "border-zinc-400 bg-zinc-50 px-2.5 py-0.5 text-xs text-zinc-600",
        )}
      >
        <span className="font-medium line-through decoration-zinc-400">{props.raw}</span>
        <span className="text-zinc-500">·</span>
        <span>{content.chip.unknownSuffix}</span>
        <span className="sr-only">{content.chip.unknownTooltip}</span>
      </span>
    );
  }

  if (props.variant === "normalized") {
    return (
      <span
        className={cn(
          "inline-flex items-center gap-1.5 rounded-full border border-amber-200",
          "bg-amber-50 px-2.5 py-0.5 text-xs text-amber-900",
        )}
      >
        <span className="text-amber-700">{props.raw}</span>
        <span aria-hidden="true">→</span>
        <span className="font-medium">{props.displayName}</span>
        <span className="sr-only">
          {fill(content.chip.normalizedTooltip, { displayName: props.displayName })}
        </span>
      </span>
    );
  }

  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border border-zinc-200",
        "bg-white px-2.5 py-0.5 text-xs font-medium text-zinc-700",
      )}
    >
      {props.displayName}
    </span>
  );
}
