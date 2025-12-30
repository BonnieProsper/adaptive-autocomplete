from aac.domain.history import History
from aac.engine.engine import AutocompleteEngine
from aac.predictors.static_prefix import StaticPrefixPredictor
from aac.ranking.learning import LearningRanker


def test_engine_and_learning_ranker_share_history() -> None:
    history = History()
    ranker = LearningRanker(history)

    engine = AutocompleteEngine(
        predictors=[StaticPrefixPredictor(["hello", "help"])],
        ranker=ranker,
    )

    engine.record_selection("he", "help")

    assert history.count("help") == 1
