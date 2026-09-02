#!/usr/bin/env python
"""Benchmark manual kualitas recommendation terhadap dataset nyata.

Menjalankan lima query wajib dari `docs/development-roadmap.md` §4.5.
Script mencetak laporan untuk review relevansi manusia; bukan pengganti unit test.

Pemakaian:
    uv run python scripts/benchmark_recommendations.py
"""

from app.core.dependencies import get_recommendation_service

QUERIES = (
    "telur, ayam, wortel",
    "tahu, tempe, kecap",
    "nasi, telur, bawang putih",
    "telur",
    "kangkung, durian",
)


def main() -> int:
    service = get_recommendation_service()

    print("Smart Living recommendation benchmark")
    print(f"Dataset: {service._recipe_repository.count()} recipes")  # noqa: SLF001
    print()

    for query in QUERIES:
        result = service.recommend(query)
        print(f"Input: {query}")
        print(f"Canonical: {', '.join(result.canonical) or '-'}")
        print(f"Unknown: {', '.join(result.unknown) or '-'}")
        print(f"Results above threshold: {len(result.results)}")

        if result.results:
            scores = ", ".join(str(item.match_percentage) for item in result.results)
            print(f"Top {len(result.results)} scores: {scores}")
            for item in result.results:
                print(f"  {item.match_percentage:>3}% {item.recipe_id}")
        else:
            print("  (empty)")
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
