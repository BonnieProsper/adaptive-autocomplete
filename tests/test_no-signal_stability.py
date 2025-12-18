# locks invariant L2
def test_learning_ranker_preserves_order_without_history() -> None:
    history = History()
    ranker = LearningRanker(history)

    suggestions = [
        ScoredSuggestion(Suggestion("a"), 0.0),
        ScoredSuggestion(Suggestion("b"), 0.0),
    ]

    ranked = ranker.rank("x", suggestions)

    assert [s.value for s in ranked] == ["a", "b"]
