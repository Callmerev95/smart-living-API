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
          "border-line-strong bg-surface px-2.5 py-0.5 text-xs text-ink-soft",
        )}
      >
        <span className="font-medium line-through">{props.raw}</span>
        <span>·</span>
        <span>{content.chip.unknownSuffix}</span>
        <span className="sr-only">{content.chip.unknownTooltip}</span>
      </span>
    );
  }

  if (props.variant === "normalized") {
    return (
      <span
        className={cn(
          "inline-flex items-center gap-1.5 rounded-full border border-clay/30",
          "bg-clay-soft px-2.5 py-0.5 text-xs text-clay",
        )}
      >
        <span className="opacity-80">{props.raw}</span>
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
        "inline-flex items-center rounded-full border border-line bg-surface",
        "px-2.5 py-0.5 text-xs font-medium text-ink",
      )}
    >
      {props.displayName}
    </span>
  );
}
