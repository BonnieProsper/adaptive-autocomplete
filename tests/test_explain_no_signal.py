from aac.domain.history import History
from aac.domain.types import ScoredSuggestion, Suggestion
from aac.ranking.learning import LearningRanker


def test_explain_has_zero_boost_without_history() -> None:
    history = History()
    ranker = LearningRanker(history)

    suggestions = [
        ScoredSuggestion(Suggestion("a"), 0.0),
        ScoredSuggestion(Suggestion("b"), 1.0),
    ]

    explanations = ranker.explain("a", suggestions)

    for e in explanations:
        assert e.history_boost == 0.0
        assert e.final_score == e.base_score
