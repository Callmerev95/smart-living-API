"""Integration test — validasi request recommendations.

Menutup skenario `docs/development-roadmap.md` §5.3 dan `docs/technical-architecture.md`
§20.2.
"""

from fastapi.testclient import TestClient
from httpx import Response

from app.main import create_app

client = TestClient(create_app())


def post(payload: dict) -> Response:
    return client.post("/api/v1/recommendations", json=payload)


class TestValidRequest:
    def test_valid_input_returns_results(self) -> None:
        response = post({"ingredients": ["telur", "ayam", "wortel"]})
        assert response.status_code == 200
        data = response.json()
        assert data["meta"]["count"] >= 1
        assert data["results"][0]["id"] == "recipe_001"

    def test_result_shapes_are_complete(self) -> None:
        response = post({"ingredients": ["telur", "ayam", "wortel"]})
        item = response.json()["results"][0]
        assert set(item) == {
            "id",
            "name",
            "description",
            "matchPercentage",
            "availableIngredients",
            "missingIngredients",
            "cookingTimeMinutes",
            "difficulty",
            "servings",
            "ingredients",
            "steps",
            "tags",
        }

    def test_match_percentage_is_integer_between_0_and_100(self) -> None:
        response = post({"ingredients": ["telur", "ayam", "wortel"]})
        for item in response.json()["results"]:
            assert isinstance(item["matchPercentage"], int)
            assert 0 <= item["matchPercentage"] <= 100

    def test_optional_limit_is_used(self) -> None:
        response = post({"ingredients": ["nasi", "telur", "bawang putih"], "limit": 2})
        assert response.status_code == 200
        assert response.json()["meta"]["limit"] == 2
        assert len(response.json()["results"]) <= 2


class TestValidationErrors:
    def test_empty_list_is_400(self) -> None:
        response = post({"ingredients": []})
        assert response.status_code == 400
        body = response.json()["error"]
        assert body["code"] == "INVALID_INGREDIENTS"
        assert body["message"]

    def test_whitespace_only_list_is_400(self) -> None:
        response = post({"ingredients": ["  ", ""]})
        assert response.status_code == 400

    def test_missing_ingredients_field_is_422(self) -> None:
        response = post({"limit": 5})
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"

    def test_limit_zero_is_422(self) -> None:
        response = post({"ingredients": ["telur"], "limit": 0})
        assert response.status_code == 422

    def test_limit_above_max_is_422(self) -> None:
        response = post({"ingredients": ["telur"], "limit": 11})
        assert response.status_code == 422

    def test_limit_wrong_type_is_422(self) -> None:
        response = post({"ingredients": ["telur"], "limit": "abc"})
        assert response.status_code == 422

    def test_too_many_ingredients_is_400(self) -> None:
        response = post({"ingredients": [f"b{i}" for i in range(31)]})
        assert response.status_code == 400
        assert response.json()["error"]["code"] == "INVALID_INGREDIENTS"

    def test_overlong_ingredient_name_is_400(self) -> None:
        response = post({"ingredients": ["x" * 61]})
        assert response.status_code == 400

    def test_ingredients_wrong_type_is_422(self) -> None:
        response = post({"ingredients": "telur"})
        assert response.status_code == 422


class TestEmptyAndUnknown:
    def test_no_match_returns_200_with_empty_results(self) -> None:
        """Tidak ada kecocokan bukan error — `results: []` dengan HTTP 200 (§A.6.1)."""
        # `snail` dikenali tapi skor tertingginya di bawah threshold 30%.
        response = post({"ingredients": ["keong"]})
        assert response.status_code == 200
        data = response.json()
        assert data["results"] == []
        assert data["meta"]["count"] == 0
        assert data["unknownIngredients"] == []

    def test_unknown_ingredient_returns_200(self) -> None:
        """Delta 2: bahan tak dikenal tidak membuat request gagal."""
        response = post({"ingredients": ["telur", "kangkung"]})
        assert response.status_code == 200
        assert "kangkung" in response.json()["unknownIngredients"]
        assert len(response.json()["results"]) >= 1


class TestErrorShape:
    def test_error_is_consistent_envelope(self) -> None:
        response = post({"ingredients": []})
        body = response.json()
        assert set(body) == {"error"}
        assert set(body["error"]) == {"code", "message", "details"}

    def test_validation_error_details_list_fields(self) -> None:
        response = post({"ingredients": ["telur"], "limit": "x"})
        details = response.json()["error"]["details"]
        assert isinstance(details, list)
        assert all({"field", "reason"} <= set(d) for d in details)

    def test_no_stack_trace_leaks(self) -> None:
        response = post({"ingredients": []})
        assert "</pre>" not in response.text
        assert "Traceback" not in response.text
        assert 'File "' not in response.text
