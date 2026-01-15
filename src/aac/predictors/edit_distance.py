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


def levenshtein(a: str, b: str) -> int:
    """
    Compute Levenshtein edit distance using a space-optimized DP.

    Cost model:
    - insertion: 1
    - deletion: 1
    - substitution: 1
    """
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)

    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        curr = [i]
        for j, cb in enumerate(b, start=1):
            cost = 0 if ca == cb else 1
            curr.append(
                min(
                    prev[j] + 1,        # deletion
                    curr[j - 1] + 1,    # insertion
                    prev[j - 1] + cost  # substitution
                )
            )
        prev = curr

    return prev[-1]


class EditDistancePredictor(Predictor):
    """
    Error-tolerant predictor using edit distance.

    Intended for:
    - typos
    - near-misses
    - recovery from incorrect prefixes

    Emits a weak signal that should be combined
    with stronger predictors and rankers.
    """

    name = "edit_distance"

    def __init__(
        self,
        vocabulary: Iterable[str],
        *,
        max_distance: int = 2,
        base_score: float = 1.0,
    ) -> None:
        self._vocabulary = tuple(vocabulary)
        self._max_distance = max_distance
        self._base_score = base_score

    def predict(self, ctx: CompletionContext | str) -> list[ScoredSuggestion]:
        ctx = ensure_context(ctx)
        prefix = ctx.prefix()

        if not prefix:
            return []

        results: list[ScoredSuggestion] = []

        for word in self._vocabulary:
            distance = levenshtein(prefix, word)

            if distance > self._max_distance:
                continue

            # Penalize by distance
            score = self._base_score / (1 + distance)

            # Confidence decays sharply with distance
            confidence = max(0.0, 1.0 - (distance / (self._max_distance + 1)))

            results.append(
                ScoredSuggestion(
                    suggestion=Suggestion(value=word),
                    score=score,
                    explanation=PredictorExplanation(
                        value=word,
                        score=score,
                        source=self.name,
                        confidence=confidence,
                    ),
                )
            )

        return results
