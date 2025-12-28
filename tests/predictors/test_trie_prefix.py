from aac.domain.types import CompletionContext
from aac.predictors.trie import TriePrefixPredictor


def test_trie_prefix_basic_completion() -> None:
    predictor = TriePrefixPredictor(
        ["hello", "help", "helium", "world"]
    )

    ctx = CompletionContext("he")
    results = predictor.predict(ctx)

    values = sorted(s.value for s in results)

    assert values == ["helium", "hello", "help"]


def test_trie_prefix_no_match() -> None:
    predictor = TriePrefixPredictor(["hello", "world"])

    ctx = CompletionContext("xyz")
    results = predictor.predict(ctx)

    assert results == []


def test_trie_prefix_explanation_source() -> None:
    predictor = TriePrefixPredictor(["hello"])
    ctx = CompletionContext("he")

    result = predictor.predict(ctx)[0]

    explanation = result.explanation
    assert explanation is not None
    assert explanation.source == "trie_prefix"
    assert explanation.score == 1.0
