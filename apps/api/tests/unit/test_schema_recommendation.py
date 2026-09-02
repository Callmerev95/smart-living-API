"""Test untuk schema recommendation (request validation + response contract)."""

import pytest
from pydantic import ValidationError

from app.core.config import get_settings
from app.core.errors import InvalidIngredientsError
from app.schemas.recommendation import (
    MetaSchema,
    QuerySchema,
    RecommendationItem,
    RecommendationRequest,
    RecommendationResponse,
)

SETTINGS = get_settings()


def item(**overrides: object) -> RecommendationItem:
    defaults: dict[str, object] = {
        "id": "recipe_001",
        "name": "Omelet Ayam Wortel",
        "description": "Omelet praktis.",
        "match_percentage": 100,
        "available_ingredients": ["egg", "chicken", "carrot"],
        "missing_ingredients": [],
        "cooking_time_minutes": 15,
        "difficulty": "easy",
        "servings": 2,
        "ingredients": ["egg", "chicken", "carrot", "salt"],
        "steps": ["a", "b", "c"],
        "tags": ["sarapan"],
    }
    defaults.update(overrides)
    return RecommendationItem(**defaults)  # type: ignore[arg-type]


# --------------------------------------------------------------------------- #
# Request validation — docs/content-schema.md §A.10.1
# --------------------------------------------------------------------------- #


class TestRequestValidation:
    def test_valid_request(self) -> None:
        request = RecommendationRequest(ingredients=["telur", "ayam"], limit=5)
        assert request.ingredients == ["telur", "ayam"]
        assert request.limit == 5

    def test_limit_optional(self) -> None:
        assert RecommendationRequest(ingredients=["telur"]).limit is None

    def test_missing_ingredients_field_is_validation_error(self) -> None:
        with pytest.raises(ValidationError):
            RecommendationRequest()  # type: ignore[call-arg]

    def test_empty_list_rejected(self) -> None:
        with pytest.raises(InvalidIngredientsError, match="setidaknya satu item"):
            RecommendationRequest(ingredients=[])

    def test_only_whitespace_items_rejected(self) -> None:
        with pytest.raises(InvalidIngredientsError):
            RecommendationRequest(ingredients=["  ", ""])

    def test_blank_items_are_dropped(self) -> None:
        request = RecommendationRequest(ingredients=["telur", "", "  ", "ayam"])
        assert request.ingredients == ["telur", "ayam"]

    def test_too_many_items_rejected(self) -> None:
        too_many = [f"bahan{i}" for i in range(SETTINGS.max_ingredients_per_request + 1)]
        with pytest.raises(InvalidIngredientsError, match="Maksimal"):
            RecommendationRequest(ingredients=too_many)

    def test_max_items_accepted(self) -> None:
        exactly_max = [f"bahan{i}" for i in range(SETTINGS.max_ingredients_per_request)]
        assert len(RecommendationRequest(ingredients=exactly_max).ingredients) == len(exactly_max)

    def test_item_too_long_rejected(self) -> None:
        long_name = "x" * (SETTINGS.max_ingredient_name_length + 1)
        with pytest.raises(InvalidIngredientsError, match="karakter"):
            RecommendationRequest(ingredients=[long_name])

    def test_item_at_max_length_accepted(self) -> None:
        name = "x" * SETTINGS.max_ingredient_name_length
        assert RecommendationRequest(ingredients=[name]).ingredients == [name]

    @pytest.mark.parametrize("bad_limit", [0, -1, 11, 100])
    def test_limit_out_of_range_rejected(self, bad_limit: int) -> None:
        with pytest.raises(ValidationError):
            RecommendationRequest(ingredients=["telur"], limit=bad_limit)

    def test_limit_boundaries_accepted(self) -> None:
        assert RecommendationRequest(ingredients=["telur"], limit=1).limit == 1
        assert (
            RecommendationRequest(ingredients=["telur"], limit=SETTINGS.max_limit).limit
            == SETTINGS.max_limit
        )

    def test_limit_wrong_type_rejected(self) -> None:
        with pytest.raises(ValidationError):
            RecommendationRequest(ingredients=["telur"], limit="abc")  # type: ignore[arg-type]

    def test_accepts_camel_case_payload(self) -> None:
        request = RecommendationRequest.model_validate({"ingredients": ["telur"], "limit": 3})
        assert request.limit == 3


# --------------------------------------------------------------------------- #
# Response contract — termasuk Delta v1.1
# --------------------------------------------------------------------------- #


class TestResponseContract:
    def test_full_structure_matches_docs(self) -> None:
        """Struktur harus cocok contoh `docs/content-schema.md` §A.10.1."""
        response = RecommendationResponse(
            query=QuerySchema(raw=["telur", "ayam"], ingredients=["egg", "chicken"]),
            unknown_ingredients=["kangkung"],
            results=[item()],
            meta=MetaSchema(count=1, limit=5, threshold=30),
        )
        payload = response.model_dump(by_alias=True)

        assert set(payload) == {"query", "unknownIngredients", "results", "meta"}
        assert set(payload["query"]) == {"raw", "ingredients"}
        assert set(payload["meta"]) == {"count", "limit", "threshold"}
        assert set(payload["results"][0]) == {
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

    def test_delta2_unknown_ingredients_at_root(self) -> None:
        response = RecommendationResponse(
            query=QuerySchema(raw=[], ingredients=[]),
            results=[],
            meta=MetaSchema(count=0, limit=5, threshold=30),
        )
        assert response.model_dump(by_alias=True)["unknownIngredients"] == []

    def test_delta3_query_has_raw_and_canonical(self) -> None:
        query = QuerySchema(raw=["telur"], ingredients=["egg"])
        payload = query.model_dump(by_alias=True)
        assert payload["raw"] == ["telur"]
        assert payload["ingredients"] == ["egg"]

    def test_ingredients_field_is_full_list(self) -> None:
        """Field `ingredients` berbeda dari `availableIngredients` (§A.5.4)."""
        recommendation = item(
            available_ingredients=["egg"],
            ingredients=["egg", "chicken", "salt", "cooking_oil"],
        )
        assert len(recommendation.ingredients) > len(recommendation.available_ingredients)

    def test_match_percentage_bounds_enforced(self) -> None:
        with pytest.raises(ValidationError):
            item(match_percentage=101)
        with pytest.raises(ValidationError):
            item(match_percentage=-1)

    def test_camel_case_serialization(self) -> None:
        payload = item().model_dump(by_alias=True)
        assert "matchPercentage" in payload
        assert "match_percentage" not in payload
        assert "cookingTimeMinutes" in payload
        assert "availableIngredients" in payload
        assert "missingIngredients" in payload

    def test_json_schema_uses_camel_case(self) -> None:
        properties = RecommendationResponse.model_json_schema(by_alias=True)["properties"]
        assert "unknownIngredients" in properties
        assert "unknown_ingredients" not in properties
