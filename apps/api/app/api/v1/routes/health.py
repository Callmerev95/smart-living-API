"""Health endpoint (`docs/content-schema.md` §A.10.4).

Menyertakan jumlah resep dan bahan sebagai bukti dataset benar-benar ter-load —
lebih berguna daripada `{"status": "ok"}` polos.
"""

from fastapi import APIRouter

from app.api.v1.deps import IngredientRepositoryDep, RecipeRepositoryDep
from app.schemas.ingredient import HealthResponse

router = APIRouter(tags=["system"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Memastikan API hidup dan dataset resep sudah termuat di memori.",
)
def health(
    recipe_repository: RecipeRepositoryDep,
    ingredient_repository: IngredientRepositoryDep,
) -> HealthResponse:
    return HealthResponse(
        status="ok",
        recipe_count=recipe_repository.count(),
        ingredient_count=ingredient_repository.count(),
    )
