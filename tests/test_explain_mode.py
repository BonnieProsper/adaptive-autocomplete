from aac.domain.history import History
from aac.engine.engine import AutocompleteEngine
from aac.predictors.prefix import PrefixPredictor
from aac.ranking.learning import LearningRanker


def test_cli_explain_does_not_mutate_history() -> None:
    history = History()
    engine = AutocompleteEngine(
        predictors=[PrefixPredictor(["hello"])],
        ranker=LearningRanker(history),
    )

    engine.explain("he")

    assert history.entries() == ()
