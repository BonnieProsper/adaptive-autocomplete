from aac.domain.history import History
from aac.domain.types import ScoredSuggestion, Suggestion
from aac.ranking.learning import LearningRanker

def test_explain_reflects_learning_history() -> None:
    history = History()
    ranker = LearningRanker(history, boost=1.0)

    history.record("he", "help")
    history.record("he", "help")

    suggestions = [
        ScoredSuggestion(Suggestion("hello"), 0.0),
        ScoredSuggestion(Suggestion("help"), 0.0),
    ]

    explanations = ranker.explain("he", suggestions)

    help_expl = next(e for e in explanations if e.value == "help")
    hello_expl = next(e for e in explanations if e.value == "hello")

    assert help_expl.history_boost == 2.0
    assert help_expl.final_score == 2.0

    assert hello_expl.history_boost == 0.0
