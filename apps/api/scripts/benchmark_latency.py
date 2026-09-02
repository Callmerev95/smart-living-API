#!/usr/bin/env python
"""Benchmark latency endpoint recommendations.

Target PRD §14 dan `docs/technical-architecture.md` §19: p50 < 200 ms, p95 < 500 ms
pada environment lokal. Angka harus diukur, bukan diasumsikan.

Pemakaian:
    uv run python scripts/benchmark_latency.py
    uv run python scripts/benchmark_latency.py --requests 500
"""

import argparse
import logging
import statistics
import time

from fastapi.testclient import TestClient

from app.main import create_app

# Input bervariasi: jumlah bahan berbeda, ada yang tak dikenal, ada yang kosong hasil.
PAYLOADS = (
    {"ingredients": ["telur", "ayam", "wortel"]},
    {"ingredients": ["tahu", "tempe", "kecap"]},
    {"ingredients": ["nasi", "telur", "bawang putih"], "limit": 10},
    {"ingredients": ["telur"]},
    {"ingredients": ["udang", "cabai", "petai", "tomat", "bawang merah"]},
    {"ingredients": ["daging sapi", "kentang", "kecap", "kangkung"]},
    {"ingredients": ["2 butir telur", "100 gr ayam", "1/2 wortel"]},
)

TARGET_P50_MS = 200.0
TARGET_P95_MS = 500.0


def percentile(sorted_values: list[float], fraction: float) -> float:
    """Persentil dengan interpolasi linear."""
    if not sorted_values:
        return 0.0
    if len(sorted_values) == 1:
        return sorted_values[0]

    position = fraction * (len(sorted_values) - 1)
    lower = int(position)
    upper = min(lower + 1, len(sorted_values) - 1)
    weight = position - lower
    return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight


def main() -> int:
    parser = argparse.ArgumentParser(description="Ukur latency POST /api/v1/recommendations.")
    parser.add_argument("--requests", type=int, default=200, help="jumlah request diukur")
    parser.add_argument("--warmup", type=int, default=20, help="request pemanasan (tidak diukur)")
    args = parser.parse_args()

    # Log per-request akan mendistorsi pengukuran.
    logging.disable(logging.CRITICAL)

    client = TestClient(create_app())

    # Warm-up: request pertama memuat dataset dan membangun alias map.
    for index in range(args.warmup):
        client.post("/api/v1/recommendations", json=PAYLOADS[index % len(PAYLOADS)])

    durations: list[float] = []
    for index in range(args.requests):
        payload = PAYLOADS[index % len(PAYLOADS)]
        started = time.perf_counter()
        response = client.post("/api/v1/recommendations", json=payload)
        durations.append((time.perf_counter() - started) * 1000)

        if response.status_code != 200:
            logging.disable(logging.NOTSET)
            print(f"FAIL — status {response.status_code} pada request ke-{index + 1}")
            return 1

    logging.disable(logging.NOTSET)
    durations.sort()

    p50 = percentile(durations, 0.50)
    p95 = percentile(durations, 0.95)
    p99 = percentile(durations, 0.99)

    print("Benchmark POST /api/v1/recommendations")
    print(f"Requests   : {args.requests} (warm-up {args.warmup})")
    print(f"min        : {durations[0]:.2f} ms")
    print(f"p50        : {p50:.2f} ms   (target < {TARGET_P50_MS:.0f} ms)")
    print(f"p95        : {p95:.2f} ms   (target < {TARGET_P95_MS:.0f} ms)")
    print(f"p99        : {p99:.2f} ms")
    print(f"max        : {durations[-1]:.2f} ms")
    print(f"mean       : {statistics.fmean(durations):.2f} ms")
    print()

    p50_ok = p50 < TARGET_P50_MS
    p95_ok = p95 < TARGET_P95_MS
    print(f"p50 target : {'OK' if p50_ok else 'GAGAL'}")
    print(f"p95 target : {'OK' if p95_ok else 'GAGAL'}")

    if not (p50_ok and p95_ok):
        print()
        print("Petunjuk: bila p95 gagal, periksa apakah dataset di-load ulang per request")
        print("(pelanggaran T-P3-13 composition root).")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
