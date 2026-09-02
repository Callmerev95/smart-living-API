"""Test untuk `domain/matching/ranking`.

Berisi seluruh 7 test case wajib `docs/content-schema.md` §A.6.1.
"""

import random

from app.domain.matching.ranking import apply_limit, filter_by_threshold, rank
from app.domain.models.match_result import MatchResult


def result(
    recipe_id: str = "recipe_001",
    *,
    pct: int = 75,
    missing: int = 1,
    minutes: int = 15,
) -> MatchResult:
    """Bangun MatchResult dengan `missing_count` sesuai jumlah yang diminta."""
    return MatchResult(
        recipe_id=recipe_id,
        match_percentage=pct,
        available_ingredients=("egg",),
        missing_ingredients=tuple(f"missing_{i}" for i in range(missing)),
        cooking_time_minutes=minutes,
    )


def ids(results: tuple[MatchResult, ...]) -> list[str]:
    return [r.recipe_id for r in results]


# --------------------------------------------------------------------------- #
# 7 test case wajib — docs/content-schema.md §A.6.1
# --------------------------------------------------------------------------- #


class TestSpecCases:
    def test_case1_different_percentage(self) -> None:
        a = result("recipe_a", pct=80)
        b = result("recipe_b", pct=60)
        assert ids(rank([b, a])) == ["recipe_a", "recipe_b"]

    def test_case2_same_percentage_different_missing(self) -> None:
        a = result("recipe_a", pct=75, missing=1)
        b = result("recipe_b", pct=75, missing=2)
        assert ids(rank([b, a])) == ["recipe_a", "recipe_b"]

    def test_case3_same_percentage_and_missing_different_time(self) -> None:
        a = result("recipe_a", pct=75, missing=1, minutes=20)
        b = result("recipe_b", pct=75, missing=1, minutes=15)
        assert ids(rank([a, b])) == ["recipe_b", "recipe_a"]

    def test_case4_all_equal_different_id(self) -> None:
        """Tie-breaker terakhir: id sebagai string compare."""
        a = result("recipe_005")
        b = result("recipe_002")
        assert ids(rank([a, b])) == ["recipe_002", "recipe_005"]

    def test_case5_threshold_filters_below(self) -> None:
        a = result("recipe_a", pct=80)
        b = result("recipe_b", pct=25)
        assert ids(filter_by_threshold([a, b], 30)) == ["recipe_a"]

    def test_case6_limit_takes_top_n(self) -> None:
        results = [result(f"recipe_{i:03d}", pct=100 - i) for i in range(8)]
        ranked = rank(results)
        limited = apply_limit(ranked, 5)
        assert len(limited) == 5
        assert ids(limited) == ids(ranked[:5])

    def test_case7_empty_after_filter(self) -> None:
        results = [result("recipe_a", pct=25), result("recipe_b", pct=10)]
        assert filter_by_threshold(results, 30) == ()


# --------------------------------------------------------------------------- #
# Urutan tie-breaker berlapis
# --------------------------------------------------------------------------- #


class TestTieBreakerPrecedence:
    def test_percentage_beats_missing_count(self) -> None:
        """Skor lebih tinggi menang meski missing lebih banyak."""
        high = result("recipe_a", pct=80, missing=5)
        low = result("recipe_b", pct=60, missing=0)
        assert ids(rank([low, high])) == ["recipe_a", "recipe_b"]

    def test_missing_beats_cooking_time(self) -> None:
        fewer_missing = result("recipe_a", pct=75, missing=1, minutes=90)
        faster = result("recipe_b", pct=75, missing=3, minutes=5)
        assert ids(rank([faster, fewer_missing])) == ["recipe_a", "recipe_b"]

    def test_cooking_time_beats_id(self) -> None:
        faster = result("recipe_zzz", pct=75, missing=1, minutes=10)
        slower = result("recipe_aaa", pct=75, missing=1, minutes=20)
        assert ids(rank([slower, faster])) == ["recipe_zzz", "recipe_aaa"]

    def test_id_compared_as_string(self) -> None:
        """`recipe_002` < `recipe_005` secara leksikografis (zero-padded)."""
        results = [result("recipe_010"), result("recipe_002"), result("recipe_005")]
        assert ids(rank(results)) == ["recipe_002", "recipe_005", "recipe_010"]

    def test_full_four_level_ordering(self) -> None:
        results = [
            result("recipe_004", pct=75, missing=1, minutes=20),
            result("recipe_003", pct=75, missing=1, minutes=20),
            result("recipe_002", pct=75, missing=1, minutes=10),
            result("recipe_001", pct=75, missing=0, minutes=99),
            result("recipe_000", pct=90, missing=9, minutes=99),
        ]
        assert ids(rank(results)) == [
            "recipe_000",
            "recipe_001",
            "recipe_002",
            "recipe_003",
            "recipe_004",
        ]


# --------------------------------------------------------------------------- #
# Determinisme
# --------------------------------------------------------------------------- #


class TestDeterminism:
    def test_shuffled_input_same_output(self) -> None:
        results = [
            result(f"recipe_{i:03d}", pct=(i * 7) % 101, missing=i % 4, minutes=(i * 3) % 60)
            for i in range(30)
        ]
        expected = ids(rank(results))

        rng = random.Random(1234)
        for _ in range(5):
            shuffled = results[:]
            rng.shuffle(shuffled)
            assert ids(rank(shuffled)) == expected

    def test_repeated_rank_is_stable(self) -> None:
        results = [result("recipe_002"), result("recipe_001")]
        assert rank(results) == rank(results)


# --------------------------------------------------------------------------- #
# Immutability & tipe kembalian
# --------------------------------------------------------------------------- #


class TestPurity:
    def test_rank_does_not_mutate_input(self) -> None:
        results = [result("recipe_005"), result("recipe_002")]
        snapshot = list(results)
        rank(results)
        assert results == snapshot

    def test_all_functions_return_tuple(self) -> None:
        results = [result()]
        assert isinstance(rank(results), tuple)
        assert isinstance(filter_by_threshold(results, 0), tuple)
        assert isinstance(apply_limit(results, 1), tuple)

    def test_empty_input(self) -> None:
        assert rank([]) == ()
        assert filter_by_threshold([], 30) == ()
        assert apply_limit([], 5) == ()


# --------------------------------------------------------------------------- #
# Batas threshold & limit
# --------------------------------------------------------------------------- #


class TestBoundaries:
    def test_threshold_is_inclusive(self) -> None:
        """Nilai tepat di threshold tetap lolos."""
        assert ids(filter_by_threshold([result("recipe_a", pct=30)], 30)) == ["recipe_a"]

    def test_threshold_zero_keeps_everything(self) -> None:
        results = [result("recipe_a", pct=0), result("recipe_b", pct=100)]
        assert len(filter_by_threshold(results, 0)) == 2

    def test_threshold_above_100_removes_everything(self) -> None:
        assert filter_by_threshold([result(pct=100)], 101) == ()

    def test_limit_larger_than_results(self) -> None:
        results = [result("recipe_a"), result("recipe_b")]
        assert len(apply_limit(results, 10)) == 2

    def test_limit_zero_returns_empty(self) -> None:
        assert apply_limit([result()], 0) == ()

    def test_limit_negative_returns_empty(self) -> None:
        assert apply_limit([result()], -1) == ()

    def test_limit_one(self) -> None:
        results = rank([result("recipe_b", pct=60), result("recipe_a", pct=90)])
        assert ids(apply_limit(results, 1)) == ["recipe_a"]
