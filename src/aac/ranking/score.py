from __future__ import annotations

from aac.domain.types import ScoredSuggestion, Suggestion
from aac.ranking.base import Ranker
from aac.ranking.explanation import RankingExplanation


class ScoreRanker(Ranker):
    """
    Ranks suggestions by descending score.
    """

    def rank(
        self,
        text: str,
        scored: list[ScoredSuggestion],
    ) -> list[Suggestion]:
        ordered = sorted(scored, key=lambda s: s.score, reverse=True)
        return [s.suggestion for s in ordered]

    def explain(
        self,
        text: str,
        scored: list[ScoredSuggestion],
    ) -> list[RankingExplanation]:
        """
        ScoreRanker does not apply learning;
        explanation reflects raw predictor scores.
        """
        ordered = sorted(scored, key=lambda s: s.score, reverse=True)

        explanations: list[RankingExplanation] = []

        for s in ordered:
            explanations.append(
                RankingExplanation(
                    value=s.suggestion.value,
                    base_score=s.score,
                    history_boost=0.0,
                    final_score=s.score,
                    source="score",
                )
            )

        return explanations
