from __future__ import annotations

from aac.domain.history import History
from aac.domain.predictor import Predictor
from aac.domain.types import (
    CompletionContext,
    PredictorExplanation,
    ScoredSuggestion,
    Suggestion,
    ensure_context,
)


class HistoryPredictor(Predictor):
    """
    Suggests words based on user selection history.
    """
    name = "history"

    def __init__(self, history: History, weight: float = 1.0) -> None:
        self._history = history
        self._weight = weight

    def predict(self, ctx: CompletionContext | str) -> list[ScoredSuggestion]:
        ctx = ensure_context(ctx)
        token = ctx.text.rstrip().split()[-1] if ctx.text else ""
        if not token:
            return []

        counts = self._history.counts_for_prefix(token)
        if not counts:
            return []

        results: list[ScoredSuggestion] = []

        for value, count in counts.items():
            score = float(count) * self._weight

            results.append(
                ScoredSuggestion(
                    suggestion=Suggestion(value=value),
                    score=score,
                    explanation=PredictorExplanation(
                        value=value,
                        score=score,
                        source=self.name,
                    ),
                )
            )

        return results

    def record(self, prefix: str, value: str) -> None:
        self._history.record(prefix, value)
