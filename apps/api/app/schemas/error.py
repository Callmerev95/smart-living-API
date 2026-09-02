"""Schema error API — format konsisten `docs/content-schema.md` §A.10.5."""

from typing import Any

from pydantic import Field

from app.schemas.base import CamelModel


class ErrorDetail(CamelModel):
    """Isi objek `error`."""

    code: str = Field(description="Kode error yang stabil sebagai kontrak.")
    message: str = Field(description="Pesan yang bisa dibaca developer.")
    details: Any | None = Field(
        default=None,
        description="Informasi tambahan opsional, mis. daftar field yang tidak valid.",
    )


class ErrorResponse(CamelModel):
    """Envelope error. Semua error API memakai bentuk ini tanpa kecuali."""

    error: ErrorDetail

    model_config = {
        **CamelModel.model_config,
        "json_schema_extra": {
            "examples": [
                {
                    "error": {
                        "code": "INVALID_INGREDIENTS",
                        "message": "Bahan harus berisi setidaknya satu item.",
                        "details": None,
                    }
                }
            ]
        },
    }
