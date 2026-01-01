from __future__ import annotations

import math
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
    Public entrypoint for the autocomplete system. 
    Only documented methods are considered stable.

    Architectural invariants:
    - Engine owns the CompletionContext lifecycle
    - Internally everything operates on ScoredSuggestion
    - Rankers must not add/remove suggestions
    - Scores must remain finite
    - Explanation final scores must reconcile with suggestion scores
    - Projection to Suggestion happens only at API boundaries
    - History has a single source of truth
    """

    def __init__(
        self,
        predictors: Sequence[Predictor | WeightedPredictor],
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
                trace_entry = (
                    f"Predictor={weighted.predictor.__class__.__name__}, "
                    f"weight={weighted.weight}, raw_score={scored.score}"
                )

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

    def _apply_ranking(
        self, ctx: CompletionContext, scored: list[ScoredSuggestion]
    ) -> list[ScoredSuggestion]:
        """
        Apply all rankers with enforced architectural invariants.
        """
        ranked = scored
        original_ids = {id(s) for s in ranked}

        for ranker in self._rankers:
            ranked = ranker.rank(ctx.text, ranked)

            # Invariant: rankers must not add/remove suggestions
            assert {id(s) for s in ranked} == original_ids, (
                f"Ranker {ranker.__class__.__name__} modified suggestion set"
            )

        # Invariant: scores must be finite
        for s in ranked:
            assert math.isfinite(s.score), (
                f"Non-finite score for '{s.suggestion.value}': {s.score}"
            )

        return ranked

    def suggest(self, text: str) -> list[Suggestion]:
        """
        Public API: return ranked suggestions without scores for the given input.
        """
        ctx = CompletionContext(text)
        scored = self._score(ctx)
        ranked = self._apply_ranking(ctx, scored)
        return [s.suggestion for s in ranked]

    def complete(self, ctx: CompletionContext) -> list[ScoredSuggestion]:
        """
        Lower-level API returning scored suggestions (no ranking).
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
        ranked = self._apply_ranking(ctx, scored)

        aggregated: dict[str, RankingExplanation] = {}

        for ranker in self._rankers:
            for exp in ranker.explain(ctx.text, ranked):
                if exp.value not in aggregated:
                    aggregated[exp.value] = exp
                else:
                    aggregated[exp.value].merge(exp)

        # preserve ranked order
        return [
            aggregated[s.suggestion.value]
            for s in ranked
            if s.suggestion.value in aggregated
        ]

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
        ranked = self._apply_ranking(ctx, scored)

        print("=== PREDICTION PHASE ===")
        for s in scored:
            print(
                f"{s.suggestion.value}: score={s.score:.2f}, trace={s.trace}"
            )

        print("\n=== RANKING PHASE ===")
        for ranker in self._rankers:
            explanations = ranker.explain(ctx.text, ranked)
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
