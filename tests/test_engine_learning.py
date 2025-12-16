from aac.engine.engine import AutocompleteEngine
from aac.predictors.prefix import PrefixPredictor
from aac.domain.history import History
from aac.ranking.learning import LearningRanker


def test_engine_adapts_after_selection() -> None:
    history = History()

    engine = AutocompleteEngine(
        predictors=[
            PrefixPredictor(["hello", "help"]),
        ],
        rankers=[
            LearningRanker(history),
        ],
        history=history,
    )

    initial = engine.suggest("he")
    assert initial[0].value in {"hello", "help"}

    engine.record_selection("he", "help")

    adapted = engine.suggest("he")
    assert adapted[0].value == "help"
