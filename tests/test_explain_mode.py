from aac.domain.history import History
from aac.engine.engine import AutocompleteEngine
from aac.predictors.static_prefix import StaticPrefixPredictor
from aac.ranking.learning import LearningRanker


def test_cli_explain_does_not_mutate_history() -> None:
    history = History()
    engine = AutocompleteEngine(
        predictors=[StaticPrefixPredictor(["hello"])],
        ranker=LearningRanker(history),
    )

    engine.explain("he")

    assert history.entries() == ()
