"""Contract test: tests shared history identity."""
def test_engine_and_learning_ranker_share_history() -> None:
    history = History()
    ranker = LearningRanker(history)

    engine = AutocompleteEngine(
        predictors=[PrefixPredictor(["hello", "help"])],
        ranker=ranker,
    )

    engine.record_selection("he", "help")

    assert history.count("help") == 1
