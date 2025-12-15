from aac.engine.engine import AutocompleteEngine
from aac.predictors.frequency import FrequencyPredictor
from aac.predictors.prefix import PrefixPredictor


def test_engine_combines_multiple_predictors() -> None:
    prefix = PrefixPredictor(
        vocabulary=["hello", "help", "helium", "world"]
    )

    frequency = FrequencyPredictor(
        {
            "hello": 10,
            "help": 5,
            "helium": 1,
            "world": 20,
        }
    )

    engine = AutocompleteEngine(
        predictors=[prefix, frequency]
    )

    results = engine.suggest("he")

    values = [s.value for s in results]

    assert values == ["hello", "help", "helium"]
