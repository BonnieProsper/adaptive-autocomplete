from aac.domain.types import CompletionContext, Suggestion, ScoredSuggestion, PredictionResult


def test_prefix_without_cursor():
    ctx = CompletionContext(text="git che")
    assert ctx.prefix() == "che"


def test_prefix_with_cursor():
    ctx = CompletionContext(text="git checkout", cursor_pos=7)
    assert ctx.prefix() == "ch"


def test_scored_suggestion_holds_score():
    s = Suggestion("checkout")
    scored = ScoredSuggestion(suggestion=s, score=0.8)

    assert scored.suggestion.value == "checkout"
    assert scored.score == 0.8


def test_prediction_result_structure():
    result = PredictionResult(
        predictor="frequency",
        suggestions=[],
    )

    assert result.predictor == "frequency"
    assert result.suggestions == []

