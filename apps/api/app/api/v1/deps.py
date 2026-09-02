"""Dependency provider untuk layer API.

Modul ini adalah satu-satunya jembatan antara FastAPI dan composition root, sehingga
`app/core/dependencies.py` tetap bebas framework dan route tidak menyentuh
repository secara langsung (`docs/component-architecture.md` §25 Rule 2).
"""

from typing import Annotated

from fastapi import Depends

from app.core.dependencies import (
    get_ingredient_repository,
    get_recipe_repository,
    get_recommendation_service,
)
from app.repositories.base import IngredientRepository, RecipeRepository
from app.services.recommendation_service import RecommendationService

RecommendationServiceDep = Annotated[RecommendationService, Depends(get_recommendation_service)]
RecipeRepositoryDep = Annotated[RecipeRepository, Depends(get_recipe_repository)]
IngredientRepositoryDep = Annotated[IngredientRepository, Depends(get_ingredient_repository)]
