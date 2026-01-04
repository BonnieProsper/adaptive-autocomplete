from __future__ import annotations

from aac.domain.types import CompletionContext
from aac.engine import AutocompleteEngine


def debug_pipeline(engine: AutocompleteEngine, text: str) -> None:
    """
    Developer utility: prints the full autocomplete pipeline.

    Intentionally not part of the public engine API.
    It exists for CLI tooling, debugging, and inspection only.
    """
    ctx = CompletionContext(text)

    scored = engine._score(ctx)
    ranked = engine._apply_ranking(ctx, scored)

    print("=== PREDICTION PHASE ===")
    for s in scored:
        print(
            f"{s.suggestion.value}: "
            f"score={s.score:.2f}, "
            f"trace={s.trace}"
        )

    print("\n=== RANKING PHASE ===")
    for ranker in engine._rankers:
        for e in ranker.explain(ctx.text, ranked):
            print(
                f"{e.value}: "
                f"base={e.base_score:.2f}, "
                f"history={e.history_boost:.2f}, "
                f"final={e.final_score:.2f}, "
                f"source={e.source}"
            )
