from aac.domain.history import History
from aac.domain.types import ScoredSuggestion, Suggestion
from aac.ranking.learning import LearningRanker


def test_learning_ranker_boosts_previously_selected_value() -> None:
    history = History()
    history.record("he", "hello")
    history.record("he", "hello")

    ranker = LearningRanker(history, boost=1.0)

    suggestions = [
        ScoredSuggestion(Suggestion("hello"), 1.0),
        ScoredSuggestion(Suggestion("help"), 1.0),
    ]

    ranked = ranker.rank("he", suggestions)

    assert ranked[0].value == "hello"
