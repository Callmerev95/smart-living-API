"""Test untuk domain model (`app.domain.models`).

Fokus: immutability, kelengkapan enum, dan determinisme urutan helper.
"""

import dataclasses

import pytest

from app.domain.models.ingredient import Ingredient, IngredientCategory
from app.domain.models.match_result import MatchResult
from app.domain.models.recipe import Difficulty, Recipe, RecipeIngredient


def make_ingredient(**overrides: object) -> Ingredient:
    defaults: dict[str, object] = {
        "name": "egg",
        "display_name": "Telur",
        "aliases": ("eggs", "telur", "telor"),
        "category": IngredientCategory.PROTEIN,
        "staple": False,
    }
    defaults.update(overrides)
    return Ingredient(**defaults)  # type: ignore[arg-type]


def make_recipe(**overrides: object) -> Recipe:
    defaults: dict[str, object] = {
        "id": "recipe_001",
        "name": "Omelet Ayam Wortel",
        "description": "Omelet praktis dengan ayam dan wortel.",
        "ingredients": (
            RecipeIngredient(name="egg", required=True),
            RecipeIngredient(name="chicken", required=True),
            RecipeIngredient(name="carrot", required=True),
            RecipeIngredient(name="shallot", required=False),
            RecipeIngredient(name="salt", required=True),
            RecipeIngredient(name="cooking_oil", required=True),
        ),
        "cooking_time_minutes": 15,
        "difficulty": Difficulty.EASY,
        "servings": 2,
        "steps": ("Kocok telur.", "Tumis ayam dan wortel.", "Tuang telur, sajikan."),
        "tags": ("sarapan", "praktis"),
        "source": "original",
    }
    defaults.update(overrides)
    return Recipe(**defaults)  # type: ignore[arg-type]


class TestIngredientCategory:
    def test_has_exactly_nine_categories(self) -> None:
        """docs/content-schema.md §A.2.3 mendefinisikan 9 kategori."""
        assert len(IngredientCategory) == 9

    def test_category_values(self) -> None:
        assert {c.value for c in IngredientCategory} == {
            "protein",
            "vegetable",
            "fruit",
            "grain",
            "dairy",
            "spice",
            "condiment",
            "staple",
            "other",
        }

    def test_is_str_enum(self) -> None:
        """StrEnum agar serialisasi ke JSON menghasilkan string apa adanya."""
        assert IngredientCategory.PROTEIN == "protein"


class TestIngredient:
    def test_instantiation(self) -> None:
        ingredient = make_ingredient()
        assert ingredient.name == "egg"
        assert ingredient.display_name == "Telur"
        assert ingredient.category is IngredientCategory.PROTEIN
        assert ingredient.staple is False

    def test_is_frozen(self) -> None:
        ingredient = make_ingredient()
        with pytest.raises(dataclasses.FrozenInstanceError):
            ingredient.name = "chicken"  # type: ignore[misc]

    def test_aliases_preserve_order(self) -> None:
        ingredient = make_ingredient(aliases=("telur", "eggs", "telor"))
        assert ingredient.aliases == ("telur", "eggs", "telor")

    def test_aliases_may_be_empty(self) -> None:
        assert make_ingredient(aliases=()).aliases == ()

    def test_staple_flag_independent_from_category(self) -> None:
        """Flag `staple` dipakai scoring; `category` hanya untuk presentasi."""
        ingredient = make_ingredient(
            name="cooking_oil",
            category=IngredientCategory.STAPLE,
            staple=True,
        )
        assert ingredient.staple is True
        assert ingredient.category is IngredientCategory.STAPLE


class TestDifficulty:
    def test_has_three_levels(self) -> None:
        assert {d.value for d in Difficulty} == {"easy", "medium", "hard"}

    def test_is_str_enum(self) -> None:
        assert Difficulty.EASY == "easy"


class TestRecipeIngredient:
    def test_instantiation(self) -> None:
        item = RecipeIngredient(name="egg", required=True)
        assert item.name == "egg"
        assert item.required is True

    def test_is_frozen(self) -> None:
        item = RecipeIngredient(name="egg", required=True)
        with pytest.raises(dataclasses.FrozenInstanceError):
            item.required = False  # type: ignore[misc]

    def test_has_no_quantity_field(self) -> None:
        """Kuantitas out of scope MVP (docs/content-schema.md §A.3.3)."""
        field_names = {f.name for f in dataclasses.fields(RecipeIngredient)}
        assert "quantity" not in field_names
        assert "unit" not in field_names


