# TODO: fix source = source behaviour, suggest() hides scores

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import TypedDict

from aac.domain.history import History
from aac.domain.types import (
    CompletionContext,
    Predictor,
    ScoredSuggestion,
    Suggestion,
    WeightedPredictor,
)
from aac.ranking.base import Ranker
from aac.ranking.contracts import LearnsFromHistory
from aac.ranking.explanation import RankingExplanation
from aac.ranking.score import ScoreRanker


class DebugState(TypedDict):
    input: str
    scored: list[ScoredSuggestion]
    ranked: list[ScoredSuggestion]
    suggestions: list[str]


class AutocompleteEngine:
    """
    Orchestrates prediction, ranking, learning, and explanation.

    Public entrypoint for the autocomplete system.
    Only documented methods are considered stable.

    Architectural invariants:
    - Engine owns the CompletionContext lifecycle
    - Internally everything operates on ScoredSuggestion
    - Rankers must not add or remove suggestions
    - Scores must remain finite
    - Explanation final scores must reconcile with ranking scores
    - Projection to Suggestion happens only at API boundaries
    - History has a single source of truth
    """

    def __init__(
        self,
        predictors: Sequence[Predictor | WeightedPredictor],
        ranker: Ranker | Sequence[Ranker] | None = None,
        history: History | None = None,
    ) -> None:
        # Normalize predictors
        self._predictors: list[WeightedPredictor] = []
        for p in predictors:
            if isinstance(p, WeightedPredictor):
                self._predictors.append(p)
            else:
                self._predictors.append(
                    WeightedPredictor(predictor=p, weight=1.0)
                )

        # Normalize rankers
        if ranker is None:
            self._rankers: list[Ranker] = [ScoreRanker()]
        elif isinstance(ranker, Ranker):
            self._rankers = [ranker]
        else:
            self._rankers = list(ranker)

        # Resolve history source of truth
        if history is not None:
            self._history = history
        elif any(isinstance(r, LearnsFromHistory) for r in self._rankers):
            for r in self._rankers:
                if isinstance(r, LearnsFromHistory):
                    self._history = r.history
                    break
        else:
            self._history = History()

    # ------------------------------------------------------------------
    # Core pipeline
    # ------------------------------------------------------------------

    def _score(self, ctx: CompletionContext) -> list[ScoredSuggestion]:
        """
        Collect and aggregate scored suggestions from all predictors.
        """
        aggregated: dict[str, ScoredSuggestion] = {}

        for weighted in self._predictors:
            results = weighted.predictor.predict(ctx)

            for scored in results:
                key = scored.suggestion.value
                weighted_score = scored.score * weighted.weight

                trace_entry = (
                    f"Predictor={weighted.predictor.name}, "
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
        self,
        ctx: CompletionContext,
        scored: list[ScoredSuggestion],
    ) -> list[ScoredSuggestion]:
        """
        Apply rankers while enforcing invariants.
        """
        ranked = scored
        original_ids = {id(s) for s in ranked}

        for ranker in self._rankers:
            ranked = ranker.rank(ctx.text, ranked)

            assert {id(s) for s in ranked} == original_ids, (
                f"Ranker {ranker.__class__.__name__} modified suggestion set"
            )

        for s in ranked:
            assert math.isfinite(s.score), (
                f"Non-finite score for '{s.suggestion.value}': {s.score}"
            )

        return ranked

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def suggest(self, text: str) -> list[Suggestion]:
        """
        Return ranked suggestions for user-facing consumption.

        Note:
            This API intentionally hides scores and explanations.
            Use explain() or debug() for introspection.
        """
        ctx = CompletionContext(text)
        ranked = self._apply_ranking(ctx, self._score(ctx))
        return [s.suggestion for s in ranked]

    def predict_scored(self, ctx: CompletionContext) -> list[ScoredSuggestion]:
        return self._score(ctx)

    # ------------------------------------------------------------------
    # Explanation
    # ------------------------------------------------------------------

    def explain(self, text: str) -> list[RankingExplanation]:
        ctx = CompletionContext(text)
        scored = self._score(ctx)
        ranked = self._apply_ranking(ctx, scored)

        aggregated: dict[str, RankingExplanation] = {}

        for ranker in self._rankers:
            for exp in ranker.explain(ctx.text, ranked):
                if exp.value not in aggregated:
                    aggregated[exp.value] = exp
                else:
                    # Multiple rankers may contribute partial explanations.
                    # merge them into a single per-suggestion explanation.
                    aggregated[exp.value] = aggregated[exp.value].merge(exp)

        return [
            aggregated[s.suggestion.value]
            for s in ranked
            if s.suggestion.value in aggregated
        ]

    def explain_as_dicts(self, text: str) -> list[dict[str, float | str]]:
        return [
            {
                "value": e.value,
                "base_score": e.base_score,
                "history_boost": e.history_boost,
                "final_score": e.final_score,
            }
            for e in self.explain(text)
        ]

    # ------------------------------------------------------------------
    # Learning
    # ------------------------------------------------------------------

    def record_selection(self, text: str, value: str) -> None:
        ctx = CompletionContext(text)
        self._history.record(ctx.text, value)

        for weighted in self._predictors:
            record = getattr(weighted.predictor, "record", None)
            if callable(record):
                record(ctx, value)

    # ------------------------------------------------------------------
    # Developer/debug API (INTENTIONALLY UNSTABLE)
    # ------------------------------------------------------------------

    def debug(self, text: str) -> DebugState:
        """
        Developer-only debug surface.

        Returns internal pipeline state for inspection.
        NOT a stable API.
        Returns:
            dict with keys: input, scored, ranked, suggestions
        """
        ctx = CompletionContext(text)
        scored = self._score(ctx)
        ranked = self._apply_ranking(ctx, scored)

        return {
            "input": text,
            "scored": scored,
            "ranked": ranked,
            "suggestions": [s.suggestion.value for s in ranked],
        }

    # ------------------------------------------------------------------

    @property
    def history(self) -> History:
        return self._history
