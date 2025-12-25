from collections.abc import Iterable

from aac.domain.types import ScoredSuggestion
from aac.ranking.base import Ranker
from aac.ranking.explanation import RankingExplanation


class ScoreRanker(Ranker):
    """
    Pure score-based ranker.

    - No mutation
    - Stable
    - Deterministic
    - Idempotent
    """

    def rank(
        self,
        prefix: str,
        suggestions: Iterable[ScoredSuggestion],
    ) -> list[ScoredSuggestion]:
        # Defensive copy to preserve idempotence
        return sorted(
            suggestions,
            key=lambda s: s.score,
            reverse=True,
        )

    def explain(
        self,
        prefix: str,
        suggestions: Iterable[ScoredSuggestion],
    ) -> list[RankingExplanation]:
        ordered = self.rank(prefix, suggestions)

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
    suggestions: Iterable[ScoredSuggestion],
) -> list[ScoredSuggestion]:
    """
    Pure functional helper used by ranking invariant tests.
    """
    return ScoreRanker().rank("", suggestions)
