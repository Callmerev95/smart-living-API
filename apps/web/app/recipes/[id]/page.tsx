import type { Metadata } from "next";

import { RecipeDetailLoader } from "@/components/recipes/RecipeDetailLoader";
import { content } from "@/lib/constants/content";

export async function generateMetadata(
  props: PageProps<"/recipes/[id]">,
): Promise<Metadata> {
  const { id } = await props.params;
  return {
    title: `${id} — ${content.meta.ogTitle}`,
  };
}

export default async function RecipePage(props: PageProps<"/recipes/[id]">) {
  const { id } = await props.params;

  return (
    <main className="mx-auto w-full max-w-3xl px-6 py-12">
      <RecipeDetailLoader recipeId={id} />
    </main>
  );
}
