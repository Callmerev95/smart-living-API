"""Test untuk repository berbasis JSON.

Pakai dataset nyata dari `data/recipes/` agar tidak menguji against fixture kecil.
"""

import json
from pathlib import Path

import pytest

from app.domain.models.ingredient import IngredientCategory
from app.domain.models.recipe import Difficulty
from app.repositories.errors import DatasetLoadError
from app.repositories.json_ingredient_repository import JsonIngredientRepository
from app.repositories.json_recipe_repository import JsonRecipeRepository

# --- lokasi dataset nyata ------------------------------------------------ #

INGREDIENTS_PATH = Path(__file__).resolve().parents[4] / "data" / "recipes" / "ingredients.json"
RECIPES_PATH = Path(__file__).resolve().parents[4] / "data" / "recipes" / "recipes.json"


def _temp_recipe_repo(path: Path | None = None) -> tuple[Path, JsonRecipeRepository]:
    target = path or RECIPES_PATH
    return target, JsonRecipeRepository(target)


def _temp_ingredient_repo(path: Path | None = None) -> tuple[Path, JsonIngredientRepository]:
    target = path or INGREDIENTS_PATH
    return target, JsonIngredientRepository(target)


# --------------------------------------------------------------------------- #
# JsonRecipeRepository
# --------------------------------------------------------------------------- #


class TestJsonRecipeRepository:
    def test_loads_sixty_recipes(self) -> None:
        _, repo = _temp_recipe_repo()
        assert repo.count() == 60
        assert len(repo.get_all()) == 60

    def test_get_by_id_hit(self) -> None:
        _, repo = _temp_recipe_repo()
        recipe = repo.get_by_id("recipe_001")
        assert recipe is not None
        assert recipe.name == "Omelet Ayam Wortel"

    def test_get_by_id_miss_returns_none(self) -> None:
        _, repo = _temp_recipe_repo()
        assert repo.get_by_id("recipe_999") is None
        assert repo.get_by_id("recipe_000") is None

    def test_order_is_stable_and_matches_file(self) -> None:
        _, repo = _temp_recipe_repo()
        assert repo.get_all()[0].id == "recipe_001"
        assert repo.get_all()[1].id == "recipe_002"
        assert repo.get_all()[-1].id == "recipe_060"

    def test_get_all_order_is_consistent_across_calls(self) -> None:
        _, repo = _temp_recipe_repo()
        assert repo.get_all() == repo.get_all()

    def test_field_mapping_camelCase_to_snake(self) -> None:
        """`cookingTimeMinutes` di JSON -> `cooking_time_minutes` di domain."""
        _, repo = _temp_recipe_repo()
        recipe = repo.get_by_id("recipe_001")
        assert recipe is not None
        assert recipe.cooking_time_minutes == 15
        assert recipe.difficulty is Difficulty.EASY
        assert isinstance(recipe.ingredients, tuple)
        assert isinstance(recipe.steps, tuple)
        assert isinstance(recipe.tags, tuple)
        assert recipe.source == "original"

    def test_file_not_found_raises(self, tmp_path: Path) -> None:
        with pytest.raises(DatasetLoadError, match="tidak ditemukan"):
            JsonRecipeRepository(tmp_path / "nope.json")

    def test_malformed_json_raises(self, tmp_path: Path) -> None:
        malformed = tmp_path / "recipes.json"
        malformed.write_text("{bad", encoding="utf-8")
        with pytest.raises(DatasetLoadError, match="tidak valid"):
            JsonRecipeRepository(malformed)

    def test_root_not_array_raises(self, tmp_path: Path) -> None:
        not_array = tmp_path / "recipes.json"
        not_array.write_text('{"id": "recipe_001"}', encoding="utf-8")
        with pytest.raises(DatasetLoadError, match="array"):
            JsonRecipeRepository(not_array)

    def test_repository_does_not_rank(self) -> None:
        """Repository tidak menentukan ranking (Rule 5). Cek tidak ada method ranking-like."""
        assert not any(
            name.startswith("rank") or name.startswith("score")
            for name in dir(JsonRecipeRepository)
        )


# --------------------------------------------------------------------------- #
# JsonIngredientRepository
# --------------------------------------------------------------------------- #


