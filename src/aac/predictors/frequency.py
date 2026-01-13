from __future__ import annotations

from aac.domain.types import (
    CompletionContext,
    Predictor,
    PredictorExplanation,
    ScoredSuggestion,
    Suggestion,
    ensure_context,
)


class FrequencyPredictor(Predictor):
    """
    Suggests words based on observed global frequency.

    Confidence is derived from normalized frequency.
    """

    name = "frequency"

    def __init__(self, frequencies: dict[str, int]) -> None:
        if not frequencies:
            raise ValueError("frequencies must not be empty")

        self._frequencies = dict(frequencies)
        self._max_freq = max(frequencies.values())

    def predict(self, ctx: CompletionContext | str) -> list[ScoredSuggestion]:
        ctx = ensure_context(ctx)
        token = ctx.prefix()

        if not token:
            return []

        results: list[ScoredSuggestion] = []

        for word, count in self._frequencies.items():
            if not word.startswith(token):
                continue

            confidence = count / self._max_freq
            score = float(count)

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
