import { Badge } from "@/components/ui/Badge";
import { content, fill } from "@/lib/constants/content";
import type { Recipe } from "@/types/api";

export function RecipeHeader({ recipe }: { recipe: Recipe }) {
  return (
    <header className="flex flex-col gap-3">
      <h1 className="font-display text-3xl font-semibold tracking-tight text-ink sm:text-4xl">
        {recipe.name}
      </h1>
      <p className="text-ink-soft">{recipe.description}</p>
      <div className="flex flex-wrap gap-2">
        {recipe.tags.map((tag) => (
          <Badge key={tag}>{tag}</Badge>
        ))}
      </div>
    </header>
  );
}

export function RecipeMeta({ recipe }: { recipe: Recipe }) {
  return (
    <section className="flex flex-col gap-2">
      <h2 className="font-display text-xl font-semibold text-ink">{content.detail.metaHeading}</h2>
      <p className="font-mono text-sm text-ink-soft tabular-nums">
        {fill(content.card.timeLabel, { minutes: recipe.cookingTimeMinutes })}
        {" · "}
        {content.card.difficulty[recipe.difficulty] ?? recipe.difficulty}
        {" · "}
        {fill(content.card.servingsLabel, { servings: recipe.servings })}
      </p>
    </section>
  );
}

export function RecipeIngredientList({ recipe }: { recipe: Recipe }) {
  return (
    <section className="flex flex-col gap-3">
      <h2 className="font-display text-xl font-semibold text-ink">
        {content.detail.ingredientsHeading}
      </h2>
      <ul className="flex flex-col gap-1.5 text-sm">
        {recipe.ingredients.map((item) => (
          <li key={item.name} className="flex items-center gap-2 text-ink-soft">
            {/* Titik clay sebagai penanda daftar: motif identitas, bukan bullet default. */}
            <span aria-hidden="true" className="size-1.5 shrink-0 rounded-full bg-clay" />
            <span className="font-medium text-ink">{item.name}</span>
            {!item.required && (
              <span className="text-xs text-ink-soft">{content.detail.optionalSuffix}</span>
            )}
          </li>
        ))}
      </ul>
      <p className="text-xs text-ink-soft">{content.detail.stapleNote}</p>
    </section>
  );
}

export function RecipeInstructionList({ recipe }: { recipe: Recipe }) {
  return (
    <section className="flex flex-col gap-3">
      <h2 className="font-display text-xl font-semibold text-ink">{content.detail.stepsHeading}</h2>
      <ol className="flex list-decimal flex-col gap-2 pl-5 text-sm text-ink marker:font-mono marker:text-turmeric">
        {recipe.steps.map((step, index) => (
          <li key={index} className="leading-relaxed pl-1">
            {step}
          </li>
        ))}
      </ol>
    </section>
  );
}

/**
 * Detail resep (`docs/component-architecture.md` §8, copy §B.7).
 *
 * Component ini tidak memanggil API — data diberikan oleh page.
 */
export function RecipeDetail({ recipe }: { recipe: Recipe }) {
  return (
    <article className="flex flex-col gap-6">
      <RecipeHeader recipe={recipe} />
      <RecipeMeta recipe={recipe} />
      <RecipeIngredientList recipe={recipe} />
      <RecipeInstructionList recipe={recipe} />
    </article>
  );
}
