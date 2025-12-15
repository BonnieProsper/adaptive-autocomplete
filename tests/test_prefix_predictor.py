from aac.predictors.prefix import PrefixPredictor


def test_prefix_predictor_basic() -> None:
    predictor = PrefixPredictor(
        vocabulary=["hello", "help", "helium", "world"]
    )

    results = predictor.predict("he")

    texts = {r.suggestion.text for r in results}

    assert texts == {"hello", "help", "helium"}


def test_prefix_predictor_empty_input() -> None:
    predictor = PrefixPredictor(vocabulary=["hello"])

    assert predictor.predict("") == []


def test_prefix_predictor_exact_match_not_repeated() -> None:
    predictor = PrefixPredictor(vocabulary=["hello"])

    assert predictor.predict("hello") == []
