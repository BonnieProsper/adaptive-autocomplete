from __future__ import annotations

from aac.domain.history import History
from aac.domain.predictor import Predictor
from aac.domain.types import CompletionContext, ScoredSuggestion, Suggestion, ensure_context
from aac.ranking.explanation import RankingExplanation


class HistoryPredictor(Predictor):
    def __init__(self, history: History, weight: float = 1.0) -> None:
        self._history = history
        self._weight = weight

    
    @property
    def name(self) -> str:
        return "history"


    def predict(self, ctx: CompletionContext | str) -> list[ScoredSuggestion]:
        ctx = ensure_context(ctx) 
        text = ctx.text
        if not text:
            return []

        counts = self._history.counts_for_prefix(text)
        if not counts:
            return []

        results: list[ScoredSuggestion] = []

        for value, count in counts.items():
            score = count * self._weight

            results.append(
                ScoredSuggestion(
                    suggestion=Suggestion(value),
                    score=score,
                    explanation=RankingExplanation.base(
                        value=value,
                        score=1.0,
                        source=self.name,
                    ),
                )
            )

        return results

    def record(self, prefix: str, value: str) -> None:
        self._history.record(prefix, value)
