from __future__ import annotations

from collections.abc import Iterable

from aac.domain.types import (
    CompletionContext,
    Predictor,
    PredictorExplanation,
    ScoredSuggestion,
    Suggestion,
    ensure_context,
)


class StaticPrefixPredictor(Predictor):
    """
    Deterministic prefix-based predictor.

    Performs a static prefix match against a fixed vocabulary.
    Emits neutral scores; ranking is handled downstream.
    """

    name: str = "static_prefix"

    def __init__(self, vocabulary: Iterable[str]) -> None:
        # Preserve order, remove duplicates
        self._vocabulary: tuple[str, ...] = tuple(dict.fromkeys(vocabulary))

    def predict(self, ctx: CompletionContext | str) -> list[ScoredSuggestion]:
        ctx = ensure_context(ctx)
        prefix = ctx.prefix()

        if not prefix:
            return []

        results: list[ScoredSuggestion] = []

        for word in self._vocabulary:
            # Do not repeat exact matches
            if word == prefix:
                continue

            if not word.startswith(prefix):
                continue

            results.append(
                ScoredSuggestion(
                    suggestion=Suggestion(value=word),
                    score=1.0,
                    explanation=PredictorExplanation(
                        value=word,
                        score=1.0,
                        source=self.name,
                    ),
                    trace=[
                        f"prefix='{prefix}'",
                        f"matched='{word}'",
                        "score=1.0",
                    ],
                )
            )

        return results
