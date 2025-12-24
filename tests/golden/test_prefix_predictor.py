from aac.domain.types import CompletionContext
from aac.predictors.prefix import PrefixPredictor


def test_prefix_predictor_basic_completion():
    predictor = PrefixPredictor(
        vocabulary=["hello", "help", "helium", "hero"]
    )

    ctx = CompletionContext(text="he")
    results = predictor.predict(ctx)

    values = [r.suggestion.value for r in results]

    assert values == ["hello", "help", "helium", "hero"]


def test_prefix_predictor_no_match():
    predictor = PrefixPredictor(
        vocabulary=["hello", "help"]
    )

    ctx = CompletionContext(text="z")
    results = predictor.predict(ctx)

    assert results == []


def test_prefix_predictor_scores_are_deterministic():
    predictor = PrefixPredictor(
        vocabulary=["hello", "help"]
    )

    ctx = CompletionContext(text="he")
    results = predictor.predict(ctx)

    scores = [r.score for r in results]

    # Explicitly lock scoring behavior
    assert scores == [1.0, 1.0]


def test_prefix_predictor_returns_new_objects():
    predictor = PrefixPredictor(
        vocabulary=["hello"]
    )

    ctx = CompletionContext(text="h")
    r1 = predictor.predict(ctx)
    r2 = predictor.predict(ctx)

    assert r1 is not r2
    assert r1[0] is not r2[0]
