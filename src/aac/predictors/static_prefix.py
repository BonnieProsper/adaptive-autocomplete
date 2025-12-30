from __future__ import annotations

from collections.abc import Iterable

from aac.domain.predictor import Predictor
from aac.domain.types import (
    CompletionContext,
    PredictorExplanation,
    ScoredSuggestion,
    Suggestion,
    ensure_context,
)


class StaticPrefixPredictor(Predictor):
    """
    Deterministic prefix-based predictor over a static vocabulary.

    Design goals:
    - Uses CompletionContext.prefix() as the single source of truth
    - Emits proportional base scores (longer prefix match = stronger signal)
    - Produces stable, explainable output
    - Does not perform ranking or normalization
    """

    name: str = "static_prefix"

    def __init__(self, vocabulary: Iterable[str]) -> None:
        # Preserve insertion order, remove duplicates
        self._vocabulary: tuple[str, ...] = tuple(dict.fromkeys(vocabulary))

    def predict(self, ctx: CompletionContext | str) -> list[ScoredSuggestion]:
        ctx = ensure_context(ctx)
        prefix = ctx.prefix()

        if not prefix:
            return []

        results: list[ScoredSuggestion] = []

        for word in self._vocabulary:
            if word == prefix:
                continue

            if not word.startswith(prefix):
                continue

            # Signal strength increases with prefix length
            score = len(prefix) / len(word)

            results.append(
                ScoredSuggestion(
                    suggestion=Suggestion(value=word),
                    score=score,
                    explanation=PredictorExplanation(
                        value=word,
                        score=score,
                        source=self.name,
                    ),
                    trace=[
                        f"prefix='{prefix}'",
                        f"matched='{word}'",
                        f"score={score:.3f}",
                    ],
                )
            )

        return results
