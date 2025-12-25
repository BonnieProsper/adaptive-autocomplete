from __future__ import annotations

from collections.abc import Sequence

from aac.domain.history import History
from aac.domain.predictor import Predictor
from aac.domain.types import (
    CompletionContext,
    ScoredSuggestion,
    Suggestion,
    WeightedPredictor,
)
from aac.ranking.base import Ranker
from aac.ranking.contracts import LearnsFromHistory
from aac.ranking.explanation import RankingExplanation
from aac.ranking.score import ScoreRanker


class AutocompleteEngine:
    """
    Orchestrates prediction, ranking, learning, and explanation.

    Architectural invariants:
    - Engine owns the CompletionContext lifecycle
    - Internally, predictors are always WeightedPredictor
    - Predictors emit raw scores
    - Engine applies weights and merges results
    - History has a single source of truth
    """

    def __init__(
        self,
        predictors: Sequence[Predictor | WeightedPredictor],
        ranker: Ranker | None = None,
        history: History | None = None,
    ) -> None:
        # Normalize predictors once at the boundary
        self._predictors: list[WeightedPredictor] = []
        for p in predictors:
            if isinstance(p, WeightedPredictor):
                self._predictors.append(p)
            else:
                self._predictors.append(
                    WeightedPredictor(predictor=p, weight=1.0)
                )

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

        Aggregation invariants:
        - Suggestions with identical values are merged
        - Scores are summed
        - Predictor weights are applied here (and nowhere else)
        - Explanation is preserved from the first producer
        """
        aggregated: dict[str, ScoredSuggestion] = {}

        for weighted in self._predictors:
            results = weighted.predictor.predict(ctx)

            for scored in results:
                key = scored.suggestion.value
                weighted_score = scored.score * weighted.weight

                if key not in aggregated:
                    aggregated[key] = ScoredSuggestion(
                        suggestion=scored.suggestion,
                        score=weighted_score,
                        explanation=scored.explanation,
                    )
                else:
                    prev = aggregated[key]
                    aggregated[key] = ScoredSuggestion(
                        suggestion=prev.suggestion,
                        score=prev.score + weighted_score,
                        explanation=prev.explanation,
                    )

        return list(aggregated.values())

    def suggest(self, text: str) -> list[Suggestion]:
        """
        Public API: returns ranked suggestions only (no scores).
        """
        ctx = CompletionContext(text)
        scored = self._score(ctx)
        return self._ranker.rank(ctx.text, scored)

    def complete(self, ctx: CompletionContext) -> list[ScoredSuggestion]:
        """
        Lower-level API used by tests and internal consumers.
        """
        return self._score(ctx)

    def explain(self, text: str) -> list[RankingExplanation]:
        """
        Public API: returns explainability objects for the current input.
        """
        ctx = CompletionContext(text)
        scored = self._score(ctx)

        return self._ranker.explain(ctx.text, scored)


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

        for weighted in self._predictors:
            record = getattr(weighted.predictor, "record", None)
            if callable(record):
                record(ctx, value)
