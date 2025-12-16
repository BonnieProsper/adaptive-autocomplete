from aac.domain.history import History
from aac.predictors.history import HistoryPredictor


def test_history_predictor_learns() -> None:
    history = History()
    predictor = HistoryPredictor(history)

    predictor.record("he", "hello")
    predictor.record("he", "hello")
    predictor.record("he", "help")

    results = predictor.predict("he")

    scores = {r.suggestion.value: r.score for r in results}

    assert scores["hello"] == 2.0
    assert scores["help"] == 1.0
