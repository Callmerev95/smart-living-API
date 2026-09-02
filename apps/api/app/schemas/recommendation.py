"""Schema request/response untuk endpoint recommendations.

Kontrak lengkap: `docs/content-schema.md` §A.10.1 — termasuk ketiga Contract Delta
v1.1 (staple exclusion, `unknownIngredients`, normalisasi transparan).
"""

from pydantic import Field, field_validator

from app.core.config import get_settings
from app.core.errors import InvalidIngredientsError
from app.schemas.base import CamelModel

_settings = get_settings()


class RecommendationRequest(CamelModel):
    """Payload `POST /api/v1/recommendations`.

    Batas jumlah dan panjang diambil dari settings, bukan angka hardcode
    (`docs/content-schema.md` §A.7).
    """

    ingredients: list[str] = Field(
        description="Bahan yang dimiliki user. Boleh nama Indonesia maupun Inggris.",
        examples=[["telur", "ayam", "wortel"]],
    )
    limit: int | None = Field(
        default=None,
        ge=1,
        le=_settings.max_limit,
        description=f"Jumlah hasil maksimum (1-{_settings.max_limit})."
        f" Default {_settings.default_limit}.",
        examples=[5],
    )

    @field_validator("ingredients")
    @classmethod
    def _reject_empty_items(cls, value: list[str]) -> list[str]:
        """Buang token kosong, lalu tolak bila tidak ada sisa yang bermakna."""
        cleaned = [item for item in value if item and item.strip()]

        if not cleaned:
            raise InvalidIngredientsError("Bahan harus berisi setidaknya satu item.")

        max_items = _settings.max_ingredients_per_request
        if len(cleaned) > max_items:
            raise InvalidIngredientsError(f"Maksimal {max_items} bahan per pencarian.")

        max_length = _settings.max_ingredient_name_length
        too_long = [item for item in cleaned if len(item) > max_length]
        if too_long:
            raise InvalidIngredientsError(f"Nama bahan maksimal {max_length} karakter.")

        return cleaned


class QuerySchema(CamelModel):
    """Ringkasan input setelah normalisasi (Contract Delta v1.1 Delta 3)."""

    raw: list[str] = Field(
        description="Token asli user setelah trim + lowercase.",
        examples=[["telur", "ayam"]],
    )
    ingredients: list[str] = Field(
        description="Canonical name hasil normalisasi, sudah dedupe.",
        examples=[["egg", "chicken"]],
    )


class RecommendationItem(CamelModel):
    """Satu resep rekomendasi beserta skornya."""

    id: str = Field(examples=["recipe_001"])
    name: str = Field(examples=["Omelet Ayam Wortel"])
    description: str
    match_percentage: int = Field(
        ge=0,
        le=100,
        description="Persentase kecocokan. Bahan pokok dikecualikan dari perhitungan.",
        examples=[100],
    )
    available_ingredients: list[str] = Field(
        description="Bahan utama yang sudah dimiliki user.",
        examples=[["egg", "chicken", "carrot"]],
    )
    missing_ingredients: list[str] = Field(
        description="Bahan utama yang belum dimiliki. Bahan pokok tidak pernah muncul di sini.",
        examples=[[]],
    )
    cooking_time_minutes: int = Field(examples=[15])
    difficulty: str = Field(examples=["easy"])
    servings: int = Field(examples=[2])
    ingredients: list[str] = Field(
        description="Daftar lengkap bahan resep, termasuk opsional dan bahan pokok.",
        examples=[["egg", "chicken", "carrot", "shallot", "salt", "cooking_oil"]],
    )
    steps: list[str]
    tags: list[str] = Field(examples=[["sarapan", "praktis", "indonesian"]])


class MetaSchema(CamelModel):
    """Metadata hasil pencarian."""

    count: int = Field(description="Jumlah item di `results`.", examples=[1])
    limit: int = Field(description="Limit yang dipakai.", examples=[5])
    threshold: int = Field(
        description="Ambang relevansi minimum yang dipakai, untuk transparansi.",
        examples=[30],
    )


class RecommendationResponse(CamelModel):
    """Response `POST /api/v1/recommendations` (`docs/content-schema.md` §A.10.1)."""

    query: QuerySchema
    unknown_ingredients: list[str] = Field(
        default_factory=list,
        description=(
            "Bahan di luar kamus. Dikembalikan dengan HTTP 200, bukan error "
            "(Contract Delta v1.1 Delta 2)."
        ),
        examples=[["kangkung"]],
    )
    results: list[RecommendationItem]
    meta: MetaSchema