class TestJsonIngredientRepository:
    def test_loads_ninety_four_ingredients(self) -> None:
        _, repo = _temp_ingredient_repo()
        assert repo.count() == 94
        assert len(repo.get_all()) == 94

    def test_get_by_name_hit(self) -> None:
        _, repo = _temp_ingredient_repo()
        ingredient = repo.get_by_name("egg")
        assert ingredient is not None
        assert ingredient.display_name == "Telur"
        assert ingredient.category is IngredientCategory.PROTEIN
        assert ingredient.staple is False

    def test_get_by_name_miss_returns_none(self) -> None:
        _, repo = _temp_ingredient_repo()
        assert repo.get_by_name("nonexistent") is None
        assert repo.get_by_name("telur") is None

    def test_alias_is_not_resolved_by_get_by_name(self) -> None:
        """Alias hanya lewat alias map, bukan `get_by_name` — boundary yang tegas."""
        _, repo = _temp_ingredient_repo()
        assert repo.get_by_name("telur") is None
        assert repo.get_alias_map()["telur"] == "egg"

    def test_alias_map_contains_canonical(self) -> None:
        _, repo = _temp_ingredient_repo()
        alias_map = repo.get_alias_map()
        assert alias_map["egg"] == "egg"
        assert alias_map["chicken"] == "chicken"

    def test_alias_map_alias_resolves(self) -> None:
        _, repo = _temp_ingredient_repo()
        alias_map = repo.get_alias_map()
        assert alias_map["telur"] == "egg"
        assert alias_map["ayam"] == "chicken"
        assert alias_map["kecap manis"] == "soy_sauce"
        assert alias_map["bawang putih"] == "garlic"

    def test_alias_map_is_copy_not_reference(self) -> None:
        _, repo = _temp_ingredient_repo()
        first = repo.get_alias_map()
        first["evil"] = "injected"
        assert "evil" not in repo.get_alias_map()

    def test_staple_names_as_frozenset(self) -> None:
        _, repo = _temp_ingredient_repo()
        staples = repo.get_staple_names()
        assert isinstance(staples, frozenset)
        assert staples == {"salt", "cooking_oil", "water", "pepper", "sugar"}

    def test_order_is_stable(self) -> None:
        _, repo = _temp_ingredient_repo()
        assert repo.get_all() == repo.get_all()
        assert repo.get_all()[0].name == "salt"

    def test_file_not_found_raises(self, tmp_path: Path) -> None:
        with pytest.raises(DatasetLoadError, match="tidak ditemukan"):
            JsonIngredientRepository(tmp_path / "nope.json")

    def test_malformed_json_raises(self, tmp_path: Path) -> None:
        malformed = tmp_path / "ingredients.json"
        malformed.write_text("{bad", encoding="utf-8")
        with pytest.raises(DatasetLoadError, match="tidak valid"):
            JsonIngredientRepository(malformed)

    def test_duplicate_alias_raises(self, tmp_path: Path) -> None:
        """Alias yang sama di dua ingredient berbeda -> fail fast."""
        data = [
            {
                "name": "egg",
                "displayName": "Telur",
                "aliases": ["telur"],
                "category": "protein",
                "staple": False,
            },
            {
                "name": "duck_egg",
                "displayName": "Telur Bebek",
                "aliases": ["telur"],
                "category": "protein",
                "staple": False,
            },
        ]
        dup = tmp_path / "ingredients.json"
        dup.write_text(json.dumps(data), encoding="utf-8")
        with pytest.raises(DatasetLoadError, match="bertubrukan"):
            JsonIngredientRepository(dup)

    def test_repository_does_not_rank(self) -> None:
        assert not any(
            name.startswith("rank") or name.startswith("score")
            for name in dir(JsonIngredientRepository)
        )


# --------------------------------------------------------------------------- #
# Jalur error parsing — dataset rusak harus gagal saat init, bukan silent
# --------------------------------------------------------------------------- #


def _write(tmp_path: Path, filename: str, payload: object) -> Path:
    target = tmp_path / filename
    target.write_text(json.dumps(payload), encoding="utf-8")
    return target