class TestRecipe:
    def test_instantiation(self) -> None:
        recipe = make_recipe()
        assert recipe.id == "recipe_001"
        assert recipe.difficulty is Difficulty.EASY
        assert recipe.servings == 2
        assert recipe.source == "original"

    def test_is_frozen(self) -> None:
        recipe = make_recipe()
        with pytest.raises(dataclasses.FrozenInstanceError):
            recipe.name = "Nasi Goreng"  # type: ignore[misc]

    def test_required_ingredient_names_excludes_optional(self) -> None:
        recipe = make_recipe()
        assert "shallot" not in recipe.required_ingredient_names()

    def test_required_ingredient_names_preserves_order(self) -> None:
        """Urutan menentukan determinisme available/missing di response."""
        recipe = make_recipe()
        assert recipe.required_ingredient_names() == (
            "egg",
            "chicken",
            "carrot",
            "salt",
            "cooking_oil",
        )

    def test_required_ingredient_names_keeps_staple(self) -> None:
        """Model tidak memfilter staple — itu tanggung jawab scoring."""
        recipe = make_recipe()
        required = recipe.required_ingredient_names()
        assert "salt" in required
        assert "cooking_oil" in required

    def test_all_ingredient_names_includes_everything(self) -> None:
        recipe = make_recipe()
        assert recipe.all_ingredient_names() == (
            "egg",
            "chicken",
            "carrot",
            "shallot",
            "salt",
            "cooking_oil",
        )

    def test_helpers_return_tuple(self) -> None:
        recipe = make_recipe()
        assert isinstance(recipe.required_ingredient_names(), tuple)
        assert isinstance(recipe.all_ingredient_names(), tuple)

    def test_recipe_without_required_ingredients(self) -> None:
        """Guard: resep tanpa required tidak boleh membuat helper meledak."""
        recipe = make_recipe(ingredients=(RecipeIngredient(name="egg", required=False),))
        assert recipe.required_ingredient_names() == ()
        assert recipe.all_ingredient_names() == ("egg",)


class TestMatchResult:
    @staticmethod
    def make(**overrides: object) -> MatchResult:
        defaults: dict[str, object] = {
            "recipe_id": "recipe_001",
            "match_percentage": 75,
            "available_ingredients": ("egg", "chicken", "carrot"),
            "missing_ingredients": ("onion",),
            "cooking_time_minutes": 15,
        }
        defaults.update(overrides)
        return MatchResult(**defaults)  # type: ignore[arg-type]

    def test_instantiation(self) -> None:
        result = self.make()
        assert result.recipe_id == "recipe_001"
        assert result.match_percentage == 75
        assert result.cooking_time_minutes == 15

    def test_is_frozen(self) -> None:
        result = self.make()
        with pytest.raises(dataclasses.FrozenInstanceError):
            result.match_percentage = 100  # type: ignore[misc]

    def test_missing_count_derived_from_missing_ingredients(self) -> None:
        """Property turunan — tidak mungkin tidak sinkron dengan array-nya."""
        assert self.make(missing_ingredients=()).missing_count == 0
        assert self.make(missing_ingredients=("onion",)).missing_count == 1
        assert self.make(missing_ingredients=("onion", "garlic")).missing_count == 2

    def test_missing_count_is_not_a_field(self) -> None:
        field_names = {f.name for f in dataclasses.fields(MatchResult)}
        assert "missing_count" not in field_names

    def test_uses_tuple_for_determinism(self) -> None:
        result = self.make()
        assert isinstance(result.available_ingredients, tuple)
        assert isinstance(result.missing_ingredients, tuple)

    def test_has_no_scoring_method(self) -> None:
        """Perhitungan skor milik `domain/matching/scoring.py`, bukan model."""
        assert not any(
            name.startswith("calculate") or name.startswith("score") for name in dir(MatchResult)
        )
