from __future__ import annotations

from time import perf_counter
from typing import Iterable

from aac.presets import create_engine


TEXTS = ["h", "he", "hel", "help", "hero", "hex"] * 10_000
WARMUP_TEXTS = ["h", "he", "hel"] * 1_000


def run_benchmark(name: str, texts: Iterable[str]) -> float:
    engine = create_engine(name)

    # Warm-up (stabilize caches, JIT paths, allocations)
    for t in WARMUP_TEXTS:
        engine.suggest(t)

    start = perf_counter()
    for t in texts:
        results = engine.suggest(t)

        # Prevent accidental dead-code elimination assumptions
        if not results:
            raise RuntimeError("Unexpected empty suggestions")

    elapsed = perf_counter() - start
    return elapsed


def main() -> None:
    presets = ["stateless", "default", "recency"]

    print(f"Benchmarking {len(TEXTS):,} suggest calls\n")

    for name in presets:
        elapsed = run_benchmark(name, TEXTS)
        avg_us = (elapsed / len(TEXTS)) * 1e6

        print(f"{name:10s} | total: {elapsed:6.3f}s | avg: {avg_us:7.2f} µs")


if __name__ == "__main__":
    main()
