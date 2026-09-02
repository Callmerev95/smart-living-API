"""Schema untuk endpoint ingredients (`docs/content-schema.md` §A.10.3)."""

from pydantic import Field

from app.schemas.base import CamelModel


class IngredientItem(CamelModel):
    """Satu bahan kanonik beserta alias dan flag bahan pokok."""

    name: str = Field(description="Canonical name.", examples=["egg"])
    display_name: str = Field(description="Label bahasa Indonesia.", examples=["Telur"])
    aliases: list[str] = Field(examples=[["telur", "telor", "eggs"]])
    category: str = Field(examples=["protein"])
    staple: bool = Field(
        description="Bahan pokok dapur — dianggap selalu tersedia dan dikecualikan dari scoring.",
        examples=[False],
    )


class IngredientListMeta(CamelModel):
    """Metadata daftar bahan."""

    count: int = Field(examples=[94])


class IngredientListResponse(CamelModel):
    """Response `GET /api/v1/ingredients`."""

    ingredients: list[IngredientItem]
    meta: IngredientListMeta


class HealthResponse(CamelModel):
    """Response `GET /api/v1/health` (`docs/content-schema.md` §A.10.4).

    `recipeCount`/`ingredientCount` membuktikan dataset benar-benar ter-load —
    lebih berguna daripada `{"status": "ok"}` polos.
    """

    status: str = Field(examples=["ok"])
    recipe_count: int = Field(examples=[60])
    ingredient_count: int = Field(examples=[94])
