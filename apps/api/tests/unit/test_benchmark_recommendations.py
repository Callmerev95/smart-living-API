"""Test acceptance gate benchmark recommendation dataset nyata."""

from app.core.dependencies import get_recommendation_service


def test_benchmark_queries() -> None:
    service = get_recommendation_service()

    cases = (
        ("telur, ayam, wortel", 3, True, False),
        ("tahu, tempe, kecap", 3, False, False),
        ("nasi, telur, bawang putih", 3, False, False),
        ("telur", 1, False, False),
        ("kangkung, durian", 0, False, True),
    )

    for query, minimum_results, needs_score_spread, all_unknown in cases:
        result = service.recommend(query)
        assert len(result.results) >= minimum_results, query
        if needs_score_spread:
            assert len({item.match_percentage for item in result.results}) >= 2, query
        if all_unknown:
            assert result.results == ()
            assert result.unknown == ("kangkung", "durian")


def test_common_query_has_score_graduation() -> None:
    result = get_recommendation_service().recommend("telur, ayam, wortel")
    scores = {item.match_percentage for item in result.results}
    assert {100, 50, 40, 33} <= scores
