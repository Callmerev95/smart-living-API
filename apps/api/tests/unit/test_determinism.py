"""Test determinisme — klaim inti produk.

PRD §14 (Reliability) dan `docs/technical-architecture.md` §8.5: input dan dataset
yang sama selalu menghasilkan hasil yang sama. Diuji terhadap dataset NYATA (60 resep),
bukan fixture kecil.

Bila test ini gagal, penyebab hampir pasti iterasi `set`/`dict` yang bocor ke urutan
output — bukan masalah formula.
"""

import random

import pytest

from app.core.config import Settings
from app.core.dependencies import build_recommendation_service

SETTINGS = Settings(_env_file=None)  # type: ignore[call-arg]

QUERIES = [
    "telur, ayam, wortel",
    "tahu, tempe, kecap",
    "nasi, telur, bawang putih",
    "udang, cabai, petai",
    "ikan, kunyit, bawang merah",
    "mie, kol, wortel, telur",
    "daging sapi, kentang, kecap",
    "telur",
]


@pytest.fixture(scope="module")
def service():
    return build_recommendation_service(SETTINGS)


def _signature(results: tuple) -> tuple:
    """Buat representasi hasil yang sensitif terhadap urutan, bukan hash."""
    return tuple(
        (
            result.recipe_id,
            result.match_percentage,
            result.available_ingredients,
            result.missing_ingredients,
            result.cooking_time_minutes,
        )
        for result in results
    )


class TestDeterminism:
    @pytest.mark.parametrize("query", QUERIES)
    def test_repeated_runs_identical(self, service, query: str) -> None:
        baselines = [service.recommend(query) for _ in range(5)]
        for run in baselines[1:]:
            assert _signature(run.results) == _signature(baselines[0].results)
            assert run.canonical == baselines[0].canonical
            assert run.unknown == baselines[0].unknown

    @pytest.mark.parametrize("query", QUERIES)
    def test_shuffled_user_input_same_ranking(self, service, query: str) -> None:
        base = service.recommend(query)
        base_ids = [r.recipe_id for r in base.results]

        tokens = query.split(", ")
        for seed in range(5):
            shuffled = tokens[:]
            random.Random(seed).shuffle(shuffled)
            variant = service.recommend(", ".join(shuffled))
            assert [r.recipe_id for r in variant.results] == base_ids

    def test_shuffled_recipe_order_same_ranking(self) -> None:
        """Urutan resep di repository tidak boleh memengaruhi ranking."""
        repo = build_recommendation_service(SETTINGS)
        base = repo.recommend("telur, ayam, wortel")
        base_ids = [r.recipe_id for r in base.results]

        recipes = repo._recipe_repository.get_all()  # noqa: SLF001
        for seed in (7, 42, 2024):
            shuffled = list(recipes)
            random.Random(seed).shuffle(shuffled)
            variant = build_recommendation_service(SETTINGS)
            object.__setattr__(variant._recipe_repository, "_recipes", tuple(shuffled))  # noqa: SLF001
            assert [
                r.recipe_id for r in variant.recommend("telur, ayam, wortel").results
            ] == base_ids

    def test_internal_arrays_also_deterministic(self, service) -> None:
        """Determinisme tidak cukup pada id — urutan array di dalamnya pun harus sama."""
        first = service.recommend("telur, ayam, wortel")
        second = service.recommend("telur, ayam, wortel")
        assert _signature(first.results) == _signature(second.results)
