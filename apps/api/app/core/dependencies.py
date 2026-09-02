"""Composition root — satu tempat membangun object graph aplikasi.

Repository dan service di-instansiasi SEKALI per proses (di-cache), bukan per request.
Dataset tidak boleh dibaca ulang setiap request karena akan merusak target latency
(`docs/technical-architecture.md` §16, `docs/development-roadmap.md` §5.3).

Modul ini tidak mengimpor FastAPI: factory-nya bisa dipakai langsung oleh test tanpa
menyalakan server. API layer di P4 membungkusnya dengan `Depends`.
"""

from functools import lru_cache

from app.core.config import Settings, get_settings
from app.repositories.base import IngredientRepository, RecipeRepository
from app.repositories.json_ingredient_repository import JsonIngredientRepository
from app.repositories.json_recipe_repository import JsonRecipeRepository
from app.services.ingredient_normalizer import IngredientNormalizer
from app.services.recommendation_service import RecommendationService


@lru_cache
def get_recipe_repository() -> RecipeRepository:
    """Repository resep sebagai singleton — dataset dibaca sekali saat pertama dipakai."""
    return JsonRecipeRepository(get_settings().recipes_path)


@lru_cache
def get_ingredient_repository() -> IngredientRepository:
    """Repository ingredient sebagai singleton, termasuk alias map yang sudah terbangun."""
    return JsonIngredientRepository(get_settings().ingredients_path)


@lru_cache
def get_normalizer() -> IngredientNormalizer:
    """Normalizer memakai alias map dari repository."""
    return IngredientNormalizer(get_ingredient_repository().get_alias_map())


@lru_cache
def get_recommendation_service() -> RecommendationService:
    """Use case utama, siap dipakai route maupun script."""
    return RecommendationService(
        normalizer=get_normalizer(),
        recipe_repository=get_recipe_repository(),
        ingredient_repository=get_ingredient_repository(),
        settings=get_settings(),
    )


def build_recommendation_service(settings: Settings) -> RecommendationService:
    """Bangun service dengan settings eksplisit, tanpa cache.

    Dipakai test dan script yang perlu dataset atau konfigurasi berbeda tanpa
    mengotori cache singleton.
    """
    ingredient_repository = JsonIngredientRepository(settings.ingredients_path)
    return RecommendationService(
        normalizer=IngredientNormalizer(ingredient_repository.get_alias_map()),
        recipe_repository=JsonRecipeRepository(settings.recipes_path),
        ingredient_repository=ingredient_repository,
        settings=settings,
    )


def reset_caches() -> None:
    """Kosongkan semua cache singleton. Hanya untuk test."""
    get_recipe_repository.cache_clear()
    get_ingredient_repository.cache_clear()
    get_normalizer.cache_clear()
    get_recommendation_service.cache_clear()
