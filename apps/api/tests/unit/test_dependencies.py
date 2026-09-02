"""Test untuk composition root (`app.core.dependencies`).

Fokus: singleton benar-benar di-cache (dataset tidak di-load ulang), dan factory bisa
dipakai tanpa FastAPI.
"""

from pathlib import Path

import pytest

from app.core.config import Settings, get_settings
from app.core.dependencies import (
    build_recommendation_service,
    get_ingredient_repository,
    get_normalizer,
    get_recipe_repository,
    get_recommendation_service,
    reset_caches,
)
from app.repositories.base import IngredientRepository, RecipeRepository
from app.services.ingredient_normalizer import IngredientNormalizer
from app.services.recommendation_service import RecommendationService

DEPENDENCIES_SOURCE = Path(__file__).resolve().parents[2] / "app" / "core" / "dependencies.py"


@pytest.fixture(autouse=True)
def clean_caches() -> None:
    reset_caches()
    get_settings.cache_clear()
    yield
    reset_caches()
    get_settings.cache_clear()


class TestSingletons:
    def test_recipe_repository_is_cached(self) -> None:
        assert get_recipe_repository() is get_recipe_repository()

    def test_ingredient_repository_is_cached(self) -> None:
        assert get_ingredient_repository() is get_ingredient_repository()

    def test_normalizer_is_cached(self) -> None:
        assert get_normalizer() is get_normalizer()

    def test_service_is_cached(self) -> None:
        assert get_recommendation_service() is get_recommendation_service()

    def test_service_reuses_same_repository_instance(self) -> None:
        """Dataset tidak boleh dibaca dua kali untuk service dan route."""
        service = get_recommendation_service()
        assert service._recipe_repository is get_recipe_repository()  # noqa: SLF001
        assert service._ingredient_repository is get_ingredient_repository()  # noqa: SLF001

    def test_reset_caches_creates_new_instances(self) -> None:
        first = get_recipe_repository()
        reset_caches()
        assert get_recipe_repository() is not first


class TestWiring:
    def test_returns_expected_types(self) -> None:
        assert isinstance(get_recipe_repository(), RecipeRepository)
        assert isinstance(get_ingredient_repository(), IngredientRepository)
        assert isinstance(get_normalizer(), IngredientNormalizer)
        assert isinstance(get_recommendation_service(), RecommendationService)

    def test_loads_real_dataset(self) -> None:
        assert get_recipe_repository().count() == 60
        assert get_ingredient_repository().count() == 94

    def test_service_works_end_to_end_without_server(self) -> None:
        """Factory harus bisa dipakai tanpa FastAPI."""
        result = get_recommendation_service().recommend("telur, ayam, wortel")
        assert len(result.results) > 0
        assert result.canonical == ("egg", "chicken", "carrot")

    def test_normalizer_uses_repository_alias_map(self) -> None:
        assert get_normalizer().normalize("telur").canonical == ("egg",)


class TestExplicitBuilder:
    def test_build_with_explicit_settings(self) -> None:
        settings = Settings(_env_file=None)  # type: ignore[call-arg]
        service = build_recommendation_service(settings)
        assert isinstance(service, RecommendationService)
        assert len(service.recommend("telur, ayam").results) > 0

    def test_build_is_not_cached(self) -> None:
        settings = Settings(_env_file=None)  # type: ignore[call-arg]
        assert build_recommendation_service(settings) is not build_recommendation_service(settings)

    def test_build_respects_custom_settings(self) -> None:
        settings = Settings(_env_file=None, default_limit=1)  # type: ignore[call-arg]
        result = build_recommendation_service(settings).recommend("telur, ayam, wortel")
        assert result.limit == 1
        assert len(result.results) == 1

    def test_build_does_not_pollute_singleton_cache(self) -> None:
        settings = Settings(_env_file=None)  # type: ignore[call-arg]
        standalone = build_recommendation_service(settings)
        assert standalone is not get_recommendation_service()


class TestBoundary:
    def test_no_fastapi_import(self) -> None:
        """Composition root harus bisa dipakai tanpa web framework."""
        source = DEPENDENCIES_SOURCE.read_text(encoding="utf-8")
        assert "fastapi" not in source

    def test_dataset_path_comes_from_settings(self) -> None:
        source = DEPENDENCIES_SOURCE.read_text(encoding="utf-8")
        assert "recipes_path" in source
        assert "data/recipes" not in source
