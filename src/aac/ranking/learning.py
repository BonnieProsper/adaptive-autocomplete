from collections.abc import Sequence

from aac.domain.history import History
from aac.domain.types import ScoredSuggestion, Suggestion
from aac.ranking.base import Ranker


class LearningRanker(Ranker):
    def __init__(self, history: History, boost: float = 1.0) -> None:
        self._history = history
        self._boost = boost

    def rank(self, prefix: str, suggestions: Sequence[ScoredSuggestion]) -> list[Suggestion]:
        counts = self._history.counts_for_prefix(prefix)

        adjusted = [
            ScoredSuggestion(
                s.suggestion,
                s.score + counts.get(s.suggestion.value, 0)
            )
            for s in suggestions
        ]
        adjusted.sort(key=lambda s: (-s.score, s.suggestion.value))
        return [s.suggestion for s in adjusted]
