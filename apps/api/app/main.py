"""Entry point Smart Living API.

Tanggung jawab file ini hanya komposisi: bikin aplikasi, pasang middleware,
daftarkan router. Tidak ada business logic di sini.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_v1_router
from app.core.config import get_settings

API_V1_PREFIX = "/api/v1"

DESCRIPTION = """
Smart Living API mengubah bahan makanan sisa menjadi rekomendasi masakan.

Recommendation engine bersifat **deterministik**: input dan dataset yang sama
selalu menghasilkan urutan hasil yang sama.
""".strip()


def create_app() -> FastAPI:
    """Bangun instance FastAPI. Dipakai juga oleh test agar tidak bergantung state global."""
    settings = get_settings()

    app = FastAPI(
        title="Smart Living API",
        description=DESCRIPTION,
        version="0.1.0",
        docs_url="/docs",
        openapi_url="/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )

    app.include_router(api_v1_router, prefix=API_V1_PREFIX)

    return app


app = create_app()
