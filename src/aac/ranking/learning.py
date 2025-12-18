from __future__ import annotations

from collections.abc import Sequence

from aac.domain.history import History
from aac.domain.types import ScoredSuggestion, Suggestion
from aac.ranking.base import Ranker
from aac.ranking.contracts import LearnsFromHistory


class LearningRanker(Ranker, LearnsFromHistory):
    def __init__(self, history: History, boost: float = 1.0) -> None:
        self.history = history
        self._boost = boost

    def rank(
        self,
        prefix: str, 
        suggestions: Sequence[ScoredSuggestion],
    ) -> list[Suggestion]:  
        
        # Get historical counts for this specific prefix
        counts = self.history.counts_for_prefix(prefix)

        adjusted: list[ScoredSuggestion] = []
        for s in suggestions:
            # Use s.suggestion.value (ScoredSuggestion doesn't have .value)
            count = counts.get(s.suggestion.value, 0)
            
            # create new object because .score is read-only
            adjusted.append(
                ScoredSuggestion(
                    suggestion=s.suggestion,
                    score=s.score + (count * self._boost)
                )
            )

        # Sort by the new scores
        adjusted.sort(key=lambda s: s.score, reverse=True)
        
        # Return only the Suggestion objects to match the interface
        return [s.suggestion for s in adjusted]
