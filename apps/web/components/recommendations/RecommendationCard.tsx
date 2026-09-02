import Link from "next/link";

import { MatchBadge } from "@/components/recommendations/MatchBadge";
import { Card } from "@/components/ui/Card";
import { content, fill } from "@/lib/constants/content";
import type { Recommendation } from "@/types/api";

/**
 * Kartu rekomendasi (`docs/component-architecture.md` §7, copy §B.6).
 *
 * Component ini tidak menghitung apa pun — seluruh nilai berasal dari props.
 * Available/missing dibedakan lewat label teks, bukan hanya warna.
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
      <div className="flex flex-col gap-2">
        <h3 className="text-lg font-semibold text-zinc-900">{name}</h3>
        <MatchBadge percentage={matchPercentage} />
        <p className="text-sm text-zinc-600">{description}</p>
      </div>

      <dl className="flex flex-col gap-2 text-sm">
        <div>
          <dt className="font-medium text-zinc-700">{content.card.availableLabel}</dt>
          <dd className="text-zinc-600">
            {availableIngredients.length > 0 ? availableIngredients.join(", ") : "—"}
          </dd>
        </div>
        <div>
          <dt className="font-medium text-zinc-700">{content.card.missingLabel}</dt>
          <dd className="text-zinc-600">
            {missingIngredients.length > 0
              ? missingIngredients.join(", ")
              : content.card.missingEmpty}
          </dd>
        </div>
      </dl>

      <p className="text-sm text-zinc-500">
        {fill(content.card.timeLabel, { minutes: cookingTimeMinutes })}
        {" · "}
        {content.card.difficulty[difficulty] ?? difficulty}
        {" · "}
        {fill(content.card.servingsLabel, { servings })}
      </p>

      <Link
        href={`/recipes/${id}`}
        className="mt-auto inline-flex w-fit items-center rounded-md border border-zinc-300 px-3 py-1.5 text-sm font-medium text-zinc-900 transition-colors hover:bg-zinc-50 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-amber-500"
      >
        {content.card.cta}
      </Link>
    </Card>
  );
}
