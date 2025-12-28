from __future__ import annotations

from collections.abc import Sequence
from typing import Union

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
    - Internally everything operates on ScoredSuggestion
    - Rankers never strip scores
    - Projection to Suggestion happens only at API boundaries
    - History has a single source of truth
    """

    def __init__(
        self,
        predictors: Sequence[Union[Predictor, WeightedPredictor]],
        ranker: Ranker | Sequence[Ranker] | None = None,
        history: History | None = None,
    ) -> None:
        # Normalize predictors at the boundary
        self._predictors: list[WeightedPredictor] = []
        for p in predictors:
            if isinstance(p, WeightedPredictor):
                self._predictors.append(p)
            else:
                self._predictors.append(
                    WeightedPredictor(predictor=p, weight=1.0)
                )

        # Normalize rankers to a list
        if ranker is None:
            self._rankers: list[Ranker] = [ScoreRanker()]
        elif isinstance(ranker, Ranker):
            self._rankers = [ranker]
        else:
            self._rankers = list(ranker)

        # Single source of truth for history
        if history is not None:
            self._history = history
        elif any(isinstance(r, LearnsFromHistory) for r in self._rankers):
            for r in self._rankers:
                if isinstance(r, LearnsFromHistory):
                    self._history = r.history
                    break
        else:
            self._history = History()

    # Predictors are the sole producers of ScoredSuggestion.
    # Engine aggregates, weights, and merges them.
    def _score(self, ctx: CompletionContext) -> list[ScoredSuggestion]:
        """
        Collect and aggregate scored suggestions from all predictors.

        Aggregation invariants:
        - Suggestions with identical values are merged
        - Scores are summed
        - Predictor weights are applied exactly once
        - Explanation is preserved from the first producer
        - Trace logs all contributions for debugging
        """
        aggregated: dict[str, ScoredSuggestion] = {}

        for weighted in self._predictors:
            results = weighted.predictor.predict(ctx)

            for scored in results:
                key = scored.suggestion.value
                weighted_score = scored.score * weighted.weight
                trace_entry = f"Predictor={weighted.predictor.__class__.__name__}, weight={weighted.weight}, raw_score={scored.score}"

                if key not in aggregated:
                    aggregated[key] = ScoredSuggestion(
                        suggestion=scored.suggestion,
                        score=weighted_score,
                        explanation=scored.explanation,
                        trace=[trace_entry],
                    )
                else:
                    prev = aggregated[key]
                    aggregated[key] = ScoredSuggestion(
                        suggestion=prev.suggestion,
                        score=prev.score + weighted_score,
                        explanation=prev.explanation,
                        trace=prev.trace + [trace_entry],
                    )

        return list(aggregated.values())

    def suggest(self, text: str) -> list[Suggestion]:
        """
        Public API: return ranked suggestions without scores for the given input.
        """
        ctx = CompletionContext(text)
        scored = self._score(ctx)
        for ranker in self._rankers:
            scored = ranker.rank(ctx.text, scored)
        return [s.suggestion for s in scored]

    def complete(self, ctx: CompletionContext) -> list[ScoredSuggestion]:
        """
        Lower-level API returning scored suggestions.
        """
        return self._score(ctx)

    def predict(self, ctx: CompletionContext) -> list[ScoredSuggestion]:
        """
        Backwards-compatible API used by invariant tests.
        """
        return self.complete(ctx)

    def explain(self, text: str) -> list[RankingExplanation]:
        """
        Public API: explain how suggestions were ranked.
        Aggregates explanations across all rankers.
        """
        ctx = CompletionContext(text)
        scored = self._score(ctx)
        aggregated: dict[str, RankingExplanation] = {}

        for ranker in self._rankers:
            for exp in ranker.explain(ctx.text, scored):
                if exp.value not in aggregated:
                    aggregated[exp.value] = exp
                else:
                    aggregated[exp.value].merge(exp)

        return list(aggregated.values())

    def explain_as_dicts(self, text: str) -> list[dict[str, float | str]]:
        """
        JSON-serializable explanation export for API consumers.
        """
        return [
            {
                "value": e.value,
                "base_score": e.base_score,
                "history_boost": e.history_boost,
                "final_score": e.final_score,
            }
            for e in self.explain(text)
        ]

    def record_selection(self, text: str, value: str) -> None:
        """
        Records user feedback for learning.
        """
        ctx = CompletionContext(text)
        self._history.record(ctx.text, value)

        for weighted in self._predictors:
            record = getattr(weighted.predictor, "record", None)
            if callable(record):
                record(ctx, value)

    def debug_pipeline(self, text: str) -> None:
        """
        Prints full prediction, ranking, and learning pipeline for debugging.
        """
        ctx = CompletionContext(text)
        scored = self._score(ctx)

        print("=== PREDICTION PHASE ===")
        for s in scored:
            print(f"{s.suggestion.value}: score={s.score:.2f}, trace={s.trace}")

        print("\n=== RANKING PHASE ===")
        for ranker in self._rankers:
            explanations = ranker.explain(ctx.text, scored)
            for e in explanations:
                print(
                    f"{e.value}: base={e.base_score:.2f}, "
                    f"history={e.history_boost:.2f}, final={e.final_score:.2f}, "
                    f"source={e.source}"
                )

    @property
    def history(self) -> History:
        """
        Read-only access to the engine's history.
        """
        return self._history
