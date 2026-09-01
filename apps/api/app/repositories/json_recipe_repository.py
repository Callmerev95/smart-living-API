"""Implementasi `RecipeRepository` berbasis file JSON.

Dataset dimuat sekali saat inisialisasi dan disimpan in-memory sebagai tuple
(`docs/technical-architecture.md` §16). Mapping `camelCase` JSON ke `snake_case`
domain terjadi di sini — domain model tidak tahu soal format file.
"""

import json
from pathlib import Path
from typing import Any

from app.domain.models.recipe import Difficulty, Recipe, RecipeIngredient
from app.repositories.base import RecipeRepository
from app.repositories.errors import DatasetLoadError


class JsonRecipeRepository(RecipeRepository):
    """Baca `recipes.json` sekali, layani dari memori."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._recipes: tuple[Recipe, ...] = self._load(path)
        self._by_id: dict[str, Recipe] = {recipe.id: recipe for recipe in self._recipes}

    # --- loading ---------------------------------------------------------- #

    @staticmethod
    def _load(path: Path) -> tuple[Recipe, ...]:
        if not path.exists():
            raise DatasetLoadError(f"file resep tidak ditemukan: {path}")

        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise DatasetLoadError(f"JSON resep tidak valid di {path}: {exc}") from exc

        if not isinstance(raw, list):
            raise DatasetLoadError(f"root {path} harus berupa array")

        return tuple(
            JsonRecipeRepository._parse_recipe(entry, index, path)
            for index, entry in enumerate(raw)
        )

    @staticmethod
    def _parse_recipe(entry: Any, index: int, path: Path) -> Recipe:
        location = f"{path.name}[{index}]"

        if not isinstance(entry, dict):
            raise DatasetLoadError(f"{location}: entry harus berupa object")

        try:
            difficulty = Difficulty(entry["difficulty"])
        except KeyError as exc:
            raise DatasetLoadError(f"{location}: field `difficulty` tidak ada") from exc
        except ValueError as exc:
            raise DatasetLoadError(f"{location}: difficulty tidak valid: {exc}") from exc

        try:
            return Recipe(
                id=entry["id"],
                name=entry["name"],
                description=entry["description"],
                ingredients=tuple(
                    RecipeIngredient(name=item["name"], required=bool(item["required"]))
                    for item in entry["ingredients"]
                ),
                cooking_time_minutes=int(entry["cookingTimeMinutes"]),
                difficulty=difficulty,
                servings=int(entry["servings"]),
                steps=tuple(entry["steps"]),
                tags=tuple(entry["tags"]),
                source=entry["source"],
            )
        except (KeyError, TypeError) as exc:
            raise DatasetLoadError(
                f"{location}: struktur resep tidak sesuai kontrak: {exc}"
            ) from exc

    # --- RecipeRepository ------------------------------------------------- #

    def get_all(self) -> tuple[Recipe, ...]:
        return self._recipes

    def get_by_id(self, recipe_id: str) -> Recipe | None:
        return self._by_id.get(recipe_id)

    def count(self) -> int:
        return len(self._recipes)
