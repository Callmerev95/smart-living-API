"""Test untuk `scripts.validate_dataset`.

Setiap aturan `docs/content-schema.md` §A.2.4 dan §A.3.7 punya test dengan fixture
yang sengaja dibuat rusak.
"""

import json
from pathlib import Path
from typing import Any

import pytest

from scripts.validate_dataset import (
    build_ingredient_index,
    build_report,
    main,
    validate_dataset,
    validate_ingredients,
    validate_recipes,
)

# --------------------------------------------------------------------------- #
# Fixture builder
# --------------------------------------------------------------------------- #


def ingredient(
    name: str,
    *,
    aliases: list[str] | None = None,
    category: str = "protein",
    staple: bool = False,
    display_name: str | None = None,
) -> dict[str, Any]:
    return {
        "name": name,
        "displayName": display_name or name.replace("_", " ").title(),
        "aliases": aliases if aliases is not None else [],
        "category": category,
        "staple": staple,
    }


def recipe(
    recipe_id: str = "recipe_001",
    *,
    ingredients: list[dict[str, Any]] | None = None,
    cooking_time: int = 15,
    difficulty: str = "easy",
    servings: int = 2,
    steps: list[str] | None = None,
    tags: list[str] | None = None,
    source: str = "original",
) -> dict[str, Any]:
    return {
        "id": recipe_id,
        "name": "Omelet Ayam Wortel",
        "description": "Omelet praktis dengan ayam dan wortel.",
        "ingredients": (
            ingredients
            if ingredients is not None
            else [
                {"name": "egg", "required": True},
                {"name": "chicken", "required": True},
                {"name": "salt", "required": True},
            ]
        ),
        "cookingTimeMinutes": cooking_time,
        "difficulty": difficulty,
        "servings": servings,
        "steps": steps if steps is not None else ["Kocok telur.", "Tumis ayam.", "Sajikan."],
        "tags": tags if tags is not None else ["sarapan"],
        "source": source,
    }


BASE_INGREDIENTS: list[dict[str, Any]] = [
    ingredient("egg", aliases=["telur", "eggs"]),
    ingredient("chicken", aliases=["ayam"]),
    ingredient("carrot", aliases=["wortel"], category="vegetable"),
    ingredient("salt", aliases=["garam"], category="staple", staple=True),
    ingredient("cooking_oil", aliases=["minyak"], category="staple", staple=True),
]


def rules(violations: list[Any]) -> set[str]:
    return {v.rule for v in violations}


def write_dataset(
    tmp_path: Path,
    ingredients: list[Any],
    recipes: list[Any],
) -> tuple[Path, Path]:
    ing_path = tmp_path / "ingredients.json"
    rec_path = tmp_path / "recipes.json"
    ing_path.write_text(json.dumps(ingredients), encoding="utf-8")
    rec_path.write_text(json.dumps(recipes), encoding="utf-8")
    return ing_path, rec_path


# --------------------------------------------------------------------------- #
# Baseline: dataset valid
# --------------------------------------------------------------------------- #


class TestValidDataset:
    def test_valid_dataset_has_no_violations(self) -> None:
        assert validate_ingredients(BASE_INGREDIENTS) == []
        assert validate_recipes([recipe()], build_ingredient_index(BASE_INGREDIENTS)) == []

    def test_empty_files_are_tolerated(self) -> None:
        """File kosong bukan pelanggaran aturan — hanya dataset yang belum diisi."""
        assert validate_ingredients([]) == []
        assert validate_recipes([], {}) == []


# --------------------------------------------------------------------------- #
# ingredients.json — §A.2.4
# --------------------------------------------------------------------------- #


class TestIngredientRules:
    def test_rule1_duplicate_name(self) -> None:
        violations = validate_ingredients([*BASE_INGREDIENTS, ingredient("egg")])
        assert "name unik" in rules(violations)

    def test_rule2_duplicate_alias_across_ingredients(self) -> None:
        """`telur` dipakai dua ingredient -> normalisasi ambigu."""
        violations = validate_ingredients(
            [*BASE_INGREDIENTS, ingredient("quail_egg", aliases=["telur"])]
        )
        assert "alias unik" in rules(violations)

    def test_rule2_duplicate_alias_within_same_ingredient(self) -> None:
        violations = validate_ingredients([ingredient("egg", aliases=["telur", "telur"])])
        assert "alias unik" in rules(violations)

    def test_rule3_alias_collides_with_other_canonical_name(self) -> None:
        """`chili` beralias `pepper` sementara `pepper` adalah ingredient tersendiri."""
        violations = validate_ingredients(
            [
                ingredient("pepper", category="spice"),
                ingredient("chili", aliases=["pepper"], category="spice"),
            ]
        )
        assert "alias vs name" in rules(violations)

    def test_rule5_alias_must_be_lowercase(self) -> None:
        violations = validate_ingredients([ingredient("egg", aliases=["Telur"])])
        assert "alias lowercase" in rules(violations)

    def test_rule5_alias_must_be_trimmed(self) -> None:
        violations = validate_ingredients([ingredient("egg", aliases=[" telur "])])
        assert "alias trimmed" in rules(violations)

    def test_rule6_invalid_category(self) -> None:
        violations = validate_ingredients([ingredient("egg", category="protien")])
        assert "category" in rules(violations)

    def test_rule7_at_least_one_staple(self) -> None:
        violations = validate_ingredients([ingredient("egg"), ingredient("chicken")])
        assert "staple" in rules(violations)

    def test_missing_required_fields(self) -> None:
        violations = validate_ingredients([{"name": "egg"}])
        assert "field" in rules(violations)

    def test_non_object_entry(self) -> None:
        violations = validate_ingredients(["egg"])
        assert "struktur" in rules(violations)


