from aac.domain.types import CompletionContext, ScoredSuggestion, Suggestion, WeightedPredictor
from aac.engine.engine import AutocompleteEngine
from tests.contracts.predictor_contract import PredictorContractTestMixin


class DummyPredictor:
    def __init__(self, name: str, score: float):
        self.name = name
        self._score = score

    def predict(self, context: CompletionContext):
        return [
            ScoredSuggestion(
                suggestion=Suggestion(value="hello"),
                score=self._score,
                explanation=None,
            )
        ]


class TestDummyPredictorContract(PredictorContractTestMixin):
    def make_predictor(self):
        return DummyPredictor(name="dummy", score=1.0)


def test_weighting_affects_score():
    low = DummyPredictor("low", 1.0)
    high = DummyPredictor("high", 1.0)

    engine = AutocompleteEngine(
        predictors=[
            WeightedPredictor(low, weight=1.0),
            WeightedPredictor(high, weight=3.0),
        ]
    )

    ctx = CompletionContext(text="h")
    results = engine.complete(ctx)

    assert len(results) == 1
    assert results[0].score == 4.0
