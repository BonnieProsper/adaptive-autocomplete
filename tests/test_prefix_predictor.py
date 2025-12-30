from aac.predictors.static_prefix import StaticPrefixPredictor


def test_prefix_predictor_basic() -> None:
    predictor = StaticPrefixPredictor(
        vocabulary=["hello", "help", "helium", "world"]
    )

    results = predictor.predict("he")

    values = {r.suggestion.value for r in results}

    assert values == {"hello", "help", "helium"}


def test_prefix_predictor_empty_input() -> None:
    predictor = StaticPrefixPredictor(vocabulary=["hello"])

    assert predictor.predict("") == []


def test_prefix_predictor_exact_match_not_repeated() -> None:
    predictor = StaticPrefixPredictor(vocabulary=["hello"])

    assert predictor.predict("hello") == []