# --------------------------------------------------------------------------- #
# recipes.json — §A.3.7
# --------------------------------------------------------------------------- #


class TestRecipeRules:
    @pytest.fixture
    def index(self) -> dict[str, bool]:
        return build_ingredient_index(BASE_INGREDIENTS)

    def test_rule1_duplicate_id(self, index: dict[str, bool]) -> None:
        violations = validate_recipes([recipe("recipe_001"), recipe("recipe_001")], index)
        assert "id unik" in rules(violations)

    def test_rule1_invalid_id_format(self, index: dict[str, bool]) -> None:
        for bad_id in ("recipe_1", "recipe-001", "001", "resep_001"):
            violations = validate_recipes([recipe(bad_id)], index)
            assert "id format" in rules(violations), bad_id

    def test_rule2_referential_integrity(self, index: dict[str, bool]) -> None:
        """Bahan yang tidak terdaftar akan membuat matching silent-fail."""
        violations = validate_recipes(
            [
                recipe(
                    ingredients=[
                        {"name": "egg", "required": True},
                        {"name": "chicken", "required": True},
                        {"name": "kangkung", "required": True},
                    ]
                )
            ],
            index,
        )
        assert "referential integrity" in rules(violations)

    def test_rule3_duplicate_ingredient_in_recipe(self, index: dict[str, bool]) -> None:
        violations = validate_recipes(
            [
                recipe(
                    ingredients=[
                        {"name": "egg", "required": True},
                        {"name": "chicken", "required": True},
                        {"name": "egg", "required": False},
                    ]
                )
            ],
            index,
        )
        assert "ingredient duplikat" in rules(violations)

    def test_rule4_all_required_are_staple(self, index: dict[str, bool]) -> None:
        """Denominator scoring akan 0 — dilarang (docs/content-schema.md §A.5.5 case 8)."""
        violations = validate_recipes(
            [
                recipe(
                    ingredients=[
                        {"name": "salt", "required": True},
                        {"name": "cooking_oil", "required": True},
                    ]
                )
            ],
            index,
        )
        assert "required non-staple" in rules(violations)

    def test_rule4_only_one_required_non_staple(self, index: dict[str, bool]) -> None:
        violations = validate_recipes(
            [
                recipe(
                    ingredients=[
                        {"name": "egg", "required": True},
                        {"name": "chicken", "required": False},
                        {"name": "salt", "required": True},
                    ]
                )
            ],
            index,
        )
        assert "required non-staple" in rules(violations)

    def test_rule5_too_few_steps(self, index: dict[str, bool]) -> None:
        violations = validate_recipes([recipe(steps=["Kocok telur.", "Sajikan."])], index)
        assert "steps" in rules(violations)

    def test_rule5_too_many_steps(self, index: dict[str, bool]) -> None:
        violations = validate_recipes([recipe(steps=[f"Langkah {i}." for i in range(11)])], index)
        assert "steps" in rules(violations)

    def test_rule5_empty_step_string(self, index: dict[str, bool]) -> None:
        violations = validate_recipes([recipe(steps=["Kocok telur.", "   ", "Sajikan."])], index)
        assert "steps" in rules(violations)

    def test_rule6_cooking_time_zero(self, index: dict[str, bool]) -> None:
        violations = validate_recipes([recipe(cooking_time=0)], index)
        assert "cookingTimeMinutes" in rules(violations)

    def test_rule6_cooking_time_too_long(self, index: dict[str, bool]) -> None:
        violations = validate_recipes([recipe(cooking_time=181)], index)
        assert "cookingTimeMinutes" in rules(violations)

    def test_rule7_invalid_difficulty(self, index: dict[str, bool]) -> None:
        violations = validate_recipes([recipe(difficulty="sedang")], index)
        assert "difficulty" in rules(violations)

    def test_rule8_servings_zero(self, index: dict[str, bool]) -> None:
        violations = validate_recipes([recipe(servings=0)], index)
        assert "servings" in rules(violations)

    def test_rule9_no_tags(self, index: dict[str, bool]) -> None:
        violations = validate_recipes([recipe(tags=[])], index)
        assert "tags" in rules(violations)

    def test_rule9_too_many_tags(self, index: dict[str, bool]) -> None:
        violations = validate_recipes([recipe(tags=["a", "b", "c", "d", "e", "f"])], index)
        assert "tags" in rules(violations)

    def test_rule10_empty_source(self, index: dict[str, bool]) -> None:
        violations = validate_recipes([recipe(source="")], index)
        assert "field" in rules(violations)

    def test_boolean_not_accepted_as_int(self, index: dict[str, bool]) -> None:
        """`True` adalah subclass int di Python — jangan lolos sebagai cookingTimeMinutes."""
        entry = recipe()
        entry["cookingTimeMinutes"] = True
        violations = validate_recipes([entry], index)
        assert "field" in rules(violations)


