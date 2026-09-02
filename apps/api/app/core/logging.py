"""Logging terstruktur dan korelasi request.

Field wajib per request (`docs/technical-architecture.md` §18):
`request_id`, `method`, `path`, `status_code`, `duration_ms`.

Yang TIDAK boleh masuk log: isi lengkap bahan user, secret, API key, header
Authorization (PRD §14). Endpoint recommendations hanya melog jumlah, bukan isi.
"""

import logging
import time
import uuid
from collections.abc import Awaitable, Callable

from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

REQUEST_ID_HEADER = "X-Request-ID"

logger = logging.getLogger("app.request")


def configure_logging(level: str) -> None:
    """Setup handler root satu kali. Idempoten agar aman dipanggil ulang oleh test."""
    root = logging.getLogger()
    resolved = getattr(logging, level.upper(), logging.INFO)
    root.setLevel(resolved)

    if not any(getattr(handler, "_smart_living", False) for handler in root.handlers):
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
        handler._smart_living = True  # type: ignore[attr-defined]
        root.addHandler(handler)


class RequestLoggingMiddleware:
    """Middleware ASGI yang melog ringkasan setiap request.

    Ditulis sebagai kelas ASGI (bukan `BaseHTTPMiddleware`) supaya tetap bekerja
    bersama exception handler global: response error yang dihasilkan handler tetap
    tercatat dengan status code yang benar.
    """

    def __init__(self, app: ASGIApp) -> None:
        self._app = app

    async def __call__(self, scope, receive, send) -> None:  # type: ignore[no-untyped-def]
        if scope["type"] != "http":
            await self._app(scope, receive, send)
            return

        request_id = str(uuid.uuid4())
        scope.setdefault("state", {})
        scope["state"]["request_id"] = request_id

        started = time.perf_counter()
        status_code = 500

        async def send_with_request_id(message) -> None:  # type: ignore[no-untyped-def]
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
                headers = message.setdefault("headers", [])
                headers.append((REQUEST_ID_HEADER.lower().encode(), request_id.encode()))
            await send(message)

        try:
            await self._app(scope, receive, send_with_request_id)
        finally:
            duration_ms = round((time.perf_counter() - started) * 1000, 2)
            logger.info(
                "request_completed",
                extra={
                    "request_id": request_id,
                    "method": scope.get("method", ""),
                    "path": scope.get("path", ""),
                    "status_code": status_code,
                    "duration_ms": duration_ms,
                },
            )


def log_recommendation(
    request: Request,
    ingredient_count: int,
    result_count: int,
    unknown_count: int,
) -> None:
    """Log metrik rekomendasi tanpa membocorkan isi bahan user.

    Hanya jumlah yang dicatat — cukup untuk metrik empty-result rate
    (`docs/technical-architecture.md` §18) tanpa menyimpan data pribadi.
    """
    logger.info(
        "recommendation_served",
        extra={
            "request_id": getattr(request.state, "request_id", None),
            "ingredient_count": ingredient_count,
            "result_count": result_count,
            "unknown_count": unknown_count,
        },
    )


LoggingCallNext = Callable[[Request], Awaitable[Response]]
