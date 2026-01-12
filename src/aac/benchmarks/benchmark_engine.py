from time import perf_counter

from aac.presets import create_engine


TEXTS = [
    "h", "he", "hel", "help", "hero", "hex"
] * 10_000


def main() -> None:
    engine = create_engine("developer")

    start = perf_counter()
    for text in TEXTS:
        engine.suggest(text)
    elapsed = perf_counter() - start

    print(f"Total time: {elapsed:.3f}s")
    print(f"Avg per suggest: {(elapsed / len(TEXTS)) * 1e6:.2f} µs")


if __name__ == "__main__":
    main()
