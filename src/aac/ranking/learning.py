from aac.domain.history import History
from aac.ranking.base import Ranker
from aac.ranking.contracts import LearnsFromHistory
from aac.ranking.score import ScoredSuggestion


class LearningRanker(Ranker, LearnsFromHistory):
    def __init__(self, history: History) -> None:
        self.history = history

    def rank(
        self,
        suggestions: list[ScoredSuggestion],
    ) -> list[ScoredSuggestion]:
        for suggestion in suggestions:
            suggestion.score += self.history.count(suggestion.value)
        return sorted(suggestions, key=lambda s: s.score, reverse=True)
