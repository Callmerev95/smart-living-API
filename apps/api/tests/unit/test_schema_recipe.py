"""Test untuk schema recipe & ingredient."""

from app.schemas.ingredient import HealthResponse, IngredientItem, IngredientListResponse
from app.schemas.recipe import RecipeIngredientSchema, RecipeResponse


def recipe_response(**overrides: object) -> RecipeResponse:
    defaults: dict[str, object] = {
        "id": "recipe_001",
        "name": "Omelet Ayam Wortel",
        "description": "Omelet praktis.",
        "ingredients": [
            RecipeIngredientSchema(name="egg", required=True),
            RecipeIngredientSchema(name="shallot", required=False),
        ],
        "cooking_time_minutes": 15,
        "difficulty": "easy",
        "servings": 2,
        "steps": ["a", "b", "c"],
        "tags": ["sarapan"],
        "source": "original",
    }
    defaults.update(overrides)
    return RecipeResponse(**defaults)  # type: ignore[arg-type]


class TestRecipeResponse:
    def test_has_no_match_related_fields(self) -> None:
        """Field match hanya bermakna dalam konteks query (§A.10.2)."""
        fields = set(RecipeResponse.model_fields)
        assert "match_percentage" not in fields
        assert "available_ingredients" not in fields
        assert "missing_ingredients" not in fields

    def test_ingredients_carry_required_flag(self) -> None:
        response = recipe_response()
        assert response.ingredients[0].required is True
        assert response.ingredients[1].required is False

    def test_camel_case_serialization(self) -> None:
        payload = recipe_response().model_dump(by_alias=True)
        assert "cookingTimeMinutes" in payload
        assert "cooking_time_minutes" not in payload

    def test_full_field_set(self) -> None:
        payload = recipe_response().model_dump(by_alias=True)
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


class TestIngredientSchemas:
    def test_ingredient_item_fields(self) -> None:
        payload = IngredientItem(
            name="egg",
            display_name="Telur",
            aliases=["telur", "eggs"],
            category="protein",
            staple=False,
        ).model_dump(by_alias=True)
        assert set(payload) == {"name", "displayName", "aliases", "category", "staple"}

    def test_list_response_meta_count(self) -> None:
        response = IngredientListResponse.model_validate(
            {
                "ingredients": [
                    {
                        "name": "egg",
                        "displayName": "Telur",
                        "aliases": ["telur"],
                        "category": "protein",
                        "staple": False,
                    }
                ],
                "meta": {"count": 1},
            }
        )
        assert response.meta.count == len(response.ingredients)

    def test_staple_flag_serialized(self) -> None:
        payload = IngredientItem(
            name="salt", display_name="Garam", aliases=["garam"], category="staple", staple=True
        ).model_dump(by_alias=True)
        assert payload["staple"] is True


class TestHealthResponse:
    def test_includes_dataset_counts(self) -> None:
        """Health harus membuktikan dataset ter-load (§A.10.4)."""
        payload = HealthResponse(status="ok", recipe_count=60, ingredient_count=94).model_dump(
            by_alias=True
        )
        assert payload == {"status": "ok", "recipeCount": 60, "ingredientCount": 94}
