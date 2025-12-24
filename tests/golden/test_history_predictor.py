from aac.domain.history import History
from aac.domain.types import CompletionContext
from aac.predictors.history import HistoryPredictor


def test_history_predictor_returns_seen_values():
    history = History()
    history.record("h", "hello")
    history.record("h", "hello")
    history.record("h", "help")

    predictor = HistoryPredictor(history)

    ctx = CompletionContext(text="h")
    results = predictor.predict(ctx)

    values = [r.suggestion.value for r in results]

    assert values == ["hello", "help"]


def test_history_predictor_scores_reflect_frequency():
    history = History()
    history.record("h", "hello")
    history.record("h", "hello")
    history.record("h", "help")

    predictor = HistoryPredictor(history)

    ctx = CompletionContext(text="h")
    results = predictor.predict(ctx)

    scores = {r.suggestion.value: r.score for r in results}

    assert scores["hello"] > scores["help"]
