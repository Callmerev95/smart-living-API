import type { Metadata } from "next";

import { RecipeDetailLoader } from "@/components/recipes/RecipeDetailLoader";
import { getRecipe } from "@/lib/api/recipes";
import { content, fill } from "@/lib/constants/content";

/**
 * Title memakai nama resep, bukan ID — `recipe_001 — Smart Living` tidak berguna
 * untuk SEO maupun saat link dibagikan.
 *
 * Kegagalan fetch (ID tak dikenal, API down) tidak boleh membuat halaman gagal
 * di-render: fallback ke judul situs, dan `RecipeDetailLoader` yang menampilkan
 * state not-found/error-nya.
 */
export async function generateMetadata(
  props: PageProps<"/recipes/[id]">,
): Promise<Metadata> {
  const { id } = await props.params;

  try {
    const recipe = await getRecipe(id);
    return {
      title: fill(content.meta.detailTitle, { name: recipe.name }),
      description: recipe.description,
    };
  } catch {
    return { title: content.meta.ogTitle };
  }
}

export default async function RecipePage(props: PageProps<"/recipes/[id]">) {
  const { id } = await props.params;

  return (
    <main id="main-content" className="mx-auto w-full max-w-3xl px-6 py-12">
      <RecipeDetailLoader recipeId={id} />
    </main>
  );
}