# --------------------------------------------------------------------------- #
# Perilaku agregat
# --------------------------------------------------------------------------- #


class TestAggregateBehaviour:
    def test_reports_all_violations_not_just_first(self) -> None:
        """Memperbaiki dataset lebih murah bila semua masalah terlihat sekaligus."""
        violations = validate_recipes(
            [recipe("recipe_1", cooking_time=0, servings=0, tags=[], difficulty="sedang")],
            build_ingredient_index(BASE_INGREDIENTS),
        )
        assert len(violations) >= 5
        assert {"id format", "cookingTimeMinutes", "servings", "tags", "difficulty"} <= rules(
            violations
        )

    def test_violation_message_includes_location(self) -> None:
        violations = validate_recipes(
            [
                recipe(
                    ingredients=[
                        {"name": "egg", "required": True},
                        {"name": "chicken", "required": True},
                        {"name": "kangkung", "required": True},
                    ]
                )
            ],
            build_ingredient_index(BASE_INGREDIENTS),
        )
        message = str(violations[0])
        assert "recipes.json[0].ingredients[2]" in message
        assert "kangkung" in message


# --------------------------------------------------------------------------- #
# File handling & CLI
# --------------------------------------------------------------------------- #


class TestFileHandling:
    def test_missing_file_reported_not_raised(self, tmp_path: Path) -> None:
        violations = validate_dataset(tmp_path / "nope.json", tmp_path / "also-nope.json")
        assert len(violations) == 2
        assert rules(violations) == {"file"}

    def test_malformed_json_reported(self, tmp_path: Path) -> None:
        ing_path = tmp_path / "ingredients.json"
        rec_path = tmp_path / "recipes.json"
        ing_path.write_text("{not json", encoding="utf-8")
        rec_path.write_text("[]", encoding="utf-8")
        violations = validate_dataset(ing_path, rec_path)
        assert "json" in rules(violations)

    def test_root_must_be_array(self, tmp_path: Path) -> None:
        ing_path = tmp_path / "ingredients.json"
        rec_path = tmp_path / "recipes.json"
        ing_path.write_text('{"name": "egg"}', encoding="utf-8")
        rec_path.write_text("[]", encoding="utf-8")
        violations = validate_dataset(ing_path, rec_path)
        assert "struktur" in rules(violations)

    def test_valid_dataset_from_disk(self, tmp_path: Path) -> None:
        ing_path, rec_path = write_dataset(tmp_path, BASE_INGREDIENTS, [recipe()])
        assert validate_dataset(ing_path, rec_path) == []


class TestCli:
    def test_exit_code_zero_when_valid(self, tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
        ing_path, rec_path = write_dataset(tmp_path, BASE_INGREDIENTS, [recipe()])
        exit_code = main(["--ingredients", str(ing_path), "--recipes", str(rec_path)])
        assert exit_code == 0
        assert "OK" in capsys.readouterr().out

    def test_exit_code_one_when_invalid(
        self, tmp_path: Path, capsys: pytest.CaptureFixture
    ) -> None:
        ing_path, rec_path = write_dataset(tmp_path, BASE_INGREDIENTS, [recipe("bad_id")])
        exit_code = main(["--ingredients", str(ing_path), "--recipes", str(rec_path)])
        assert exit_code == 1
        assert "GAGAL" in capsys.readouterr().out

    def test_quiet_suppresses_report(self, tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
        ing_path, rec_path = write_dataset(tmp_path, BASE_INGREDIENTS, [recipe()])
        main(["--ingredients", str(ing_path), "--recipes", str(rec_path), "--quiet"])
        assert "Distribusi difficulty" not in capsys.readouterr().out


class TestReport:
    def test_report_contains_key_metrics(self) -> None:
        report = build_report(BASE_INGREDIENTS, [recipe(), recipe("recipe_002", cooking_time=45)])
        assert "Ingredient : 5" in report
        assert "Resep      : 2" in report
        assert "Distribusi difficulty" in report
        assert "Distribusi waktu" in report
        assert "Top 10 bahan tersering" in report

    def test_report_lists_unused_ingredients(self) -> None:
        """Bahan tak terpakai bukan error, tapi tanda dataset belum seimbang."""
        report = build_report(BASE_INGREDIENTS, [recipe()])
        assert "Bahan belum dipakai" in report
        assert "carrot" in report

    def test_report_handles_empty_recipes(self) -> None:
        report = build_report(BASE_INGREDIENTS, [])
        assert "Resep      : 0" in report
        assert "Distribusi difficulty" not in report
