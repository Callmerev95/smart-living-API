"""Test untuk `RecommendationService`.

Memakai fake repository in-memory, bukan file nyata — service test harus cepat dan
terisolasi dari dataset.
"""

from collections.abc import Mapping
from pathlib import Path

import pytest

from app.core.config import Settings
from app.domain.models.ingredient import Ingredient, IngredientCategory
from app.domain.models.recipe import Difficulty, Recipe, RecipeIngredient
from app.repositories.base import IngredientRepository, RecipeRepository
from app.services.ingredient_normalizer import IngredientNormalizer
from app.services.recommendation_service import RecommendationResult, RecommendationService

SERVICE_SOURCE = (
    Path(__file__).resolve().parents[2] / "app" / "services" / "recommendation_service.py"
)


# --------------------------------------------------------------------------- #
# Fake repository
# --------------------------------------------------------------------------- #


class FakeRecipeRepository(RecipeRepository):
    def __init__(self, recipes: tuple[Recipe, ...]) -> None:
        self._recipes = recipes

    def get_all(self) -> tuple[Recipe, ...]:
        return self._recipes

    def get_by_id(self, recipe_id: str) -> Recipe | None:
        return next((r for r in self._recipes if r.id == recipe_id), None)

    def count(self) -> int:
        return len(self._recipes)


class FakeIngredientRepository(IngredientRepository):
    def __init__(self, ingredients: tuple[Ingredient, ...]) -> None:
        self._ingredients = ingredients

    def get_all(self) -> tuple[Ingredient, ...]:
        return self._ingredients

    def get_by_name(self, name: str) -> Ingredient | None:
        return next((i for i in self._ingredients if i.name == name), None)

    def get_alias_map(self) -> Mapping[str, str]:
        mapping: dict[str, str] = {}
        for ingredient in self._ingredients:
            mapping[ingredient.name] = ingredient.name
            for alias in ingredient.aliases:
                mapping[alias] = ingredient.name
        return mapping

    def get_staple_names(self) -> frozenset[str]:
        return frozenset(i.name for i in self._ingredients if i.staple)

    def count(self) -> int:
        return len(self._ingredients)


# --------------------------------------------------------------------------- #
# Fixture data
# --------------------------------------------------------------------------- #


def ingredient(name: str, *, aliases: tuple[str, ...] = (), staple: bool = False) -> Ingredient:
    return Ingredient(
        name=name,
        display_name=name.replace("_", " ").title(),
        aliases=aliases,
        category=IngredientCategory.STAPLE if staple else IngredientCategory.PROTEIN,
        staple=staple,
    )


INGREDIENTS = (
    ingredient("egg", aliases=("telur", "eggs")),
    ingredient("chicken", aliases=("ayam",)),
    ingredient("carrot", aliases=("wortel", "carrots")),
    ingredient("tofu", aliases=("tahu",)),
    ingredient("onion", aliases=("bawang bombay",)),
    ingredient("salt", aliases=("garam",), staple=True),
    ingredient("cooking_oil", aliases=("minyak",), staple=True),
)


def recipe(
    recipe_id: str,
    *items: tuple[str, bool],
    minutes: int = 15,
) -> Recipe:
    return Recipe(
        id=recipe_id,
        name=f"Resep {recipe_id}",
        description="Resep uji.",
        ingredients=tuple(RecipeIngredient(name=n, required=r) for n, r in items),
        cooking_time_minutes=minutes,
        difficulty=Difficulty.EASY,
        servings=2,
        steps=("a", "b", "c"),
        tags=("praktis",),
        source="original",
    )


RECIPES = (
    # 100% untuk egg+chicken+carrot
    recipe("recipe_001", ("egg", True), ("chicken", True), ("carrot", True), minutes=15),
    # 67% — butuh onion
    recipe("recipe_002", ("egg", True), ("chicken", True), ("onion", True), minutes=20),
    # 100% tapi staple-heavy — memvalidasi Delta 1
    recipe(
        "recipe_003",
        ("egg", True),
        ("chicken", True),
        ("salt", True),
        ("cooking_oil", True),
        minutes=10,
    ),
    # 0% — tidak akan lolos threshold
    recipe("recipe_004", ("tofu", True), ("onion", True), minutes=25),
)


def build_service(
    recipes: tuple[Recipe, ...] = RECIPES,
    ingredients: tuple[Ingredient, ...] = INGREDIENTS,
    **setting_overrides: object,
) -> RecommendationService:
    settings = Settings(_env_file=None, **setting_overrides)  # type: ignore[arg-type]
    ingredient_repo = FakeIngredientRepository(ingredients)
    return RecommendationService(
        normalizer=IngredientNormalizer(ingredient_repo.get_alias_map()),
        recipe_repository=FakeRecipeRepository(recipes),
        ingredient_repository=ingredient_repo,
        settings=settings,
    )


@pytest.fixture
def service() -> RecommendationService:
    return build_service()


def ids(result: RecommendationResult) -> list[str]:
    return [r.recipe_id for r in result.results]


# --------------------------------------------------------------------------- #
# Alur utama
# --------------------------------------------------------------------------- #


class TestRecommend:
    def test_returns_ranked_results(self, service: RecommendationService) -> None:
        result = service.recommend("telur, ayam, wortel")
        # recipe_001 dan recipe_003 keduanya 100%; recipe_003 lebih cepat (10 menit)
        assert ids(result) == ["recipe_003", "recipe_001", "recipe_002"]

    def test_normalizes_indonesian_input(self, service: RecommendationService) -> None:
        result = service.recommend("telur, ayam")
        assert result.canonical == ("egg", "chicken")

    def test_below_threshold_is_excluded(self, service: RecommendationService) -> None:
        """recipe_004 (0%) tidak boleh muncul."""
        result = service.recommend("telur, ayam, wortel")
        assert "recipe_004" not in ids(result)

    def test_empty_input_returns_no_results(self, service: RecommendationService) -> None:
        result = service.recommend("")
        assert result.results == ()
        assert result.canonical == ()

    def test_result_type(self, service: RecommendationService) -> None:
        assert isinstance(service.recommend("telur"), RecommendationResult)


