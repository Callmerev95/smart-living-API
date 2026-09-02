"""Integration test untuk logging & request correlation.

Field wajib `docs/technical-architecture.md` §18: `request_id`, `method`, `path`,
`status_code`, `duration_ms`. Plus larangan log isi bahan user / secret.
"""

import logging

import pytest
from fastapi.testclient import TestClient

from app.main import create_app

client = TestClient(create_app())


class TestRequestId:
    def test_every_response_has_request_id(self) -> None:
        response = client.post("/api/v1/recommendations", json={"ingredients": ["telur"]})
        assert response.status_code == 200
        assert response.headers.get("x-request-id")

    def test_request_id_is_unique_per_request(self) -> None:
        first = client.get("/api/v1/health").headers.get("x-request-id")
        second = client.get("/api/v1/health").headers.get("x-request-id")
        assert first and second
        assert first != second

    def test_request_id_present_on_errors_too(self) -> None:
        response = client.post("/api/v1/recommendations", json={"ingredients": []})
        assert response.status_code == 400
        assert response.headers.get("x-request-id")


class TestLogContent:
    def test_request_completed_log_has_required_fields(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        with caplog.at_level(logging.INFO, logger="app.request"):
            client.get("/api/v1/health")

        record = next(r for r in caplog.records if getattr(r, "message", "") == "request_completed")
        assert record.request_id  # type: ignore[attr-defined]
        assert record.method == "GET"  # type: ignore[attr-defined]
        assert record.path == "/api/v1/health"  # type: ignore[attr-defined]
        assert record.status_code == 200  # type: ignore[attr-defined]
        assert record.duration_ms >= 0  # type: ignore[attr-defined]

    def test_recommendation_log_counts_but_not_contents(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Isi bahan user TIDAK boleh masuk log — hanya jumlah."""
        with caplog.at_level(logging.INFO, logger="app.request"):
            client.post(
                "/api/v1/recommendations",
                json={"ingredients": ["telur", "ayam", "kangkung"]},
            )

        record = next(
            r for r in caplog.records if getattr(r, "message", "") == "recommendation_served"
        )
        assert record.ingredient_count == 2  # type: ignore[attr-defined]
        assert record.result_count >= 1  # type: ignore[attr-defined]
        assert record.unknown_count == 1  # type: ignore[attr-defined]

        # Bahan mentah maupun canonical tidak boleh tercetak.
        for banned in ("telur", "ayam", "kangkung", "egg", "chicken"):
            assert banned not in caplog.text

    def test_no_secret_in_logs(self, caplog: pytest.LogCaptureFixture) -> None:
        with caplog.at_level(logging.INFO, logger="app.request"):
            client.get("/api/v1/health")
        for banned in ("password", "token", "api_key", "authorization", "secret"):
            assert banned.lower() not in caplog.text.lower()

    def test_error_response_is_logged_with_status(self, caplog: pytest.LogCaptureFixture) -> None:
        with caplog.at_level(logging.INFO, logger="app.request"):
            client.post("/api/v1/recommendations", json={"ingredients": []})
        record = next(r for r in caplog.records if getattr(r, "message", "") == "request_completed")
        assert record.status_code == 400  # type: ignore[attr-defined]
