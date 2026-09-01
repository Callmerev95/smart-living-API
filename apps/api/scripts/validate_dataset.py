#!/usr/bin/env python
"""Validator dataset resep & bahan.

Memeriksa `data/recipes/ingredients.json` dan `data/recipes/recipes.json` terhadap
seluruh aturan `docs/content-schema.md` §A.2.4 dan §A.3.7.

Sengaja bekerja pada raw dict hasil `json.load`, bukan pada domain model yang sudah
di-parse: data rusak harus menghasilkan laporan pelanggaran yang rapi, bukan
exception saat parsing.

Pemakaian:
    uv run python scripts/validate_dataset.py
    uv run python scripts/validate_dataset.py --ingredients path --recipes path

Exit code 0 bila valid, 1 bila ada pelanggaran.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.core.config import get_settings
from app.domain.models.ingredient import IngredientCategory
from app.domain.models.recipe import Difficulty

RECIPE_ID_PATTERN = re.compile(r"^recipe_\d{3}$")

MIN_STEPS = 3
MAX_STEPS = 10
MAX_COOKING_TIME_MINUTES = 180
MIN_TAGS = 1
MAX_TAGS = 5
MIN_REQUIRED_NON_STAPLE = 2


@dataclass(frozen=True, slots=True)
class Violation:
    """Satu pelanggaran aturan dataset."""

    location: str
    rule: str
    detail: str

    def __str__(self) -> str:
        return f"{self.location}: [{self.rule}] {self.detail}"


# --------------------------------------------------------------------------- #
# Helper
# --------------------------------------------------------------------------- #


def load_json_array(path: Path, label: str) -> tuple[list[Any], list[Violation]]:
    """Baca file JSON yang seharusnya berisi array. Error dilaporkan, tidak di-raise."""
    if not path.exists():
        return [], [Violation(label, "file", f"file tidak ditemukan: {path}")]

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [], [Violation(label, "json", f"JSON tidak valid: {exc}")]

    if not isinstance(data, list):
        return [], [Violation(label, "struktur", "root harus berupa array")]

    return data, []


def _as_str(value: Any) -> str | None:
    return value if isinstance(value, str) else None


def _as_int(value: Any) -> int | None:
    # bool adalah subclass int di Python — jangan diterima sebagai angka.
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _as_list(value: Any) -> list[Any] | None:
    return value if isinstance(value, list) else None


# --------------------------------------------------------------------------- #
# Validasi ingredients.json — docs/content-schema.md §A.2.4
# --------------------------------------------------------------------------- #


def validate_ingredients(raw: list[Any]) -> list[Violation]:
    """Cek 6 aturan §A.2.4 plus kelengkapan field."""
    violations: list[Violation] = []
    valid_categories = {c.value for c in IngredientCategory}

    seen_names: dict[str, int] = {}
    alias_owner: dict[str, tuple[int, str]] = {}
    staple_count = 0

    for index, entry in enumerate(raw):
        loc = f"ingredients.json[{index}]"

        if not isinstance(entry, dict):
            violations.append(Violation(loc, "struktur", "entry harus berupa object"))
            continue

        name = _as_str(entry.get("name"))
        display_name = _as_str(entry.get("displayName"))
        aliases = _as_list(entry.get("aliases"))
        category = _as_str(entry.get("category"))
        staple = entry.get("staple")

        # --- field wajib ---
        if not name:
            violations.append(Violation(loc, "field", "`name` wajib berupa string non-empty"))
        if not display_name:
            violations.append(
                Violation(loc, "field", "`displayName` wajib berupa string non-empty")
            )
        if aliases is None:
            violations.append(Violation(loc, "field", "`aliases` wajib berupa array"))
        if not isinstance(staple, bool):
            violations.append(Violation(loc, "field", "`staple` wajib boolean"))
        elif staple:
            staple_count += 1

        # --- aturan 6: category valid ---
        if category is None:
            violations.append(Violation(loc, "field", "`category` wajib berupa string"))
        elif category not in valid_categories:
            violations.append(
                Violation(
                    loc,
                    "category",
                    f"`{category}` bukan kategori valid; pilihan: {sorted(valid_categories)}",
                )
            )

        if not name:
            continue

        # --- aturan 1: name unik ---
        if name in seen_names:
            violations.append(
                Violation(
                    loc,
                    "name unik",
                    f"`{name}` duplikat dengan ingredients.json[{seen_names[name]}]",
                )
            )
        else:
            seen_names[name] = index

        # --- aturan 5: alias lowercase & trimmed ---
        for alias_index, alias in enumerate(aliases or []):
            alias_loc = f"{loc}.aliases[{alias_index}]"
            alias_str = _as_str(alias)

            if alias_str is None:
                violations.append(Violation(alias_loc, "field", "alias harus berupa string"))
                continue
            if not alias_str:
                violations.append(Violation(alias_loc, "alias", "alias tidak boleh kosong"))
                continue
            if alias_str != alias_str.lower():
                violations.append(
                    Violation(alias_loc, "alias lowercase", f"`{alias_str}` harus lowercase")
                )
            if alias_str != alias_str.strip():
                violations.append(
                    Violation(alias_loc, "alias trimmed", f"`{alias_str}` mengandung spasi tepi")
                )

            normalized = alias_str.strip().lower()

            # --- aturan 2: alias tidak duplikat lintas ingredient ---
            if normalized in alias_owner:
                owner_index, owner_name = alias_owner[normalized]
                if owner_name != name:
                    violations.append(
                        Violation(
                            alias_loc,
                            "alias unik",
                            f"`{normalized}` sudah dipakai `{owner_name}` "
                            f"(ingredients.json[{owner_index}]) — normalisasi jadi ambigu",
                        )
                    )
                else:
                    violations.append(
                        Violation(
                            alias_loc,
                            "alias unik",
                            f"`{normalized}` duplikat di dalam ingredient yang sama",
                        )
                    )
            else:
                alias_owner[normalized] = (index, name)

    # --- aturan 3: alias tidak sama dengan name ingredient lain ---
    for alias, (alias_index, owner_name) in alias_owner.items():
        if alias in seen_names and seen_names[alias] != alias_index:
            violations.append(
                Violation(
                    f"ingredients.json[{alias_index}]",
                    "alias vs name",
                    f"`{owner_name}` punya alias `{alias}` yang merupakan canonical name "
                    f"ingredient lain (ingredients.json[{seen_names[alias]}])",
                )
            )

    # --- aturan 7: minimal satu staple ---
    if raw and staple_count == 0:
        violations.append(
            Violation(
                "ingredients.json",
                "staple",
                "minimal satu ingredient dengan `staple: true` (target 5-8)",
            )
        )

    return violations


# --------------------------------------------------------------------------- #
# Validasi recipes.json — docs/content-schema.md §A.3.7
# --------------------------------------------------------------------------- #


def build_ingredient_index(raw: list[Any]) -> dict[str, bool]:
    """Petakan canonical name -> flag staple. Dipakai untuk cek referensi resep."""
    index: dict[str, bool] = {}
    for entry in raw:
        if isinstance(entry, dict):
            name = _as_str(entry.get("name"))
            if name:
                index[name] = bool(entry.get("staple"))
    return index


def _validate_recipe_ingredients(
    loc: str,
    entry: dict[str, Any],
    ingredient_index: dict[str, bool],
) -> list[Violation]:
    """Cek aturan 2, 3, dan 4 §A.3.7 untuk satu resep."""
    violations: list[Violation] = []
    items = _as_list(entry.get("ingredients"))

    if items is None:
        return [Violation(loc, "field", "`ingredients` wajib berupa array")]
    if not items:
        return [Violation(loc, "ingredients", "`ingredients` tidak boleh kosong")]

    seen: dict[str, int] = {}
    required_non_staple = 0

    for item_index, item in enumerate(items):
        item_loc = f"{loc}.ingredients[{item_index}]"

        if not isinstance(item, dict):
            violations.append(Violation(item_loc, "struktur", "item harus berupa object"))
            continue

        item_name = _as_str(item.get("name"))
        required = item.get("required")

        if not item_name:
            violations.append(Violation(item_loc, "field", "`name` wajib string non-empty"))
            continue
        if not isinstance(required, bool):
            violations.append(Violation(item_loc, "field", "`required` wajib boolean"))
            continue

        # --- aturan 2: referential integrity ---
        if item_name not in ingredient_index:
            violations.append(
                Violation(
                    item_loc,
                    "referential integrity",
                    f"`{item_name}` tidak terdaftar di ingredients.json",
                )
            )
            continue

        # --- aturan 3: tidak duplikat dalam satu resep ---
        if item_name in seen:
            violations.append(
                Violation(
                    item_loc,
                    "ingredient duplikat",
                    f"`{item_name}` sudah muncul di index {seen[item_name]}",
                )
            )
            continue
        seen[item_name] = item_index

        if required and not ingredient_index[item_name]:
            required_non_staple += 1

    # --- aturan 4: minimal 2 required non-staple ---
    if required_non_staple < MIN_REQUIRED_NON_STAPLE:
        violations.append(
            Violation(
                loc,
                "required non-staple",
                f"hanya {required_non_staple} required non-staple, minimal "
                f"{MIN_REQUIRED_NON_STAPLE} (denominator scoring tidak boleh 0)",
            )
        )

    return violations


def validate_recipes(raw: list[Any], ingredient_index: dict[str, bool]) -> list[Violation]:
    """Cek 10 aturan §A.3.7 plus kelengkapan field."""
    violations: list[Violation] = []
    valid_difficulties = {d.value for d in Difficulty}
    seen_ids: dict[str, int] = {}

    for index, entry in enumerate(raw):
        loc = f"recipes.json[{index}]"

        if not isinstance(entry, dict):
            violations.append(Violation(loc, "struktur", "entry harus berupa object"))
            continue

        recipe_id = _as_str(entry.get("id"))
        name = _as_str(entry.get("name"))
        description = _as_str(entry.get("description"))
        cooking_time = _as_int(entry.get("cookingTimeMinutes"))
        difficulty = _as_str(entry.get("difficulty"))
        servings = _as_int(entry.get("servings"))
        steps = _as_list(entry.get("steps"))
        tags = _as_list(entry.get("tags"))
        source = _as_str(entry.get("source"))

        # --- aturan 1: id unik + format recipe_NNN ---
        if not recipe_id:
            violations.append(Violation(loc, "field", "`id` wajib string non-empty"))
        else:
            if not RECIPE_ID_PATTERN.match(recipe_id):
                violations.append(
                    Violation(loc, "id format", f"`{recipe_id}` harus mengikuti pola recipe_NNN")
                )
            if recipe_id in seen_ids:
                violations.append(
                    Violation(
                        loc,
                        "id unik",
                        f"`{recipe_id}` duplikat dengan recipes.json[{seen_ids[recipe_id]}]",
                    )
                )
            else:
                seen_ids[recipe_id] = index

        if not name:
            violations.append(Violation(loc, "field", "`name` wajib string non-empty"))
        if not description:
            violations.append(Violation(loc, "field", "`description` wajib string non-empty"))

        # --- aturan 2, 3, 4 ---
        violations.extend(_validate_recipe_ingredients(loc, entry, ingredient_index))

        # --- aturan 5: jumlah steps ---
        if steps is None:
            violations.append(Violation(loc, "field", "`steps` wajib berupa array"))
        else:
            if not MIN_STEPS <= len(steps) <= MAX_STEPS:
                violations.append(
                    Violation(
                        loc,
                        "steps",
                        f"{len(steps)} langkah; harus antara {MIN_STEPS} dan {MAX_STEPS}",
                    )
                )
            for step_index, step in enumerate(steps):
                step_str = _as_str(step)
                if not step_str or not step_str.strip():
                    violations.append(
                        Violation(
                            f"{loc}.steps[{step_index}]",
                            "steps",
                            "langkah harus string non-empty",
                        )
                    )

        # --- aturan 6: cooking time ---
        if cooking_time is None:
            violations.append(Violation(loc, "field", "`cookingTimeMinutes` wajib integer"))
        elif not 0 < cooking_time <= MAX_COOKING_TIME_MINUTES:
            violations.append(
                Violation(
                    loc,
                    "cookingTimeMinutes",
                    f"{cooking_time} di luar rentang 1..{MAX_COOKING_TIME_MINUTES}",
                )
            )

        # --- aturan 7: difficulty ---
        if difficulty is None:
            violations.append(Violation(loc, "field", "`difficulty` wajib berupa string"))
        elif difficulty not in valid_difficulties:
            violations.append(
                Violation(
                    loc,
                    "difficulty",
                    f"`{difficulty}` tidak valid; pilihan: {sorted(valid_difficulties)}",
                )
            )

        # --- aturan 8: servings ---
        if servings is None:
            violations.append(Violation(loc, "field", "`servings` wajib integer"))
        elif servings <= 0:
            violations.append(Violation(loc, "servings", f"{servings} harus lebih dari 0"))

        # --- aturan 9: tags ---
        if tags is None:
            violations.append(Violation(loc, "field", "`tags` wajib berupa array"))
        elif not MIN_TAGS <= len(tags) <= MAX_TAGS:
            violations.append(
                Violation(loc, "tags", f"{len(tags)} tag; harus antara {MIN_TAGS} dan {MAX_TAGS}")
            )

        # --- aturan 10: source ---
        if not source:
            violations.append(Violation(loc, "field", "`source` wajib string non-empty"))

    return violations


def validate_dataset(ingredients_path: Path, recipes_path: Path) -> list[Violation]:
    """Validasi kedua file. Semua pelanggaran dikumpulkan, tidak berhenti di error pertama."""
    raw_ingredients, ingredient_errors = load_json_array(ingredients_path, "ingredients.json")
    raw_recipes, recipe_errors = load_json_array(recipes_path, "recipes.json")

    violations = [*ingredient_errors, *recipe_errors]
    violations.extend(validate_ingredients(raw_ingredients))
    violations.extend(validate_recipes(raw_recipes, build_ingredient_index(raw_ingredients)))
    return violations


# --------------------------------------------------------------------------- #
# Laporan ringkas — bukan pelanggaran, untuk audit T-P2-08
# --------------------------------------------------------------------------- #


def build_report(raw_ingredients: list[Any], raw_recipes: list[Any]) -> str:
    """Ringkasan komposisi dataset untuk dibandingkan dengan target §A.8."""
    lines: list[str] = []
    recipes = [entry for entry in raw_recipes if isinstance(entry, dict)]
    ingredients = [entry for entry in raw_ingredients if isinstance(entry, dict)]

    staples = sorted(str(i.get("name")) for i in ingredients if i.get("staple") is True)

    lines.append(f"Ingredient : {len(ingredients)}")
    lines.append(f"Staple     : {len(staples)} ({', '.join(staples) or '-'})")
    lines.append(f"Resep      : {len(recipes)}")

    if not recipes:
        return "\n".join(lines)

    difficulty_counts = Counter(str(r.get("difficulty")) for r in recipes)
    lines.append("")
    lines.append("Distribusi difficulty:")
    for level in (d.value for d in Difficulty):
        count = difficulty_counts.get(level, 0)
        lines.append(f"  {level:<7} {count:>3}  ({count / len(recipes) * 100:.0f}%)")

    buckets = {"<=15 menit": 0, "16-30 menit": 0, ">30 menit": 0}
    for recipe in recipes:
        minutes = _as_int(recipe.get("cookingTimeMinutes")) or 0
        if minutes <= 15:
            buckets["<=15 menit"] += 1
        elif minutes <= 30:
            buckets["16-30 menit"] += 1
        else:
            buckets[">30 menit"] += 1

    lines.append("")
    lines.append("Distribusi waktu:")
    for label, count in buckets.items():
        lines.append(f"  {label:<12} {count:>3}  ({count / len(recipes) * 100:.0f}%)")

    ingredient_usage: Counter[str] = Counter()
    total_items = 0
    for recipe in recipes:
        for item in _as_list(recipe.get("ingredients")) or []:
            if isinstance(item, dict):
                item_name = _as_str(item.get("name"))
                if item_name:
                    ingredient_usage[item_name] += 1
                    total_items += 1

    lines.append("")
    lines.append(f"Rata-rata bahan per resep: {total_items / len(recipes):.1f}")
    lines.append("")
    lines.append("Top 10 bahan tersering (indikator overlap):")
    for item_name, count in ingredient_usage.most_common(10):
        lines.append(f"  {item_name:<18} {count:>3} resep")

    unused = sorted({str(i.get("name")) for i in ingredients} - set(ingredient_usage))
    if unused:
        lines.append("")
        lines.append(f"Bahan belum dipakai resep ({len(unused)}): {', '.join(unused)}")

    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def main(argv: list[str] | None = None) -> int:
    settings = get_settings()

    parser = argparse.ArgumentParser(description="Validasi dataset resep & bahan.")
    parser.add_argument("--ingredients", type=Path, default=settings.ingredients_path)
    parser.add_argument("--recipes", type=Path, default=settings.recipes_path)
    parser.add_argument("--quiet", action="store_true", help="jangan cetak laporan ringkas")
    args = parser.parse_args(argv)

    violations = validate_dataset(args.ingredients, args.recipes)

    if violations:
        print(f"GAGAL — {len(violations)} pelanggaran:\n")
        for violation in violations:
            print(f"  {violation}")
        return 1

    print("OK — dataset valid.")

    if not args.quiet:
        raw_ingredients, _ = load_json_array(args.ingredients, "ingredients.json")
        raw_recipes, _ = load_json_array(args.recipes, "recipes.json")
        print()
        print(build_report(raw_ingredients, raw_recipes))

    return 0


if __name__ == "__main__":
    sys.exit(main())
