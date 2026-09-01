"""Health endpoint.

Versi minimal (T-P1-07). Field `recipeCount`/`ingredientCount` ditambahkan di
T-P4-13 setelah repository tersedia.
"""

from fastapi import APIRouter

router = APIRouter(tags=["system"])


@router.get(
    "/health",
    summary="Health check",
    description="Memastikan API hidup dan bisa menerima request.",
)
def health() -> dict[str, str]:
    return {"status": "ok"}
