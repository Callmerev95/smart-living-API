"""Test untuk `domain/matching/engine`.

Berisi seluruh 8 test case wajib `docs/content-schema.md` §A.5.5, termasuk case 4 & 5
yang memvalidasi Contract Delta v1.1 Delta 1 (staple exclusion) dan case 8
(guard divide-by-zero).
"""

from pathlib import Path

from app.domain.matching.engine import match_recipe, match_recipes
from app.domain.models.recipe import Difficulty, Recipe, RecipeIngredient

STAPLES = frozenset({"salt", "cooking_oil", "water", "pepper", "sugar"})

ENGINE_SOURCE = Path(__file__).resolve().parents[2] / "app" / "domain" / "matching" / "engine.py"


def recipe(
    *items: tuple[str, bool],
    recipe_id: str = "recipe_001",
    minutes: int = 15,
) -> Recipe:
    """Bangun resep dari pasangan `(nama, required)`."""
    return Recipe(
        id=recipe_id,
        name="Uji",
        description="Resep uji.",
        ingredients=tuple(
            RecipeIngredient(name=name, required=required) for name, required in items
        ),
        cooking_time_minutes=minutes,
        difficulty=Difficulty.EASY,
        servings=2,
        steps=("a", "b", "c"),
        tags=("praktis",),
        source="original",
    )


# --------------------------------------------------------------------------- #
# 8 test case wajib — docs/content-schema.md §A.5.5
# --------------------------------------------------------------------------- #


class TestSpecCases:
    def test_case1_partial_match(self) -> None:
        """3/4 -> 75%, onion masuk missing."""
        result = match_recipe(
            frozenset({"egg", "chicken", "carrot"}),
            recipe(("egg", True), ("chicken", True), ("carrot", True), ("onion", True)),
            STAPLES,
        )
        assert result.match_percentage == 75
        assert result.available_ingredients == ("egg", "chicken", "carrot")
        assert result.missing_ingredients == ("onion",)

    def test_case2_full_match(self) -> None:
        result = match_recipe(
            frozenset({"egg", "chicken", "carrot"}),
            recipe(("egg", True), ("chicken", True), ("carrot", True)),
            STAPLES,
        )
        assert result.match_percentage == 100
        assert result.available_ingredients == ("egg", "chicken", "carrot")
        assert result.missing_ingredients == ()

    def test_case3_no_match(self) -> None:
        result = match_recipe(
            frozenset({"tofu"}),
            recipe(("egg", True), ("chicken", True), ("carrot", True)),
            STAPLES,
        )
        assert result.match_percentage == 0
        assert result.available_ingredients == ()
        assert result.missing_ingredients == ("egg", "chicken", "carrot")

    def test_case4_staple_excluded_from_denominator(self) -> None:
        """Delta 1: salt + cooking_oil tidak menurunkan skor dari 100%."""
        result = match_recipe(
            frozenset({"egg", "chicken"}),
            recipe(("egg", True), ("chicken", True), ("salt", True), ("cooking_oil", True)),
            STAPLES,
        )
        assert result.match_percentage == 100
        assert result.available_ingredients == ("egg", "chicken")
        assert result.missing_ingredients == ()

    def test_case5_staple_excluded_partial(self) -> None:
        """Delta 1: 1/2 = 50%, bukan 1/3 = 33% — salt tidak dihitung."""
        result = match_recipe(
            frozenset({"egg"}),
            recipe(("egg", True), ("chicken", True), ("salt", True)),
            STAPLES,
        )
        assert result.match_percentage == 50
        assert result.available_ingredients == ("egg",)
        assert result.missing_ingredients == ("chicken",)

    def test_case6_extra_user_ingredients_do_not_lower_score(self) -> None:
        """Bahan user yang tidak dipakai resep tidak berpengaruh."""
        result = match_recipe(
            frozenset({"egg", "chicken", "carrot", "tofu", "rice"}),
            recipe(("egg", True), ("chicken", True), ("carrot", True)),
            STAPLES,
        )
        assert result.match_percentage == 100
        assert result.available_ingredients == ("egg", "chicken", "carrot")
        assert result.missing_ingredients == ()

    def test_case7_optional_ingredient_ignored(self) -> None:
        """`required: false` tidak masuk denominator maupun missing."""
        result = match_recipe(
            frozenset({"egg", "chicken", "carrot"}),
            recipe(("egg", True), ("chicken", True), ("carrot", True), ("onion", False)),
            STAPLES,
        )
        assert result.match_percentage == 100
        assert result.missing_ingredients == ()
        assert "onion" not in result.available_ingredients

    def test_case8_all_required_are_staple(self) -> None:
        """Guard divide-by-zero: denominator 0 -> 0%, tanpa exception."""
        result = match_recipe(
            frozenset({"egg"}),
            recipe(("salt", True), ("water", True)),
            STAPLES,
        )
        assert result.match_percentage == 0
        assert result.available_ingredients == ()
        assert result.missing_ingredients == ()


# --------------------------------------------------------------------------- #
# Delta 1 — staple tidak pernah dilaporkan
# --------------------------------------------------------------------------- #


