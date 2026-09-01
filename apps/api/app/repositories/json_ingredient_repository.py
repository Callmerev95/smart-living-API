"""Implementasi `IngredientRepository` berbasis file JSON.

Selain list, membangun alias map `alias -> canonical` sekali saat init agar
lookup normalisasi O(1) (`docs/content-schema.md` §A.4.4).
"""

import json
from pathlib import Path
from typing import Any

from app.domain.models.ingredient import Ingredient, IngredientCategory
from app.repositories.base import IngredientRepository
from app.repositories.errors import DatasetLoadError


class JsonIngredientRepository(IngredientRepository):
    """Baca `ingredients.json` sekali, layani dari memori."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._ingredients: tuple[Ingredient, ...] = self._load(path)
        self._by_name: dict[str, Ingredient] = {
            ingredient.name: ingredient for ingredient in self._ingredients
        }
        self._alias_map: dict[str, str] = self._build_alias_map(self._ingredients, path)
        self._staple_names: frozenset[str] = frozenset(
            ingredient.name for ingredient in self._ingredients if ingredient.staple
        )

    # --- loading ---------------------------------------------------------- #

    @staticmethod
    def _load(path: Path) -> tuple[Ingredient, ...]:
        if not path.exists():
            raise DatasetLoadError(f"file ingredient tidak ditemukan: {path}")

        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise DatasetLoadError(f"JSON ingredient tidak valid di {path}: {exc}") from exc

        if not isinstance(raw, list):
            raise DatasetLoadError(f"root {path} harus berupa array")

        return tuple(
            JsonIngredientRepository._parse_ingredient(entry, index, path)
            for index, entry in enumerate(raw)
        )

    @staticmethod
    def _parse_ingredient(entry: Any, index: int, path: Path) -> Ingredient:
        location = f"{path.name}[{index}]"

        if not isinstance(entry, dict):
            raise DatasetLoadError(f"{location}: entry harus berupa object")

        try:
            category = IngredientCategory(entry["category"])
        except KeyError as exc:
            raise DatasetLoadError(f"{location}: field `category` tidak ada") from exc
        except ValueError as exc:
            raise DatasetLoadError(f"{location}: category tidak valid: {exc}") from exc

        try:
            return Ingredient(
                name=entry["name"],
                display_name=entry["displayName"],
                aliases=tuple(entry["aliases"]),
                category=category,
                staple=bool(entry["staple"]),
            )
        except (KeyError, TypeError) as exc:
            raise DatasetLoadError(
                f"{location}: struktur ingredient tidak sesuai kontrak: {exc}"
            ) from exc

    @staticmethod
    def _build_alias_map(ingredients: tuple[Ingredient, ...], path: Path) -> dict[str, str]:
        alias_map: dict[str, str] = {}
        alias_owner: dict[str, str] = {}

        for ingredient in ingredients:
            # canonical name juga ada di map — lookup "telur" dan "egg" seragam.
            if ingredient.name not in alias_map:
                alias_map[ingredient.name] = ingredient.name
                alias_owner[ingredient.name] = ingredient.name

            for alias in ingredient.aliases:
                normalized = alias.strip().lower()

                if normalized in alias_owner and alias_owner[normalized] != ingredient.name:
                    raise DatasetLoadError(
                        f"{path}: alias `{alias}` milik `{ingredient.name}` "
                        f"bertubrukan dengan `{alias_owner[normalized]}`"
                    )
                if normalized not in alias_map:
                    alias_map[normalized] = ingredient.name
                    alias_owner[normalized] = ingredient.name

        return alias_map

    # --- IngredientRepository --------------------------------------------- #

    def get_all(self) -> tuple[Ingredient, ...]:
        return self._ingredients

    def get_by_name(self, name: str) -> Ingredient | None:
        return self._by_name.get(name)

    def get_alias_map(self) -> dict[str, str]:
        return dict(self._alias_map)

    def get_staple_names(self) -> frozenset[str]:
        return self._staple_names

    def count(self) -> int:
        return len(self._ingredients)
