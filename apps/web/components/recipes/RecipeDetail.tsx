import { Badge } from "@/components/ui/Badge";
import { content, fill } from "@/lib/constants/content";
import type { Recipe } from "@/types/api";

export function RecipeHeader({ recipe }: { recipe: Recipe }) {
  return (
    <header className="flex flex-col gap-2">
      <h1 className="text-3xl font-semibold text-zinc-900">{recipe.name}</h1>
      <p className="text-zinc-600">{recipe.description}</p>
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
      <h2 className="text-lg font-semibold text-zinc-900">{content.detail.metaHeading}</h2>
      <p className="text-sm text-zinc-600">
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
    <section className="flex flex-col gap-2">
      <h2 className="text-lg font-semibold text-zinc-900">
        {content.detail.ingredientsHeading}
      </h2>
      <ul className="flex flex-col gap-1 text-sm text-zinc-700">
        {recipe.ingredients.map((item) => (
          <li key={item.name} className="flex items-center gap-2">
            <span>{item.name}</span>
            {!item.required && (
              <span className="text-xs text-zinc-500">{content.detail.optionalSuffix}</span>
            )}
          </li>
        ))}
      </ul>
      <p className="text-xs text-zinc-500">{content.detail.stapleNote}</p>
    </section>
  );
}

export function RecipeInstructionList({ recipe }: { recipe: Recipe }) {
  return (
    <section className="flex flex-col gap-2">
      <h2 className="text-lg font-semibold text-zinc-900">{content.detail.stepsHeading}</h2>
      <ol className="flex list-decimal flex-col gap-2 pl-5 text-sm text-zinc-700">
        {recipe.steps.map((step, index) => (
          <li key={index}>{step}</li>
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
