import Link from "next/link";

import { MatchBadge } from "@/components/recommendations/MatchBadge";
import { Card } from "@/components/ui/Card";
import { content, fill } from "@/lib/constants/content";
import type { Recommendation } from "@/types/api";

/**
 * Kartu rekomendasi (`docs/component-architecture.md` §7, copy §B.6).
 *
 * Component ini tidak menghitung apa pun — seluruh nilai berasal dari props.
 * Available/missing dibedakan lewat label teks, bukan hanya warna. Angka meta
 * (waktu, porsi) memakai mono: motif "data voice" (DESIGN.md).
 */
export function RecommendationCard({ recommendation }: { recommendation: Recommendation }) {
  const {
    id,
    name,
    description,
    matchPercentage,
    availableIngredients,
    missingIngredients,
    cookingTimeMinutes,
    difficulty,
    servings,
  } = recommendation;

  return (
    <Card className="flex flex-col gap-3">
      <MatchBadge percentage={matchPercentage} />

      <div className="flex flex-col gap-1.5">
        <h3 className="text-lg leading-snug font-semibold text-ink">{name}</h3>
        <p className="text-sm text-ink-soft">{description}</p>
      </div>

      <dl className="flex flex-col gap-2 border-t border-line pt-3 text-sm">
        <div className="flex flex-col gap-0.5">
          <dt className="text-xs font-medium text-ink-soft">{content.card.availableLabel}</dt>
          <dd className="text-olive">
            {availableIngredients.length > 0
              ? availableIngredients.join(", ")
              : content.card.availableEmpty}
          </dd>
        </div>
        <div className="flex flex-col gap-0.5">
          <dt className="text-xs font-medium text-ink-soft">{content.card.missingLabel}</dt>
          <dd className="text-ink-soft">
            {missingIngredients.length > 0
              ? missingIngredients.join(", ")
              : content.card.missingEmpty}
          </dd>
        </div>
      </dl>

      <p className="font-mono text-xs text-ink-soft tabular-nums">
        {fill(content.card.timeLabel, { minutes: cookingTimeMinutes })}
        {" · "}
        {content.card.difficulty[difficulty] ?? difficulty}
        {" · "}
        {fill(content.card.servingsLabel, { servings })}
      </p>

      <Link
        href={`/recipes/${id}`}
        className="mt-auto inline-flex min-h-11 w-fit items-center rounded-lg border border-line-strong px-4 text-sm font-medium text-ink transition-colors hover:bg-surface-muted focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-solid focus-visible:outline-turmeric"
      >
        {content.card.cta}
      </Link>
    </Card>
  );
}
