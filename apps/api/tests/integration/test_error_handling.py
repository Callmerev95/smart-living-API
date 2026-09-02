"""Integration test untuk exception handler global."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.errors import AppError, InvalidIngredientsError, RecipeNotFoundError
from app.main import create_app, register_exception_handlers


@pytest.fixture
def failing_app() -> FastAPI:
    """App kecil dengan endpoint yang sengaja gagal, untuk menguji handler."""
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/boom/unexpected")
    def unexpected() -> None:
        raise RuntimeError("secret internal detail: db password abc123")

    @app.get("/boom/app-error")
    def app_error() -> None:
        raise InvalidIngredientsError("bahan kosong", details={"hint": "isi bahan"})

    @app.get("/boom/not-found")
    def not_found() -> None:
        raise RecipeNotFoundError("recipe_999")

    @app.get("/boom/base")
    def base_error() -> None:
        raise AppError("kesalahan umum")

    return app


class TestAppErrorHandler:
    def test_maps_status_and_code(self, failing_app: FastAPI) -> None:
        client = TestClient(failing_app, raise_server_exceptions=False)
        response = client.get("/boom/app-error")
        assert response.status_code == 400
        assert response.json()["error"]["code"] == "INVALID_INGREDIENTS"
        assert response.json()["error"]["details"] == {"hint": "isi bahan"}

    def test_not_found_maps_to_404(self, failing_app: FastAPI) -> None:
        client = TestClient(failing_app, raise_server_exceptions=False)
        response = client.get("/boom/not-found")
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "RECIPE_NOT_FOUND"

    def test_base_app_error_maps_to_500(self, failing_app: FastAPI) -> None:
        client = TestClient(failing_app, raise_server_exceptions=False)
        response = client.get("/boom/base")
        assert response.status_code == 500
        assert response.json()["error"]["code"] == "INTERNAL_ERROR"


class TestUnexpectedErrorHandler:
    def test_returns_generic_500(self, failing_app: FastAPI) -> None:
        client = TestClient(failing_app, raise_server_exceptions=False)
        response = client.get("/boom/unexpected")
        assert response.status_code == 500
        assert response.json()["error"]["code"] == "INTERNAL_ERROR"

    def test_does_not_leak_exception_message(self, failing_app: FastAPI) -> None:
        """Detail internal (mis. kredensial) tidak boleh muncul di response."""
        client = TestClient(failing_app, raise_server_exceptions=False)
        response = client.get("/boom/unexpected")
        assert "db password" not in response.text
        assert "abc123" not in response.text
        assert "Traceback" not in response.text

    def test_logs_stack_trace_server_side(
        self, failing_app: FastAPI, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Stack trace tetap masuk log — hilang dari response, bukan hilang total."""
        client = TestClient(failing_app, raise_server_exceptions=False)
        with caplog.at_level("ERROR", logger="app"):
            client.get("/boom/unexpected")
        assert "unhandled_exception" in caplog.text
        assert "RuntimeError" in caplog.text


class TestValidationErrorHandler:
    def test_pydantic_error_becomes_422_with_details(self) -> None:
        client = TestClient(create_app())
        response = client.post(
            "/api/v1/recommendations", json={"ingredients": ["telur"], "limit": 99}
        )
        assert response.status_code == 422
        body = response.json()["error"]
        assert body["code"] == "VALIDATION_ERROR"
        assert isinstance(body["details"], list)
        assert body["details"][0]["field"] == "limit"

    def test_missing_body_is_422(self) -> None:
        client = TestClient(create_app())
        response = client.post("/api/v1/recommendations")
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"


class TestErrorEnvelopeConsistency:
    @pytest.mark.parametrize(
        "path, expected_status",
        [
            ("/boom/app-error", 400),
            ("/boom/not-found", 404),
            ("/boom/base", 500),
            ("/boom/unexpected", 500),
        ],
    )
    def test_all_errors_use_same_envelope(
        self, failing_app: FastAPI, path: str, expected_status: int
    ) -> None:
        client = TestClient(failing_app, raise_server_exceptions=False)
        response = client.get(path)
        assert response.status_code == expected_status
        body = response.json()
        assert set(body) == {"error"}
        assert set(body["error"]) == {"code", "message", "details"}
