"""Test yang menjaga kualitas dokumentasi OpenAPI.

Spesifikasi yang salah atau tidak lengkap membuat `/docs` tidak bisa dipakai tanpa
membaca source code — padahal itu tujuan FR-11 (PRD §13).
"""

import logging

import pytest
from fastapi.testclient import TestClient

from app.main import create_app

client = TestClient(create_app())


@pytest.fixture(scope="module", autouse=True)
def quiet_logs():
    """Kurangi noise log saat memanggil endpoint spesifikasi."""
    logging.disable(logging.INFO)
    yield
    logging.disable(logging.NOTSET)


@pytest.fixture(scope="module")
def spec() -> dict:
    response = client.get("/openapi.json")
    assert response.status_code == 200
    return response.json()


class TestSpecMetadata:
    def test_info_is_filled(self, spec: dict) -> None:
        info = spec["info"]
        assert info["title"] == "Smart Living API"
        assert info["version"] == "0.1.0"
        assert len(info["description"]) > 50

    def test_all_endpoints_registered(self, spec: dict) -> None:
        assert set(spec["paths"]) == {
            "/api/v1/recommendations",
            "/api/v1/recipes/{recipe_id}",
            "/api/v1/ingredients",
            "/api/v1/health",
        }

    def test_tags_documented(self, spec: dict) -> None:
        names = {tag["name"] for tag in spec["tags"]}
        assert names == {"recommendations", "recipes", "ingredients", "system"}
        assert all(tag["description"] for tag in spec["tags"])

    def test_docs_page_renders(self) -> None:
        response = client.get("/docs")
        assert response.status_code == 200
        assert "swagger" in response.text.lower()


class TestOperationDocs:
    @pytest.mark.parametrize(
        "path, method",
        [
            ("/api/v1/recommendations", "post"),
            ("/api/v1/recipes/{recipe_id}", "get"),
            ("/api/v1/ingredients", "get"),
            ("/api/v1/health", "get"),
        ],
    )
    def test_every_operation_has_summary_and_description(
        self, spec: dict, path: str, method: str
    ) -> None:
        operation = spec["paths"][path][method]
        assert operation["summary"]
        assert operation["description"]
        assert operation["tags"]

    def test_recommendations_documents_error_responses(self, spec: dict) -> None:
        responses = spec["paths"]["/api/v1/recommendations"]["post"]["responses"]
        assert {"200", "400", "422", "500"} <= set(responses)

    def test_recipe_documents_404(self, spec: dict) -> None:
        responses = spec["paths"]["/api/v1/recipes/{recipe_id}"]["get"]["responses"]
        assert "404" in responses

    def test_recommendations_documents_delta_behaviour(self, spec: dict) -> None:
        """Perilaku Contract Delta v1.1 harus terbaca reviewer di `/docs`."""
        description = spec["paths"]["/api/v1/recommendations"]["post"]["description"].lower()
        assert "bahan pokok" in description
        assert "unknowningredients" in description
        assert "normalisasi" in description


class TestSchemaDocs:
    def test_schemas_use_camel_case(self, spec: dict) -> None:
        properties = spec["components"]["schemas"]["RecommendationResponse"]["properties"]
        assert "unknownIngredients" in properties
        assert "unknown_ingredients" not in properties

    def test_recommendation_item_fields_documented(self, spec: dict) -> None:
        properties = spec["components"]["schemas"]["RecommendationItem"]["properties"]
        assert "matchPercentage" in properties
        assert "availableIngredients" in properties
        assert properties["matchPercentage"]["description"]

    def test_request_schema_has_examples(self, spec: dict) -> None:
        properties = spec["components"]["schemas"]["RecommendationRequest"]["properties"]
        assert properties["ingredients"].get("examples")

    def test_error_schema_documented(self, spec: dict) -> None:
        assert "ErrorResponse" in spec["components"]["schemas"]
        error_properties = spec["components"]["schemas"]["ErrorDetail"]["properties"]
        assert {"code", "message", "details"} <= set(error_properties)
