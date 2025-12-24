from aac.domain.types import CompletionContext, WeightedPredictor
from aac.engine.engine import AutocompleteEngine


class DummyPredictor:
    def __init__(self, name: str, score: float):
        self.name = name
        self._score = score

    def predict(self, context: CompletionContext):
        return [
            ScoredCompletion(
                text="hello",
                score=self._score,
                explanation=self.name,
            )
        ]


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

    assert results[0].score == 4.0
