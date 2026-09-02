"""Error domain aplikasi dan pemetaannya ke HTTP.

Exception di sini TIDAK mengimpor FastAPI — hanya membawa data. Konversi menjadi
HTTP response terjadi di exception handler (`app/main.py`), sesuai pembagian
tanggung jawab `docs/component-architecture.md` §29.

Kode error adalah kontrak publik (`docs/content-schema.md` §A.10.5): frontend
memetakan `code`, bukan `message`.
"""

from enum import StrEnum
from typing import Any


class ErrorCode(StrEnum):
    """Kode error yang dipakai API. Nilainya bagian dari kontrak, jangan diubah."""

    INVALID_INGREDIENTS = "INVALID_INGREDIENTS"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    RECIPE_NOT_FOUND = "RECIPE_NOT_FOUND"
    INGREDIENT_NOT_FOUND = "INGREDIENT_NOT_FOUND"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class AppError(Exception):
    """Base error aplikasi yang membawa kode dan status HTTP.

    Attributes:
        code: Kode kontrak yang dikirim ke client.
        message: Pesan untuk developer/log.
        status_code: Status HTTP yang sesuai.
        details: Data tambahan opsional.
    """

    code: ErrorCode = ErrorCode.INTERNAL_ERROR
    status_code: int = 500

    def __init__(self, message: str, *, details: Any | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details


class InvalidIngredientsError(AppError):
    """Daftar bahan tidak memenuhi aturan dasar (kosong atau melewati batas)."""

    code = ErrorCode.INVALID_INGREDIENTS
    status_code = 400


class RecipeNotFoundError(AppError):
    """Resep dengan id yang diminta tidak ada."""

    code = ErrorCode.RECIPE_NOT_FOUND
    status_code = 404

    def __init__(self, recipe_id: str) -> None:
        super().__init__(f"Resep `{recipe_id}` tidak ditemukan.")
        self.recipe_id = recipe_id


class IngredientNotFoundError(AppError):
    """Bahan tidak ada di kamus.

    Catatan: TIDAK dipakai endpoint recommendations — bahan tak dikenal di sana
    dikembalikan lewat `unknownIngredients` dengan HTTP 200
    (Contract Delta v1.1 — `docs/content-schema.md` §A.9 Delta 2).
    """

    code = ErrorCode.INGREDIENT_NOT_FOUND
    status_code = 404
