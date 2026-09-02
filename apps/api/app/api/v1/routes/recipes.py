"""Endpoint detail resep (`docs/content-schema.md` §A.10.2)."""

from fastapi import APIRouter, Path

from app.api.v1.deps import RecipeRepositoryDep
from app.core.errors import RecipeNotFoundError
from app.schemas.error import ErrorResponse
from app.schemas.mappers import to_recipe_response
from app.schemas.recipe import RecipeResponse

router = APIRouter(tags=["recipes"])


@router.get(
    "/recipes/{recipe_id}",
    response_model=RecipeResponse,
    summary="Detail satu resep",
    description=(
        "Mengembalikan resep lengkap berdasarkan id. Field yang berkaitan dengan "
        "kecocokan tidak disertakan karena hanya bermakna dalam konteks pencarian."
    ),
    responses={404: {"model": ErrorResponse, "description": "Resep tidak ditemukan."}},
)
def get_recipe(
    repository: RecipeRepositoryDep,
    recipe_id: str = Path(description="Id resep, format `recipe_NNN`.", examples=["recipe_001"]),
) -> RecipeResponse:
    recipe = repository.get_by_id(recipe_id)

    if recipe is None:
        raise RecipeNotFoundError(recipe_id)

    return to_recipe_response(recipe)
