from collections.abc import Sequence

from aac.domain.types import ScoredSuggestion, Suggestion
from aac.ranking.base import Ranker
from aac.ranking.explanation import RankingExplanation


class ScoreRanker(Ranker):
    """
    Pure score-based ranker.
    No learning or mutation and stable ordering.
    """

    def rank(
        self,
        text: str,
        scored: Sequence[ScoredSuggestion],
    ) -> list[Suggestion]:
        if not scored:
            return []

        ordered = sorted(
            scored,
            key=lambda s: s.score,
            reverse=True,
        )

        return [s.suggestion for s in ordered]

    def explain(
        self,
        text: str,
        scored: Sequence[ScoredSuggestion],
    ) -> list[RankingExplanation]:
        if not scored:
            return []

        ordered = sorted(
            scored,
            key=lambda s: s.score,
            reverse=True,
        )

        return [
            RankingExplanation(
                value=s.suggestion.value,
                base_score=s.score,
                history_boost=0.0,
                final_score=s.score,
                source="score",
            )
            for s in ordered
        ]


def score_and_rank(
    prefix: str,
    suggestions: Sequence[ScoredSuggestion],
) -> list[Suggestion]:
    """
    Pure functional ranking helper used by tests.
    """
    return ScoreRanker().rank(prefix, suggestions)
