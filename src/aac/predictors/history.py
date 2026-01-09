from __future__ import annotations

from aac.domain.history import History
from aac.domain.types import (
    CompletionContext,
    Predictor,
    PredictorExplanation,
    ScoredSuggestion,
    Suggestion,
    ensure_context,
)


class HistoryPredictor(Predictor):
    """
    Recall-based predictor driven by user selection history.

    Responsibility:
    - Introduces previously selected values as candidates
    - Does NOT perform ranking or dominance control
    - LearningRanker is responsible for ordering and preference shaping
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

    def record(self, ctx: CompletionContext | str, value: str) -> None:
        """
        Record user selection feedback for recall-based learning.
        """
        ctx = ensure_context(ctx)
        self._history.record(ctx.text, value)
