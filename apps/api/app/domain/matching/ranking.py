"""Ranking hasil matching — deterministik penuh.

Urutan sort dan tie-breaker: `docs/content-schema.md` §A.6 dan
`docs/technical-architecture.md` §8.5.

    1. matchPercentage DESC
    2. missingCount     ASC
    3. cookingTime      ASC
    4. recipeId         ASC (string compare)

`rank`, `filter_by_threshold`, dan `apply_limit` sengaja terpisah agar urutan operasi
(score -> filter -> sort -> limit) dikendalikan service, bukan tersembunyi di sini.
"""

from collections.abc import Sequence

from app.domain.models.match_result import MatchResult


def _sort_key(result: MatchResult) -> tuple[int, int, int, str]:
    """Sort key berlapis. Negasi persentase menghasilkan urutan menurun."""
    return (
        -result.match_percentage,
        result.missing_count,
        result.cooking_time_minutes,
        result.recipe_id,
    )


def rank(results: Sequence[MatchResult]) -> tuple[MatchResult, ...]:
    """Urutkan hasil dari paling relevan.

    Tidak memodifikasi input — mengembalikan tuple baru. Dua pemanggilan dengan
    input yang sama selalu menghasilkan urutan yang sama.
    """
    return tuple(sorted(results, key=_sort_key))


def filter_by_threshold(results: Sequence[MatchResult], threshold: int) -> tuple[MatchResult, ...]:
    """Buang hasil di bawah ambang relevansi.

    Dipanggil SEBELUM `apply_limit` agar slot limit tidak terpakai oleh hasil yang
    akan dibuang (`docs/content-schema.md` §A.6).
    """
    return tuple(result for result in results if result.match_percentage >= threshold)


def apply_limit(results: Sequence[MatchResult], limit: int) -> tuple[MatchResult, ...]:
    """Ambil `limit` hasil teratas. `limit <= 0` menghasilkan tuple kosong."""
    if limit <= 0:
        return ()
    return tuple(results[:limit])
