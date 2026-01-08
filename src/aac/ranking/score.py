from collections.abc import Sequence

from aac.domain.types import ScoredSuggestion
from aac.ranking.base import Ranker
from aac.ranking.explanation import RankingExplanation


class ScoreRanker(Ranker):
    """
    Pure score-based ranker.

    Invariants:
    - Deterministic
    - Stable
    - Non-mutating
    - Idempotent
    """

    def rank(
        self,
        prefix: str,
        suggestions: Sequence[ScoredSuggestion],
    ) -> list[ScoredSuggestion]:
        # Defensive copy via sorted()
        return sorted(
            suggestions,
            key=lambda s: s.score,
            reverse=True,
        )

    def explain(
        self,
        prefix: str,
        suggestions: Sequence[ScoredSuggestion],
    ) -> list[RankingExplanation]:
        ranked = self.rank(prefix, suggestions)

        return [
            RankingExplanation(
                value=s.suggestion.value,
                base_score=s.score,
                history_boost=0.0,
                final_score=s.score,
                source="score",
            )
            for s in ranked
        ]


def score_and_rank(
    suggestions: Sequence[ScoredSuggestion],
) -> list[ScoredSuggestion]:
    """
    Pure functional helper used by ranking invariant tests.
    """
    return ScoreRanker().rank("", suggestions)
