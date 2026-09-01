"""Domain model untuk resep.

Bebas framework — hanya standard library. Lihat `docs/content-schema.md` §A.3.

Tidak ada field `quantity`/`unit`: kuantitas out of scope MVP
(`docs/content-schema.md` §A.3.3, jawaban PRD §26 Q4).
"""

from dataclasses import dataclass
from enum import StrEnum


class Difficulty(StrEnum):
    """Tingkat kesulitan resep (`docs/content-schema.md` §A.3.4)."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


@dataclass(frozen=True, slots=True)
class RecipeIngredient:
    """Satu baris bahan di dalam resep.

    Attributes:
        name: Harus merujuk `Ingredient.name` yang terdaftar di `ingredients.json`.
        required: `True` bila bahan wajib. Bahan `required=False` tidak memengaruhi
            `matchPercentage` dan tidak masuk `missingIngredients`.
    """

    name: str
    required: bool


@dataclass(frozen=True, slots=True)
class Recipe:
    """Satu resep lengkap.

    Attributes:
        id: Format `recipe_NNN`. Dipakai sebagai tie-breaker ranking terakhir dan
            sebagai path parameter detail resep.
        name: Nama resep bahasa Indonesia.
        description: Satu kalimat penjelas hasil akhir.
        ingredients: Urutan dipertahankan — menentukan urutan
            `availableIngredients`/`missingIngredients` di response sehingga hasil
            deterministik (`docs/content-schema.md` §A.5.3).
        cooking_time_minutes: Waktu total. Tie-breaker ranking ketiga.
        difficulty: Tingkat kesulitan.
        servings: Jumlah porsi.
        steps: Langkah memasak, urutan berasal dari posisi array.
        tags: Label untuk personalisasi masa depan. Belum dipakai matching di MVP.
        source: MVP selalu `"original"`.
    """

    id: str
    name: str
    description: str
    ingredients: tuple[RecipeIngredient, ...]
    cooking_time_minutes: int
    difficulty: Difficulty
    servings: int
    steps: tuple[str, ...]
    tags: tuple[str, ...]
    source: str

    def required_ingredient_names(self) -> tuple[str, ...]:
        """Nama bahan `required=True`, urutan sesuai `ingredients`.

        Staple TIDAK difilter di sini — pengecualian staple adalah tanggung jawab
        scoring (`docs/content-schema.md` §A.5.1), bukan model. Model tidak tahu
        bahan mana yang staple karena informasi itu ada di `ingredients.json`.
        """
        return tuple(item.name for item in self.ingredients if item.required)

    def all_ingredient_names(self) -> tuple[str, ...]:
        """Semua nama bahan (required + optional + staple), urutan asli.

        Dipakai untuk field `ingredients` di response — daftar lengkap yang
        ditampilkan di detail resep (`docs/content-schema.md` §A.5.4).
        """
        return tuple(item.name for item in self.ingredients)