class TestRecipeParsingErrors:
    def test_entry_not_object(self, tmp_path: Path) -> None:
        path = _write(tmp_path, "recipes.json", ["recipe_001"])
        with pytest.raises(DatasetLoadError, match="harus berupa object"):
            JsonRecipeRepository(path)

    def test_missing_difficulty_field(self, tmp_path: Path) -> None:
        path = _write(tmp_path, "recipes.json", [{"id": "recipe_001"}])
        with pytest.raises(DatasetLoadError, match="`difficulty` tidak ada"):
            JsonRecipeRepository(path)

    def test_invalid_difficulty_value(self, tmp_path: Path) -> None:
        path = _write(tmp_path, "recipes.json", [{"id": "recipe_001", "difficulty": "sedang"}])
        with pytest.raises(DatasetLoadError, match="difficulty tidak valid"):
            JsonRecipeRepository(path)

    def test_missing_required_field(self, tmp_path: Path) -> None:
        """`difficulty` valid tapi field lain hilang -> error menyebut lokasi."""
        path = _write(tmp_path, "recipes.json", [{"id": "recipe_001", "difficulty": "easy"}])
        with pytest.raises(DatasetLoadError, match=r"recipes\.json\[0\].*tidak sesuai kontrak"):
            JsonRecipeRepository(path)

    def test_ingredients_wrong_shape(self, tmp_path: Path) -> None:
        path = _write(
            tmp_path,
            "recipes.json",
            [
                {
                    "id": "recipe_001",
                    "name": "Uji",
                    "description": "Uji",
                    "ingredients": ["egg"],
                    "cookingTimeMinutes": 10,
                    "difficulty": "easy",
                    "servings": 1,
                    "steps": ["a", "b", "c"],
                    "tags": ["praktis"],
                    "source": "original",
                }
            ],
        )
        with pytest.raises(DatasetLoadError, match="tidak sesuai kontrak"):
            JsonRecipeRepository(path)


class TestIngredientParsingErrors:
    def test_entry_not_object(self, tmp_path: Path) -> None:
        path = _write(tmp_path, "ingredients.json", ["egg"])
        with pytest.raises(DatasetLoadError, match="harus berupa object"):
            JsonIngredientRepository(path)

    def test_missing_category_field(self, tmp_path: Path) -> None:
        path = _write(tmp_path, "ingredients.json", [{"name": "egg"}])
        with pytest.raises(DatasetLoadError, match="`category` tidak ada"):
            JsonIngredientRepository(path)

    def test_invalid_category_value(self, tmp_path: Path) -> None:
        path = _write(tmp_path, "ingredients.json", [{"name": "egg", "category": "protien"}])
        with pytest.raises(DatasetLoadError, match="category tidak valid"):
            JsonIngredientRepository(path)

    def test_missing_required_field(self, tmp_path: Path) -> None:
        path = _write(tmp_path, "ingredients.json", [{"name": "egg", "category": "protein"}])
        with pytest.raises(DatasetLoadError, match=r"ingredients\.json\[0\].*tidak sesuai kontrak"):
            JsonIngredientRepository(path)

    def test_root_not_array_raises(self, tmp_path: Path) -> None:
        path = _write(tmp_path, "ingredients.json", {"name": "egg"})
        with pytest.raises(DatasetLoadError, match="array"):
            JsonIngredientRepository(path)

    def test_duplicate_canonical_name_tolerated_in_alias_map(self, tmp_path: Path) -> None:
        """Nama kanonik ganda ditolak validator dataset; repository tidak boleh crash."""
        data = [
            {
                "name": "egg",
                "displayName": "Telur",
                "aliases": ["telur"],
                "category": "protein",
                "staple": False,
            },
            {
                "name": "egg",
                "displayName": "Telur Lain",
                "aliases": ["telur"],
                "category": "protein",
                "staple": False,
            },
        ]
        path = _write(tmp_path, "ingredients.json", data)
        repo = JsonIngredientRepository(path)
        assert repo.get_alias_map()["telur"] == "egg"


# --------------------------------------------------------------------------- #
# `get_staple_names` di JsonRecipeRepository tidak ada — bukan tempatnya
# --------------------------------------------------------------------------- #


def test_recipe_repo_has_no_staple_concept() -> None:
    """Staple diketahui ingredient repo, bukan recipe repo (separation of concerns)."""
    assert not hasattr(JsonRecipeRepository, "get_staple_names")
    assert not hasattr(JsonRecipeRepository, "get_alias_map")


# --------------------------------------------------------------------------- #
# Null/empty path sanity — misuse yang sering salah didiamkan
# --------------------------------------------------------------------------- #


def test_ingredient_repository_count_matches_len_get_all() -> None:
    _, repo = _temp_ingredient_repo()
    assert repo.count() == len(repo.get_all())


def test_recipe_repository_count_matches_len_get_all() -> None:
    _, repo = _temp_recipe_repo()
    assert repo.count() == len(repo.get_all())
