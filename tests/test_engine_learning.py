from aac.domain.history import History
from aac.engine.engine import AutocompleteEngine
from aac.predictors.static_prefix import StaticPrefixPredictor
from aac.ranking.learning import LearningRanker


def test_engine_adapts_after_selection() -> None:
    history = History()

    engine = AutocompleteEngine(
        predictors=[
            StaticPrefixPredictor(["hello", "help"]),
        ],
        ranker=LearningRanker(history),
    )

    # initial order is alphabetical / neutral
    initial = engine.suggest("he")
    assert [s.value for s in initial] == ["hello", "help"]

    # user selects "help"
    engine.record_selection("he", "help")

    updated = engine.suggest("he")
    assert updated[0].value == "help"
