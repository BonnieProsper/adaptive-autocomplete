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

    Emits candidates previously selected by the user.
    """

    name = "history"

    def __init__(self, history: History) -> None:
        self._history = history

    def predict(self, ctx: CompletionContext | str) -> list[ScoredSuggestion]:
        ctx = ensure_context(ctx)
        prefix = ctx.prefix()

        if not prefix:
            return []

        counts = self._history.counts_for_prefix(prefix)
        if not counts:
            return []

        max_count = max(counts.values())
        results: list[ScoredSuggestion] = []

        for value, count in counts.items():
            confidence = count / max_count
            score = float(count)

            results.append(
                ScoredSuggestion(
                    suggestion=Suggestion(value=value),
                    score=score,
                    explanation=PredictorExplanation(
                        value=value,
                        score=score,
                        source=self.name,
                        confidence=confidence,
                    ),
                )
            )

        return results

    def record(self, ctx: CompletionContext | str, value: str) -> None:
        ctx = ensure_context(ctx)
        self._history.record(ctx.text, value)
