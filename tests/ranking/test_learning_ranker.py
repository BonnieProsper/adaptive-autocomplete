from aac.domain.history import History
from aac.domain.types import ScoredSuggestion
from aac.ranking.learning import LearningRanker


def test_learning_ranker_boosts_previously_selected_value() -> None:
    history = History()
    history.record("he", "hello")
    history.record("he", "hello")

    ranker = LearningRanker(history, weight=1.0)

    suggestions = [
        ScoredSuggestion("hello", 1.0),
        ScoredSuggestion("help", 1.0),
    ]

    ranked = ranker.rank("he", suggestions)

    scores = {s.value: s.score for s in ranked}

    assert scores["hello"] == 3.0
    assert scores["help"] == 1.0
