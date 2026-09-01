"""Integration test untuk health endpoint."""

from fastapi.testclient import TestClient

from app.main import create_app

client = TestClient(create_app())


def test_health_returns_ok() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_is_registered_under_v1_prefix() -> None:
    """Endpoint tanpa prefix /api/v1 tidak boleh ada."""
    assert client.get("/health").status_code == 404
