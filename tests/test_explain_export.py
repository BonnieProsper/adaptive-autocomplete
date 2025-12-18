from aac.domain.history import History
from aac.domain.types import ScoredSuggestion, Suggestion
from aac.ranking.learning import LearningRanker


def test_explanation_dict_export() -> None:
    history = History()
    ranker = LearningRanker(history)

    suggestions = [
        ScoredSuggestion(Suggestion("hello"), 0.5),
    ]

    exported = ranker.explain_as_dicts("he", suggestions)

    assert exported == [
        {
            "value": "hello",
            "base_score": 0.5,
            "history_boost": 0.0,
            "final_score": 0.5,
        }
    ]
