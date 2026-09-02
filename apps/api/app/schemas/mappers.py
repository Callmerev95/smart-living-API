"""Mapper domain -> schema.

Satu-satunya tempat objek domain bertemu Pydantic. Ini yang menjaga
`app/domain/` tetap bebas framework: konversi terjadi di boundary, bukan dengan
membuat domain model mewarisi `BaseModel` (`AGENTS.md` §4).

Semua fungsi di sini murni — tanpa akses repository maupun file.
"""

from collections.abc import Sequence

from app.domain.models.ingredient import Ingredient
from app.domain.models.recipe import Recipe
from app.schemas.ingredient import IngredientItem, IngredientListMeta, IngredientListResponse
from app.schemas.recipe import RecipeIngredientSchema, RecipeResponse
from app.schemas.recommendation import (
    MetaSchema,
    QuerySchema,
    RecommendationItem,
    RecommendationResponse,
)
from app.services.recommendation_service import RecommendationResult


def to_recommendation_response(result: RecommendationResult) -> RecommendationResponse:
    """Gabungkan skor (`MatchResult`) dengan data resep menjadi response.

    `MatchResult` sengaja tidak menyimpan nama/steps resep, jadi mapper yang
    menyatukan keduanya memakai `result.recipes`. Urutan `result.results`
    dipertahankan apa adanya — mapper TIDAK melakukan sorting ulang.
    """
    items: list[RecommendationItem] = []

    for match in result.results:
        recipe = result.recipes.get(match.recipe_id)
        if recipe is None:
            # Skor mengacu resep yang tidak ada: hanya mungkin bila dataset
            # berubah di tengah proses. Lewati daripada mengirim data separuh.
            continue

        items.append(
            RecommendationItem(
                id=recipe.id,
                name=recipe.name,
                description=recipe.description,
                match_percentage=match.match_percentage,
                available_ingredients=list(match.available_ingredients),
                missing_ingredients=list(match.missing_ingredients),
                cooking_time_minutes=recipe.cooking_time_minutes,
                difficulty=recipe.difficulty.value,
                servings=recipe.servings,
                ingredients=list(recipe.all_ingredient_names()),
                steps=list(recipe.steps),
                tags=list(recipe.tags),
            )
        )

    return RecommendationResponse(
        query=QuerySchema(raw=list(result.raw), ingredients=list(result.canonical)),
        unknown_ingredients=list(result.unknown),
        results=items,
        meta=MetaSchema(count=len(items), limit=result.limit, threshold=result.threshold),
    )


def to_recipe_response(recipe: Recipe) -> RecipeResponse:
    """Konversi satu resep menjadi response detail."""
    return RecipeResponse(
        id=recipe.id,
        name=recipe.name,
        description=recipe.description,
        ingredients=[
            RecipeIngredientSchema(name=item.name, required=item.required)
            for item in recipe.ingredients
        ],
        cooking_time_minutes=recipe.cooking_time_minutes,
        difficulty=recipe.difficulty.value,
        servings=recipe.servings,
        steps=list(recipe.steps),
        tags=list(recipe.tags),
        source=recipe.source,
    )


def to_ingredient_list_response(
    ingredients: Sequence[Ingredient],
) -> IngredientListResponse:
    """Konversi kamus bahan menjadi response daftar."""
    items = [
        IngredientItem(
            name=ingredient.name,
            display_name=ingredient.display_name,
            aliases=list(ingredient.aliases),
            category=ingredient.category.value,
            staple=ingredient.staple,
        )
        for ingredient in ingredients
    ]

    return IngredientListResponse(
        ingredients=items,
        meta=IngredientListMeta(count=len(items)),
    )
