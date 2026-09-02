"""Integration test untuk endpoint recipes (`docs/content-schema.md` §A.10.2)."""

from fastapi.testclient import TestClient

from app.main import create_app

client = TestClient(create_app())


class TestGetRecipe:
    def test_existing_recipe_returns_200(self) -> None:
        response = client.get("/api/v1/recipes/recipe_001")
        assert response.status_code == 200
        assert response.json()["id"] == "recipe_001"
        assert response.json()["name"] == "Omelet Ayam Wortel"

    def test_response_shape(self) -> None:
        payload = client.get("/api/v1/recipes/recipe_001").json()
        assert set(payload) == {
            "id",
            "name",
            "description",
            "ingredients",
            "cookingTimeMinutes",
            "difficulty",
            "servings",
            "steps",
            "tags",
            "source",
        }

    def test_no_match_related_fields(self) -> None:
        """Detail resep tidak punya konteks query, jadi tanpa field kecocokan."""
        payload = client.get("/api/v1/recipes/recipe_001").json()
        assert "matchPercentage" not in payload
        assert "availableIngredients" not in payload
        assert "missingIngredients" not in payload

    def test_ingredients_carry_required_flag(self) -> None:
        payload = client.get("/api/v1/recipes/recipe_001").json()
        assert all({"name", "required"} == set(item) for item in payload["ingredients"])
        assert any(item["required"] is False for item in payload["ingredients"])

    def test_last_recipe_accessible(self) -> None:
        assert client.get("/api/v1/recipes/recipe_060").status_code == 200

    def test_unknown_id_returns_404(self) -> None:
        response = client.get("/api/v1/recipes/recipe_999")
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "RECIPE_NOT_FOUND"

    def test_malformed_id_returns_404(self) -> None:
        response = client.get("/api/v1/recipes/not-an-id")
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "RECIPE_NOT_FOUND"

    def test_404_error_envelope(self) -> None:
        body = client.get("/api/v1/recipes/recipe_999").json()
        assert set(body) == {"error"}
        assert set(body["error"]) == {"code", "message", "details"}
