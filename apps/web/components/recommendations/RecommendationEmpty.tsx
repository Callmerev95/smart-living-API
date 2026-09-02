import { Alert } from "@/components/ui/Alert";
import { content, fill } from "@/lib/constants/content";

type RecommendationEmptyProps = {
  /** Bahan yang tidak dikenali. Bila semua input tak dikenali, pesan berbeda dipakai. */
  unknownIngredients?: string[];
  /** True bila tidak ada satu pun bahan yang dikenali (Delta 2, copy §B.5.5). */
  allUnknown?: boolean;
};

/**
 * State kosong (`docs/content-schema.md` §B.5.4) dengan varian khusus
 * "semua bahan tidak dikenali" (§B.5.5) agar user paham penyebabnya.
 */
export function RecommendationEmpty({
  unknownIngredients = [],
  allUnknown = false,
}: RecommendationEmptyProps) {
  if (allUnknown && unknownIngredients.length > 0) {
    return (
      <Alert tone="info" title={content.results.allUnknown.title}>
        {fill(content.results.allUnknown.body, {
          list: unknownIngredients.join(", "),
        })}
      </Alert>
    );
  }

  return (
    <Alert tone="info" title={content.results.empty.title}>
      {content.results.empty.body}
    </Alert>
  );
}
