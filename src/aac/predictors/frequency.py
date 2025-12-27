from __future__ import annotations

from aac.domain.predictor import Predictor
from aac.domain.types import (
    CompletionContext,
    PredictorExplanation,
    ScoredSuggestion,
    Suggestion,
    ensure_context,
)


class FrequencyPredictor(Predictor):
    """
    Suggests words based on observed global frequency.
    """
    name = "frequency"

    def __init__(self, frequencies: dict[str, int]) -> None:
        self._freq = dict(frequencies)

    def predict(self, ctx: CompletionContext | str) -> list[ScoredSuggestion]:
        ctx = ensure_context(ctx)

        token = ctx.text.rstrip().split()[-1] if ctx.text else ""
        if not token:
            return []

        results: list[ScoredSuggestion] = []

        for word, count in self._freq.items():
            if word.startswith(token):
                score = float(count)

                results.append(
                    ScoredSuggestion(
                        suggestion=Suggestion(value=word),
                        score=score,
                        explanation=PredictorExplanation(
                            value=word,
                            score=score,
                            source=self.name,
                        ),
                    )
                )

        return results