# --------------------------------------------------------------------------- #
# Contract Delta v1.1
# --------------------------------------------------------------------------- #


class TestContractDelta:
    def test_delta1_staple_excluded_from_score(self, service: RecommendationService) -> None:
        """recipe_003 butuh salt + cooking_oil tapi tetap 100% dengan egg + chicken."""
        result = service.recommend("telur, ayam")
        by_id = {r.recipe_id: r for r in result.results}
        assert by_id["recipe_003"].match_percentage == 100
        assert by_id["recipe_003"].missing_ingredients == ()

    def test_delta2_unknown_reported_not_raised(self, service: RecommendationService) -> None:
        result = service.recommend("telur, kangkung, ayam")
        assert result.unknown == ("kangkung",)
        assert len(result.results) > 0

    def test_delta2_all_unknown_gives_empty_results(self, service: RecommendationService) -> None:
        result = service.recommend("kangkung, durian")
        assert result.results == ()
        assert result.unknown == ("kangkung", "durian")

    def test_delta3_raw_and_canonical_both_present(self, service: RecommendationService) -> None:
        result = service.recommend("Telur, AYAM")
        assert result.raw == ("telur", "ayam")
        assert result.canonical == ("egg", "chicken")

    def test_threshold_is_reported(self, service: RecommendationService) -> None:
        assert service.recommend("telur").threshold == 30


# --------------------------------------------------------------------------- #
# Urutan operasi: filter sebelum limit
# --------------------------------------------------------------------------- #


class TestOperationOrder:
    def test_filter_runs_before_limit(self) -> None:
        """Limit 4 tidak boleh terisi oleh hasil 0% hanya karena slot masih ada."""
        service = build_service()
        result = service.recommend("telur, ayam, wortel", limit=4)
        assert len(result.results) == 3
        assert all(r.match_percentage >= 30 for r in result.results)

    def test_limit_applied_after_ranking(self) -> None:
        service = build_service()
        full = service.recommend("telur, ayam, wortel", limit=10)
        limited = service.recommend("telur, ayam, wortel", limit=2)
        assert ids(limited) == ids(full)[:2]

    def test_custom_threshold_changes_result_count(self) -> None:
        service = build_service(min_match_threshold=100)
        result = service.recommend("telur, ayam")
        assert all(r.match_percentage == 100 for r in result.results)
        assert "recipe_002" not in ids(result)


# --------------------------------------------------------------------------- #
# Limit resolution
# --------------------------------------------------------------------------- #


class TestLimitResolution:
    def test_none_uses_default_limit(self) -> None:
        service = build_service(default_limit=2)
        result = service.recommend("telur, ayam, wortel")
        assert result.limit == 2
        assert len(result.results) == 2

    def test_explicit_limit_respected(self, service: RecommendationService) -> None:
        result = service.recommend("telur, ayam, wortel", limit=1)
        assert result.limit == 1
        assert len(result.results) == 1

    def test_limit_clamped_to_max(self) -> None:
        service = build_service(max_limit=2)
        result = service.recommend("telur, ayam, wortel", limit=99)
        assert result.limit == 2

    def test_limit_clamped_to_minimum_one(self, service: RecommendationService) -> None:
        assert service.recommend("telur", limit=0).limit == 1
        assert service.recommend("telur", limit=-5).limit == 1


# --------------------------------------------------------------------------- #
# Boundary — service tidak boleh tahu HTTP, file, atau menghitung skor
# --------------------------------------------------------------------------- #


class TestBoundary:
    def test_no_http_or_file_access(self) -> None:
        source = SERVICE_SOURCE.read_text(encoding="utf-8")
        for forbidden in ("fastapi", "httpx", "requests", "openai", "json.load", "open("):
            assert forbidden not in source, f"service tidak boleh menyebut {forbidden}"

    def test_does_not_compute_percentage_itself(self) -> None:
        """Perhitungan skor didelegasikan ke engine, bukan dihitung ulang di service."""
        source = SERVICE_SOURCE.read_text(encoding="utf-8")
        assert "* 100" not in source
        assert "calculate_match_percentage" not in source

    def test_does_not_sort_directly(self) -> None:
        source = SERVICE_SOURCE.read_text(encoding="utf-8")
        assert "sorted(" not in source
        assert ".sort(" not in source

    def test_works_with_fake_repositories(self, service: RecommendationService) -> None:
        """Service hanya bergantung pada interface — terbukti karena fake repo bekerja."""
        assert len(service.recommend("telur, ayam").results) > 0


# --------------------------------------------------------------------------- #
# Determinisme
# --------------------------------------------------------------------------- #


class TestDeterminism:
    def test_same_input_same_output(self, service: RecommendationService) -> None:
        first = service.recommend("telur, ayam, wortel")
        second = service.recommend("telur, ayam, wortel")
        assert first == second

    def test_input_order_does_not_change_ranking(self, service: RecommendationService) -> None:
        first = service.recommend("telur, ayam, wortel")
        second = service.recommend("wortel, ayam, telur")
        assert ids(first) == ids(second)

    def test_recipe_repository_order_does_not_change_ranking(self) -> None:
        forward = build_service(recipes=RECIPES)
        reversed_repo = build_service(recipes=tuple(reversed(RECIPES)))
        assert ids(forward.recommend("telur, ayam, wortel")) == ids(
            reversed_repo.recommend("telur, ayam, wortel")
        )
