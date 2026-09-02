import { IngredientTag } from "@/components/ingredients/IngredientTag";
import { RecommendationCard } from "@/components/recommendations/RecommendationCard";
import { RecommendationEmpty } from "@/components/recommendations/RecommendationEmpty";
import { RecommendationError } from "@/components/recommendations/RecommendationError";
import { RecommendationSkeleton } from "@/components/recommendations/RecommendationSkeleton";
import { content, fill } from "@/lib/constants/content";
import type { Recommendation, RecommendationResponse } from "@/types/api";

type DisplayNameMap = Record<string, string>;

function NormalizedIngredientChips({
  data,
  displayNames,
}: {
  data: RecommendationResponse;
  displayNames: DisplayNameMap;
}) {
  const { ingredients: known, raw } = data.query;

  return (
    <div className="flex flex-wrap gap-2" aria-label={content.results.chipsLabel}>
      {known.map((canonical, index) => {
        const rawValue = raw[index] ?? canonical;
        // Tanpa kamus, canonical dipakai apa adanya — chip tetap informatif.
        const displayName = displayNames[canonical] ?? canonical;

        if (rawValue.toLowerCase() === displayName.toLowerCase()) {
          return (
            <IngredientTag key={`known-${canonical}`} variant="plain" displayName={displayName} />
          );
        }

        return (
          <IngredientTag
            key={`known-${canonical}`}
            variant="normalized"
            raw={rawValue}
            displayName={displayName}
          />
        );
      })}
      {data.unknownIngredients.map((value) => (
        <IngredientTag key={`unknown-${value}`} variant="unknown" raw={value} />
      ))}
    </div>
  );
}

export function RecommendationList({ results }: { results: Recommendation[] }) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {results.map((recommendation) => (
        <RecommendationCard key={recommendation.id} recommendation={recommendation} />
      ))}
    </div>
  );
}

type RecommendationSectionProps = {
  status: "idle" | "loading" | "success" | "error";
  data?: RecommendationResponse;
  /** Peta `canonical -> displayName` dari kamus bahan. Opsional; fallback ke canonical. */
  displayNames?: DisplayNameMap;
  onRetry: () => void;
};

/** Memetakan status hook ke component state secara eksplisit. */
export function RecommendationSection({
  status,
  data,
  displayNames = {},
  onRetry,
}: RecommendationSectionProps) {
  if (status === "idle") {
    return (
      <section aria-label={content.results.sectionLabel}>
        <div className="rounded-lg border border-dashed border-zinc-300 p-8 text-center">
          <h2 className="text-lg font-semibold text-zinc-900">{content.results.initial.title}</h2>
          <p className="mt-2 text-sm text-zinc-600">{content.results.initial.body}</p>
        </div>
      </section>
    );
  }

  if (status === "loading") {
    return <RecommendationSkeleton />;
  }

  if (status === "error") {
    return <RecommendationError onRetry={onRetry} />;
  }

  if (!data || data.results.length === 0) {
    const allUnknown = Boolean(data?.unknownIngredients.length && !data.query.ingredients.length);
    return (
      <section className="flex flex-col gap-4" aria-label={content.results.sectionLabel}>
        {data && <NormalizedIngredientChips data={data} displayNames={displayNames} />}
        <RecommendationEmpty
          unknownIngredients={data?.unknownIngredients}
          allUnknown={allUnknown}
        />
      </section>
    );
  }

  const heading =
    data.results.length === 1
      ? content.results.success.headingSingle
      : fill(content.results.success.heading, { count: data.results.length });

  return (
    <section className="flex flex-col gap-4" aria-label={content.results.sectionLabel}>
      <div className="flex flex-col gap-1" role="status">
        <h2 className="text-2xl font-semibold text-zinc-900">{heading}</h2>
        <p className="text-sm text-zinc-500">{content.results.success.sortNote}</p>
      </div>
      <NormalizedIngredientChips data={data} displayNames={displayNames} />
      <RecommendationList results={data.results} />
    </section>
  );
}
