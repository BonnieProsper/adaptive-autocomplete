from __future__ import annotations

from collections.abc import Sequence

from aac.domain.history import History
from aac.domain.predictor import Predictor
from aac.domain.types import CompletionContext, ScoredSuggestion, Suggestion
from aac.ranking.base import Ranker
from aac.ranking.contracts import LearnsFromHistory
from aac.ranking.explanation import RankingExplanation
from aac.ranking.score import ScoreRanker


class AutocompleteEngine:
    """
    Orchestrates prediction, ranking, learning, and explanation.

    Architectural invariants:
    - Engine owns the CompletionContext lifecycle
    - Predictors produce ScoredSuggestions
    - Rankers order suggestions and may learn from history
    - History has a single source of truth
    """

    def __init__(
        self,
        predictors: Sequence[Predictor],
        ranker: Ranker | None = None,
        history: History | None = None,
    ) -> None:
        self._predictors = list(predictors)
        self._ranker = ranker or ScoreRanker()

        # SINGLE SOURCE OF TRUTH FOR HISTORY
        if history is not None:
            self._history = history
        elif isinstance(self._ranker, LearnsFromHistory):
            self._history = self._ranker.history
        else:
            self._history = History()

    def _score(self, ctx: CompletionContext) -> list[ScoredSuggestion]:
        """
        Collects and aggregates scored suggestions from all predictors.

        Aggregation rule:
        - Same suggestion value → scores are summed
        - Explanation is preserved from the first producer
        """
        aggregated: dict[str, ScoredSuggestion] = {}

        for predictor in self._predictors:
            predictions = predictor.predict(ctx)

            for scored in predictions:
                key = scored.suggestion.value

                if key not in aggregated:
                    aggregated[key] = scored
                else:
                    prev = aggregated[key]
                    aggregated[key] = ScoredSuggestion(
                        suggestion=prev.suggestion,
                        score=prev.score + scored.score,
                        explanation=prev.explanation,
                    )

        return list(aggregated.values())

    def suggest(self, text: str) -> list[Suggestion]:
        """
        Public API: returns ranked suggestions only (no scores).
        """
        ctx = CompletionContext(text)
        scored = self._score(ctx)
        return self._ranker.rank(ctx, scored)

    def explain(self, text: str) -> list[RankingExplanation]:
        """
        Public API: returns explainability objects for the current input.
        """
        ctx = CompletionContext(text)
        scored = self._score(ctx)

        return [
            item.explanation
            for item in scored
            if item.explanation is not None
        ]

    def record_selection(self, text: str, value: str) -> None:
        """
        Records user feedback and propagates learning.

        Learning rules:
        - History is always updated
        - Predictors may optionally learn
        - Rankers that learn from history are updated implicitly
        """
        ctx = CompletionContext(text)
        self._history.record(ctx.text, value)

        for predictor in self._predictors:
            record = getattr(predictor, "record", None)
            if callable(record):
                record(ctx, value)
