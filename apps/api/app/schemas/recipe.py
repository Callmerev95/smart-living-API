"""Schema untuk endpoint recipes dan ingredients.

Kontrak: `docs/content-schema.md` §A.10.2 dan §A.10.3.
"""

from pydantic import Field

from app.schemas.base import CamelModel


class RecipeIngredientSchema(CamelModel):
    """Satu baris bahan di dalam resep."""

    name: str = Field(examples=["egg"])
    required: bool = Field(
        description="Bahan opsional (`false`) tidak memengaruhi persentase kecocokan.",
        examples=[True],
    )


class RecipeResponse(CamelModel):
    """Detail resep.

    Sengaja TIDAK memuat `matchPercentage`/`availableIngredients`/`missingIngredients`
    — field itu hanya bermakna dalam konteks query rekomendasi
    (`docs/content-schema.md` §A.10.2).
    """

    id: str = Field(examples=["recipe_001"])
    name: str = Field(examples=["Omelet Ayam Wortel"])
    description: str
    ingredients: list[RecipeIngredientSchema]
    cooking_time_minutes: int = Field(examples=[15])
    difficulty: str = Field(examples=["easy"])
    servings: int = Field(examples=[2])
    steps: list[str]
    tags: list[str] = Field(examples=[["sarapan", "praktis", "indonesian"]])
    source: str = Field(examples=["original"])
