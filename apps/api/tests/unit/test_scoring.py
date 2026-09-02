"""Test untuk `domain/matching/scoring`.

Berisi seluruh 8 test case wajib `docs/content-schema.md` §A.5.5.
"""

import pytest

from app.domain.matching.scoring import calculate_match_percentage


class TestCalculateMatchPercentage:
    @pytest.mark.parametrize(
        "matched, denominator, expected",
        [
            # docs/content-schema.md §A.5.5
            (3, 4, 75),  # case 1: 3/4
            (3, 3, 100),  # case 2: 3/3
            (0, 3, 0),  # case 3: 0/3
            (2, 2, 100),  # case 4 (Delta 1): 2/2 excludes staple
            (1, 2, 50),  # case 5 (Delta 1): 1/2
            (3, 3, 100),  # case 6: 3/3
            (3, 3, 100),  # case 7: 3/3
            (0, 0, 0),  # case 8: guard divide-by-zero
            # pembulatan half-up
            (2, 3, 67),  # 2/3 -> 66.67 -> 67
            (1, 3, 33),  # 1/3 -> 33.33 -> 33
            (1, 2, 50),  # 1/2 -> 50.0 -> 50
            (1, 8, 13),  # 1/8 -> 12.5 -> 13 (half-up, bukan banker's 12)
            (3, 8, 38),  # 3/8 -> 37.5 -> 38
            (5, 8, 63),  # 5/8 -> 62.5 -> 63
            (7, 8, 88),  # 7/8 -> 87.5 -> 88
            # batas
            (0, 1, 0),  # 0/1
            (1, 1, 100),  # 1/1
            (100, 100, 100),  # 100/100
        ],
    )
    def test_cases(self, matched: int, denominator: int, expected: int) -> None:
        assert calculate_match_percentage(matched, denominator) == expected

    def test_denominator_zero_returns_zero(self) -> None:
        assert calculate_match_percentage(0, 0) == 0
        assert calculate_match_percentage(5, 0) == 0

    def test_matched_negative_safe(self) -> None:
        """Guard: pemanggil seharusnya tidak pernah kirim negatif, tapi aman."""
        assert calculate_match_percentage(-1, 5) == 0

    def test_denominator_negative_safe(self) -> None:
        assert calculate_match_percentage(3, -1) == 0

    def test_clamp_100(self) -> None:
        """Matched bisa melebihi denominator bila ada bug — clamp ke 100."""
        assert calculate_match_percentage(5, 3) == 100

    def test_returns_int(self) -> None:
        assert isinstance(calculate_match_percentage(3, 4), int)