class TestStapleExclusion:
    def test_staple_never_in_available_even_if_user_has_it(self) -> None:
        """User punya garam pun, garam tidak dilaporkan sebagai 'sudah ada'."""
        result = match_recipe(
            frozenset({"egg", "salt"}),
            recipe(("egg", True), ("salt", True)),
            STAPLES,
        )
        assert result.available_ingredients == ("egg",)
        assert "salt" not in result.available_ingredients

    def test_staple_never_in_missing(self) -> None:
        result = match_recipe(
            frozenset({"egg"}),
            recipe(("egg", True), ("salt", True), ("cooking_oil", True), ("pepper", True)),
            STAPLES,
        )
        assert result.missing_ingredients == ()

    def test_optional_staple_also_excluded(self) -> None:
        result = match_recipe(
            frozenset({"egg", "chicken"}),
            recipe(("egg", True), ("chicken", True), ("pepper", False)),
            STAPLES,
        )
        assert result.match_percentage == 100
        assert "pepper" not in result.available_ingredients
        assert "pepper" not in result.missing_ingredients

    def test_empty_staple_set_counts_everything(self) -> None:
        """Tanpa daftar staple, salt dihitung seperti bahan biasa."""
        result = match_recipe(
            frozenset({"egg"}),
            recipe(("egg", True), ("salt", True)),
            frozenset(),
        )
        assert result.match_percentage == 50
        assert result.missing_ingredients == ("salt",)


# --------------------------------------------------------------------------- #
# Determinisme urutan output
# --------------------------------------------------------------------------- #


class TestDeterminism:
    def test_available_order_follows_recipe_not_set(self) -> None:
        """Urutan mengikuti `recipe.ingredients`, bukan urutan iterasi set."""
        result = match_recipe(
            frozenset({"carrot", "egg", "chicken"}),
            recipe(("egg", True), ("chicken", True), ("carrot", True)),
            STAPLES,
        )
        assert result.available_ingredients == ("egg", "chicken", "carrot")

    def test_missing_order_follows_recipe(self) -> None:
        result = match_recipe(
            frozenset(),
            recipe(("carrot", True), ("egg", True), ("chicken", True)),
            STAPLES,
        )
        assert result.missing_ingredients == ("carrot", "egg", "chicken")

    def test_same_input_same_output(self) -> None:
        user = frozenset({"egg", "chicken"})
        target = recipe(("egg", True), ("chicken", True), ("carrot", True))
        assert match_recipe(user, target, STAPLES) == match_recipe(user, target, STAPLES)

    def test_user_set_iteration_order_irrelevant(self) -> None:
        target = recipe(("egg", True), ("chicken", True), ("carrot", True))
        first = match_recipe(frozenset({"egg", "chicken"}), target, STAPLES)
        second = match_recipe(frozenset({"chicken", "egg"}), target, STAPLES)
        assert first == second


# --------------------------------------------------------------------------- #
# match_recipes (batch)
# --------------------------------------------------------------------------- #


class TestMatchRecipes:
    def test_returns_result_per_recipe(self) -> None:
        recipes = [
            recipe(("egg", True), ("chicken", True), recipe_id="recipe_001"),
            recipe(("tofu", True), ("tempeh", True), recipe_id="recipe_002"),
        ]
        results = match_recipes(["egg", "chicken"], recipes, STAPLES)
        assert len(results) == 2
        assert results[0].match_percentage == 100
        assert results[1].match_percentage == 0

    def test_preserves_input_order(self) -> None:
        """Engine tidak mengurutkan — itu tugas ranking."""
        recipes = [
            recipe(("tofu", True), ("tempeh", True), recipe_id="recipe_005"),
            recipe(("egg", True), ("chicken", True), recipe_id="recipe_001"),
        ]
        results = match_recipes(["egg", "chicken"], recipes, STAPLES)
        assert [r.recipe_id for r in results] == ["recipe_005", "recipe_001"]

    def test_accepts_any_iterable(self) -> None:
        recipes = [recipe(("egg", True), ("chicken", True))]
        from_list = match_recipes(["egg", "chicken"], recipes, STAPLES)
        from_tuple = match_recipes(("egg", "chicken"), recipes, STAPLES)
        from_set = match_recipes({"egg", "chicken"}, recipes, STAPLES)
        assert from_list == from_tuple == from_set

    def test_empty_recipes(self) -> None:
        assert match_recipes(["egg"], [], STAPLES) == ()

    def test_empty_user_ingredients(self) -> None:
        results = match_recipes([], [recipe(("egg", True), ("chicken", True))], STAPLES)
        assert results[0].match_percentage == 0
        assert results[0].missing_ingredients == ("egg", "chicken")

    def test_returns_tuple(self) -> None:
        assert isinstance(match_recipes(["egg"], [recipe(("egg", True))], STAPLES), tuple)


# --------------------------------------------------------------------------- #
# Boundary — engine harus bebas framework & tidak melakukan I/O
# --------------------------------------------------------------------------- #


class TestBoundary:
    def test_no_framework_or_network_import(self) -> None:
        source = ENGINE_SOURCE.read_text(encoding="utf-8")
        for forbidden in ("fastapi", "pydantic", "httpx", "requests", "openai"):
            assert forbidden not in source, f"engine.py tidak boleh menyebut {forbidden}"

    def test_no_file_access(self) -> None:
        source = ENGINE_SOURCE.read_text(encoding="utf-8")
        for forbidden in ("open(", "json.load", "Path("):
            assert forbidden not in source, f"engine.py tidak boleh melakukan {forbidden}"

    def test_no_sorting_in_engine(self) -> None:
        """Ranking adalah tanggung jawab `ranking.py`, bukan engine."""
        source = ENGINE_SOURCE.read_text(encoding="utf-8")
        assert "sorted(" not in source
        assert ".sort(" not in source

    def test_does_not_mutate_input_recipe(self) -> None:
        target = recipe(("egg", True), ("chicken", True))
        before = target.ingredients
        match_recipe(frozenset({"egg"}), target, STAPLES)
        assert target.ingredients is before
