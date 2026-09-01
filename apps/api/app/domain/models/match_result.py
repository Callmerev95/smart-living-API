"""Hasil pencocokan satu resep terhadap bahan yang dimiliki user.

Bebas framework — hanya standard library. Lihat `docs/component-architecture.md` §17.

`cooking_time_minutes` sengaja dibawa di sini agar `ranking.py` cukup bergantung pada
`MatchResult` tanpa perlu objek `Recipe` — ranking hanya butuh sort key
(`docs/content-schema.md` §A.6).
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MatchResult:
    """Skor kecocokan satu resep.

    Attributes:
        recipe_id: Id resep yang dinilai.
        match_percentage: Integer 0-100, staple sudah dikecualikan dari denominator
            (Contract Delta v1.1 — `docs/content-schema.md` §A.9 Delta 1).
        available_ingredients: Bahan required non-staple yang user punya. Urutan
            mengikuti urutan `ingredients[]` di resep.
        missing_ingredients: Bahan required non-staple yang user belum punya. Urutan
            mengikuti urutan `ingredients[]` di resep.
        cooking_time_minutes: Dibawa untuk tie-breaker ranking ketiga.
    """

    recipe_id: str
    match_percentage: int
    available_ingredients: tuple[str, ...]
    missing_ingredients: tuple[str, ...]
    cooking_time_minutes: int

    @property
    def missing_count(self) -> int:
        """Jumlah bahan yang kurang — tie-breaker ranking kedua.

        Turunan dari `missing_ingredients`, bukan field terpisah, agar tidak mungkin
        tidak sinkron.
        """
        return len(self.missing_ingredients)
