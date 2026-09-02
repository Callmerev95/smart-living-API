"""Test untuk mapper domain -> schema."""

from pathlib import Path

from app.domain.models.ingredient import Ingredient, IngredientCategory
from app.domain.models.match_result import MatchResult
from app.domain.models.recipe import Difficulty, Recipe, RecipeIngredient
from app.schemas.mappers import (
    to_ingredient_list_response,
    to_recipe_response,
    to_recommendation_response,
)
from app.services.recommendation_service import RecommendationResult

MAPPERS_SOURCE = Path(__file__).resolve().parents[2] / "app" / "schemas" / "mappers.py"


def recipe(recipe_id: str = "recipe_001", minutes: int = 15) -> Recipe:
    return Recipe(
        id=recipe_id,
        name="Omelet Ayam Wortel",
        description="Omelet praktis dengan ayam dan wortel.",
        ingredients=(
            RecipeIngredient(name="egg", required=True),
            RecipeIngredient(name="chicken", required=True),
            RecipeIngredient(name="shallot", required=False),
            RecipeIngredient(name="salt", required=True),
        ),
        cooking_time_minutes=minutes,
        difficulty=Difficulty.EASY,
        servings=2,
        steps=("Kocok telur.", "Tumis ayam.", "Sajikan."),
        tags=("sarapan", "praktis"),
        source="original",
    )


def match(recipe_id: str = "recipe_001", pct: int = 100) -> MatchResult:
    return MatchResult(
        recipe_id=recipe_id,
        match_percentage=pct,
        available_ingredients=("egg", "chicken"),
        missing_ingredients=(),
        cooking_time_minutes=15,
    )


def domain_result(
    *,
    recipes: dict[str, Recipe] | None = None,
    **overrides: object,
) -> RecommendationResult:
    defaults: dict[str, object] = {
        "raw": ("telur", "ayam"),
        "canonical": ("egg", "chicken"),
        "unknown": (),
        "results": (match(),),
        "recipes": recipes if recipes is not None else {"recipe_001": recipe()},
        "limit": 5,
        "threshold": 30,
    }
    defaults.update(overrides)
    return RecommendationResult(**defaults)  # type: ignore[arg-type]


class TestRecommendationMapper:
    def test_merges_match_with_recipe_data(self) -> None:
        """MatchResult hanya punya skor; nama & steps berasal dari Recipe."""
        response = to_recommendation_response(domain_result())
        result = response.results[0]
        assert result.id == "recipe_001"
        assert result.name == "Omelet Ayam Wortel"
        assert result.match_percentage == 100
        assert result.steps == ["Kocok telur.", "Tumis ayam.", "Sajikan."]

    def test_ingredients_field_is_full_list(self) -> None:
        """Field `ingredients` memuat semua bahan termasuk opsional dan staple."""
        response = to_recommendation_response(domain_result())
        assert response.results[0].ingredients == ["egg", "chicken", "shallot", "salt"]

    def test_preserves_service_order(self) -> None:
        """Mapper tidak boleh me-sort ulang hasil dari service."""
        result = domain_result(
            results=(match("recipe_002", 60), match("recipe_001", 100)),
            recipes={"recipe_001": recipe("recipe_001"), "recipe_002": recipe("recipe_002")},
        )
        response = to_recommendation_response(result)
        assert [r.id for r in response.results] == ["recipe_002", "recipe_001"]

    def test_unknown_passed_through(self) -> None:
        response = to_recommendation_response(domain_result(unknown=("kangkung",)))
        assert response.unknown_ingredients == ["kangkung"]

    def test_query_carries_raw_and_canonical(self) -> None:
        response = to_recommendation_response(domain_result())
        assert response.query.raw == ["telur", "ayam"]
        assert response.query.ingredients == ["egg", "chicken"]

    def test_meta_count_matches_results(self) -> None:
        response = to_recommendation_response(domain_result())
        assert response.meta.count == len(response.results) == 1

    def test_meta_reports_limit_and_threshold(self) -> None:
        response = to_recommendation_response(domain_result(limit=3, threshold=50))
        assert response.meta.limit == 3
        assert response.meta.threshold == 50

    def test_missing_recipe_in_lookup_is_skipped(self) -> None:
        """Skor tanpa resep pasangannya dilewati, bukan mengirim data separuh."""
        response = to_recommendation_response(domain_result(recipes={}))
        assert response.results == []
        assert response.meta.count == 0

    def test_empty_results(self) -> None:
        response = to_recommendation_response(domain_result(results=(), recipes={}))
        assert response.results == []
        assert response.meta.count == 0

    def test_difficulty_serialized_as_string(self) -> None:
        response = to_recommendation_response(domain_result())
        payload = response.model_dump(by_alias=True)
        assert payload["results"][0]["difficulty"] == "easy"


class TestRecipeMapper:
    def test_maps_all_fields(self) -> None:
        response = to_recipe_response(recipe())
        assert response.id == "recipe_001"
        assert response.difficulty == "easy"
        assert response.source == "original"
        assert len(response.ingredients) == 4

    def test_preserves_ingredient_order_and_flags(self) -> None:
        response = to_recipe_response(recipe())
        assert [i.name for i in response.ingredients] == ["egg", "chicken", "shallot", "salt"]
        assert [i.required for i in response.ingredients] == [True, True, False, True]


class TestIngredientMapper:
    def test_maps_list_with_meta(self) -> None:
        ingredients = [
            Ingredient(
                name="egg",
                display_name="Telur",
                aliases=("telur",),
                category=IngredientCategory.PROTEIN,
                staple=False,
            ),
            Ingredient(
                name="salt",
                display_name="Garam",
                aliases=("garam",),
                category=IngredientCategory.STAPLE,
                staple=True,
            ),
        ]
        response = to_ingredient_list_response(ingredients)
        assert response.meta.count == 2
        assert response.ingredients[1].staple is True
        assert response.ingredients[0].display_name == "Telur"

    def test_empty_list(self) -> None:
        response = to_ingredient_list_response([])
        assert response.ingredients == []
        assert response.meta.count == 0


class TestPurity:
    def test_mapper_does_not_access_repository_or_files(self) -> None:
        source = MAPPERS_SOURCE.read_text(encoding="utf-8")
        for forbidden in ("open(", "json.load", "Repository(", "get_settings"):
            assert forbidden not in source, f"mapper tidak boleh memakai {forbidden}"

    def test_mapper_does_not_sort(self) -> None:
        source = MAPPERS_SOURCE.read_text(encoding="utf-8")
        assert "sorted(" not in source
        assert ".sort(" not in source
