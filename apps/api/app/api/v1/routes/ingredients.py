"""Endpoint kamus bahan (`docs/content-schema.md` §A.10.3)."""

from fastapi import APIRouter

from app.api.v1.deps import IngredientRepositoryDep
from app.schemas.ingredient import IngredientListResponse
from app.schemas.mappers import to_ingredient_list_response

router = APIRouter(tags=["ingredients"])


@router.get(
    "/ingredients",
    response_model=IngredientListResponse,
    summary="Daftar bahan kanonik",
    description=(
        "Mengembalikan seluruh bahan yang dikenali sistem beserta alias, kategori, "
        "dan penanda bahan pokok. Dipakai untuk autocomplete dan dokumentasi."
    ),
)
def list_ingredients(repository: IngredientRepositoryDep) -> IngredientListResponse:
    return to_ingredient_list_response(repository.get_all())
