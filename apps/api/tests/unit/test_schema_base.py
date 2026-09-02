"""Test untuk `app.schemas.base`."""

from app.schemas.base import CamelModel


class Sample(CamelModel):
    cooking_time_minutes: int
    match_percentage: int
    recipe_id: str


class TestCamelModel:
    def test_serializes_to_camel_case(self) -> None:
        payload = Sample(
            cooking_time_minutes=15, match_percentage=75, recipe_id="recipe_001"
        ).model_dump(by_alias=True)
        assert payload == {
            "cookingTimeMinutes": 15,
            "matchPercentage": 75,
            "recipeId": "recipe_001",
        }

    def test_accepts_camel_case_input(self) -> None:
        model = Sample.model_validate(
            {"cookingTimeMinutes": 20, "matchPercentage": 80, "recipeId": "recipe_002"}
        )
        assert model.cooking_time_minutes == 20

    def test_accepts_snake_case_input(self) -> None:
        """populate_by_name membuat kode internal tetap bisa memakai snake_case."""
        model = Sample.model_validate(
            {"cooking_time_minutes": 20, "match_percentage": 80, "recipe_id": "recipe_002"}
        )
        assert model.cooking_time_minutes == 20

    def test_round_trip(self) -> None:
        original = Sample(cooking_time_minutes=15, match_percentage=75, recipe_id="recipe_001")
        restored = Sample.model_validate(original.model_dump(by_alias=True))
        assert restored == original

    def test_json_schema_uses_camel_case(self) -> None:
        """OpenAPI harus menampilkan nama camelCase, bukan snake_case."""
        properties = Sample.model_json_schema(by_alias=True)["properties"]
        assert "cookingTimeMinutes" in properties
        assert "cooking_time_minutes" not in properties

    def test_strips_whitespace_on_strings(self) -> None:
        model = Sample.model_validate(
            {"cookingTimeMinutes": 1, "matchPercentage": 1, "recipeId": "  recipe_001  "}
        )
        assert model.recipe_id == "recipe_001"

    def test_extra_fields_ignored(self) -> None:
        model = Sample.model_validate(
            {
                "cookingTimeMinutes": 1,
                "matchPercentage": 1,
                "recipeId": "recipe_001",
                "unexpected": "value",
            }
        )
        assert not hasattr(model, "unexpected")
