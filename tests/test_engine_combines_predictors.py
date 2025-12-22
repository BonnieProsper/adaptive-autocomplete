from aac.engine.engine import AutocompleteEngine
from aac.predictors.frequency import FrequencyPredictor
from aac.predictors.trie import TriePrefixPredictor


def test_engine_combines_predictors() -> None:
    engine = AutocompleteEngine(
        predictors=[
            TriePrefixPredictor(["hello", "help"]),
            FrequencyPredictor({"hello": 10, "help": 1}),
        ]
    )

    results = engine.suggest("he")
    values = [s.value for s in results]

    assert values[0] == "hello"
