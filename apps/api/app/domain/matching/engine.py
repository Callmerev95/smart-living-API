"""Matching engine — inti nilai produk.

Menerapkan `docs/content-schema.md` §A.5: definisi himpunan (§A.5.1), formula
(§A.5.2), dan available/missing (§A.5.3) — termasuk Contract Delta v1.1 Delta 1
(staple dikecualikan dari scoring).

Engine ini tidak tahu HTTP, tidak tahu FastAPI, tidak load file, dan tidak memanggil
LLM (`AGENTS.md` §4). Ranking BUKAN tanggung jawabnya — lihat `ranking.py`.
"""

from collections.abc import Iterable, Sequence

from app.domain.matching.scoring import calculate_match_percentage
from app.domain.models.match_result import MatchResult
from app.domain.models.recipe import Recipe


def match_recipe(
    user_ingredients: frozenset[str],
    recipe: Recipe,
    staple_names: frozenset[str],
) -> MatchResult:
    """Hitung kecocokan satu resep terhadap bahan user.

    Args:
        user_ingredients: Canonical name yang dimiliki user. `frozenset` agar
            lookup O(1) dan tidak bisa dimutasi engine.
        recipe: Resep yang dinilai.
        staple_names: Canonical name bahan pokok. Diterima sebagai himpunan agar
            engine tidak perlu tahu objek `Ingredient` maupun asal datanya.

    Returns:
        `MatchResult` dengan urutan `available_ingredients`/`missing_ingredients`
        mengikuti urutan `recipe.ingredients` — bukan urutan iterasi set — sehingga
        hasil deterministik (`docs/content-schema.md` §A.5.3).
    """
    available: list[str] = []
    missing: list[str] = []

    for item in recipe.ingredients:
        # Optional ingredient tidak memengaruhi skor maupun daftar kekurangan.
        if not item.required:
            continue
        # Delta 1: staple dianggap selalu tersedia, tidak dilaporkan sama sekali.
        if item.name in staple_names:
            continue

        if item.name in user_ingredients:
            available.append(item.name)
        else:
            missing.append(item.name)

    denominator = len(available) + len(missing)

    return MatchResult(
        recipe_id=recipe.id,
        match_percentage=calculate_match_percentage(len(available), denominator),
        available_ingredients=tuple(available),
        missing_ingredients=tuple(missing),
        cooking_time_minutes=recipe.cooking_time_minutes,
    )


def match_recipes(
    user_ingredients: Iterable[str],
    recipes: Sequence[Recipe],
    staple_names: frozenset[str],
) -> tuple[MatchResult, ...]:
    """Hitung kecocokan untuk banyak resep.

    Urutan hasil mengikuti urutan `recipes` — sorting dilakukan terpisah oleh
    `ranking.rank()` agar urutan operasi (score -> filter -> sort -> limit)
    dikendalikan service, bukan tersembunyi di dalam engine.
    """
    user_set = frozenset(user_ingredients)
    return tuple(match_recipe(user_set, recipe, staple_names) for recipe in recipes)
