"""Domain model untuk ingredient kanonik.

Model ini bebas framework — hanya standard library. Mapping ke/dari JSON
(`camelCase`) terjadi di repository, mapping ke response API terjadi di schema.
Lihat `docs/content-schema.md` §A.2 dan `AGENTS.md` §4.
"""

from dataclasses import dataclass
from enum import StrEnum


class IngredientCategory(StrEnum):
    """Kategori bahan untuk grouping/filter UI (`docs/content-schema.md` §A.2.3).

    Catatan: `IngredientCategory.STAPLE` dan flag `Ingredient.staple` adalah dua
    hal berbeda. Kategori untuk presentasi, flag untuk aturan scoring.
    """

    PROTEIN = "protein"
    VEGETABLE = "vegetable"
    FRUIT = "fruit"
    GRAIN = "grain"
    DAIRY = "dairy"
    SPICE = "spice"
    CONDIMENT = "condiment"
    STAPLE = "staple"
    OTHER = "other"


@dataclass(frozen=True, slots=True)
class Ingredient:
    """Satu bahan kanonik beserta aliasnya.

    Attributes:
        name: Canonical name (bahasa Inggris, lowercase, snake_case). Immutable
            karena dipakai sebagai referensi di `recipes.json`.
        display_name: Label tampilan bahasa Indonesia.
        aliases: Varian input yang dipetakan ke `name`. Urutan dipertahankan agar
            output `GET /api/v1/ingredients` deterministik.
        category: Kategori presentasi.
        staple: `True` bila bahan dianggap selalu tersedia di dapur user sehingga
            dikecualikan dari scoring (Contract Delta v1.1 — `docs/content-schema.md`
            §A.9 Delta 1).
    """

    name: str
    display_name: str
    aliases: tuple[str, ...]
    category: IngredientCategory
    staple: bool
