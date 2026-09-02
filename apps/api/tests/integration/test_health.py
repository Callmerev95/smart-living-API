"""Integration test untuk health endpoint."""

from fastapi.testclient import TestClient

from app.main import create_app

client = TestClient(create_app())


def test_health_returns_ok_with_dataset_counts() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["recipeCount"] == 60
    assert payload["ingredientCount"] == 94


def test_health_is_registered_under_v1_prefix() -> None:
    """Endpoint tanpa prefix /api/v1 tidak boleh ada."""
    assert client.get("/health").status_code == 404
