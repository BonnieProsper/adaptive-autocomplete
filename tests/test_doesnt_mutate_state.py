from aac.domain.history import History
from aac.domain.types import ScoredSuggestion, Suggestion
from aac.ranking.learning import LearningRanker


def test_explain_does_not_modify_history() -> None:
    history = History()
    ranker = LearningRanker(history)

    suggestions = [
        ScoredSuggestion(Suggestion("x"), 0.0),
    ]

    ranker.explain("x", suggestions)

    assert len(history.entries()) == 0
