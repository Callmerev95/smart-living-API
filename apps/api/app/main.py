"""Entry point Smart Living API.

Tanggung jawab file ini hanya komposisi: bikin aplikasi, pasang middleware,
daftarkan router dan exception handler. Tidak ada business logic di sini.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_v1_router
from app.core.config import get_settings
from app.core.errors import AppError, ErrorCode
from app.schemas.error import ErrorDetail, ErrorResponse

API_V1_PREFIX = "/api/v1"

logger = logging.getLogger("app")

DESCRIPTION = """
Smart Living API mengubah bahan makanan sisa menjadi rekomendasi masakan.

Recommendation engine bersifat **deterministik**: input dan dataset yang sama
selalu menghasilkan urutan hasil yang sama.
""".strip()

TAGS_METADATA = [
    {
        "name": "recommendations",
        "description": "Cari resep berdasarkan bahan yang dimiliki user.",
    },
    {"name": "recipes", "description": "Detail resep."},
    {"name": "ingredients", "description": "Kamus bahan kanonik beserta aliasnya."},
    {"name": "system", "description": "Health check dan metadata operasional."},
]


def _error_response(
    status_code: int,
    code: ErrorCode | str,
    message: str,
    details: object | None = None,
) -> JSONResponse:
    """Bangun response error dalam format `docs/content-schema.md` §A.10.5."""
    payload = ErrorResponse(error=ErrorDetail(code=str(code), message=message, details=details))
    return JSONResponse(status_code=status_code, content=payload.model_dump(by_alias=True))


def register_exception_handlers(app: FastAPI) -> None:
    """Pasang handler agar semua error keluar dalam satu format konsisten."""

    @app.exception_handler(AppError)
    async def handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        return _error_response(exc.status_code, exc.code, exc.message, exc.details)

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        # Ringkas error Pydantic menjadi daftar field + alasan, tanpa membocorkan
        # struktur internal maupun input mentah.
        details = [
            {
                "field": ".".join(str(part) for part in error["loc"][1:]) or "body",
                "reason": error["msg"],
            }
            for error in exc.errors()
        ]
        return _error_response(
            422,
            ErrorCode.VALIDATION_ERROR,
            "Request tidak valid.",
            details,
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        # Stack trace masuk log server, TIDAK dikirim ke client
        # (`docs/technical-architecture.md` §10).
        logger.exception(
            "unhandled_exception",
            extra={"path": request.url.path, "method": request.method},
            exc_info=exc,
        )
        return _error_response(
            500,
            ErrorCode.INTERNAL_ERROR,
            "Terjadi kesalahan di sisi server.",
        )


def create_app() -> FastAPI:
    """Bangun instance FastAPI. Dipakai juga oleh test agar tidak bergantung state global."""
    settings = get_settings()

    app = FastAPI(
        title="Smart Living API",
        description=DESCRIPTION,
        version="0.1.0",
        docs_url="/docs",
        openapi_url="/openapi.json",
        openapi_tags=TAGS_METADATA,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
        expose_headers=["X-Request-ID"],
    )

    register_exception_handlers(app)
    app.include_router(api_v1_router, prefix=API_V1_PREFIX)

    return app


app = create_app()
