"""
Shared contract tests for all Ranker implementations.

Any ranker must satisfy these invariants. Add a subclass to
tests/contracts/test_ranker_contracts.py for each new ranker.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from aac.domain.types import ScoredSuggestion, Suggestion
from aac.ranking.base import Ranker
from aac.ranking.explanation import RankingExplanation


def _make_suggestion(value: str, score: float) -> ScoredSuggestion:
    return ScoredSuggestion(suggestion=Suggestion(value=value), score=score)


class RankerContractTestMixin(ABC):
    """
    Shared contract tests for all Ranker implementations.

    Subclass this and implement make_ranker() to get all invariants for free.
    Tests cover the core guarantees the engine relies on:

    - rank() preserves the candidate set (no additions or removals)
    - rank() returns a list, not a sequence or generator
    - rank() is stable on equal scores (preserves insertion order)
    - rank() on an empty list returns an empty list
    - explain() returns one explanation per suggestion
    - explain() values match the suggestions passed in
    - explain() final_score == base_score + history_boost (enforced by __post_init__)
    """

    @abstractmethod
    def make_ranker(self) -> Ranker:
        """Return a ranker instance under test."""
        raise NotImplementedError

    # ----------------------------------------------------------------
    # rank() contracts
    # ----------------------------------------------------------------

    def test_rank_empty_input_returns_empty_list(self) -> None:
        ranker = self.make_ranker()
        result = ranker.rank("he", [])
        assert result == []
        assert isinstance(result, list)

    def test_rank_returns_list(self) -> None:
        ranker = self.make_ranker()
        suggestions = [_make_suggestion("hello", 1.0)]
        result = ranker.rank("he", suggestions)
        assert isinstance(result, list)

    def test_rank_preserves_candidate_set(self) -> None:
        """The engine enforces this after every ranker step; ranker must not break it."""
        ranker = self.make_ranker()
        suggestions = [
            _make_suggestion("hello", 1.0),
            _make_suggestion("help", 0.8),
            _make_suggestion("helium", 0.5),
        ]
        result = ranker.rank("he", suggestions)
        assert {s.suggestion.value for s in result} == {
            s.suggestion.value for s in suggestions
        }, "rank() must not add or remove candidates"

    def test_rank_single_suggestion_returns_it(self) -> None:
        ranker = self.make_ranker()
        suggestions = [_make_suggestion("hello", 1.0)]
        result = ranker.rank("he", suggestions)
        assert len(result) == 1
        assert result[0].suggestion.value == "hello"

    def test_rank_does_not_mutate_input(self) -> None:
        ranker = self.make_ranker()
        suggestions = [
            _make_suggestion("hello", 1.0),
            _make_suggestion("help", 0.8),
        ]
        original_order = [s.suggestion.value for s in suggestions]
        ranker.rank("he", suggestions)
        assert [s.suggestion.value for s in suggestions] == original_order, (
            "rank() must not mutate the input list"
        )

    def test_rank_scores_are_finite(self) -> None:
        import math
        ranker = self.make_ranker()
        suggestions = [
            _make_suggestion("hello", 1.0),
            _make_suggestion("help", 0.8),
        ]
        result = ranker.rank("he", suggestions)
        for s in result:
            assert math.isfinite(s.score), (
                f"rank() produced non-finite score {s.score!r} for {s.suggestion.value!r}"
            )

    def test_rank_with_identical_prefix_is_deterministic(self) -> None:
        """Two rank() calls with the same inputs must return the same order."""
        ranker = self.make_ranker()
        suggestions = [
            _make_suggestion("hello", 1.0),
            _make_suggestion("help", 0.8),
            _make_suggestion("helium", 0.5),
        ]
        first = [s.suggestion.value for s in ranker.rank("he", suggestions)]
        second = [s.suggestion.value for s in ranker.rank("he", suggestions)]
        assert first == second, "rank() must be deterministic for the same inputs"

    def test_rank_preserves_insertion_order_on_equal_scores(self) -> None:
        """When scores are equal, original insertion order must be preserved (stable sort)."""
        ranker = self.make_ranker()
        # All suggestions have the same score, so ranking order must equal insertion order.
        suggestions = [
            _make_suggestion("alpha", 1.0),
            _make_suggestion("beta", 1.0),
            _make_suggestion("gamma", 1.0),
        ]
        result = ranker.rank("a", suggestions)
        result_values = [s.suggestion.value for s in result]
        # Insertion order must be preserved when all scores are equal.
        # A ranker that sorts unstably would permute this list arbitrarily.
        assert result_values == ["alpha", "beta", "gamma"], (
            f"rank() must be stable on equal scores; got {result_values}"
        )

    # ----------------------------------------------------------------
    # explain() contracts
    # ----------------------------------------------------------------

    def test_explain_returns_one_per_suggestion(self) -> None:
        ranker = self.make_ranker()
        suggestions = [
            _make_suggestion("hello", 1.0),
            _make_suggestion("help", 0.8),
        ]
        # explain() is called after rank() in the engine; call rank() first
        # so caches are warm (matches real engine usage).
        ranker.rank("he", suggestions)
        explanations = ranker.explain("he", suggestions)
        assert len(explanations) == len(suggestions)

    def test_explain_empty_input_returns_empty_list(self) -> None:
        ranker = self.make_ranker()
        ranker.rank("he", [])
        result = ranker.explain("he", [])
        assert result == []

    def test_explain_returns_ranking_explanation_objects(self) -> None:
        ranker = self.make_ranker()
        suggestions = [_make_suggestion("hello", 1.0)]
        ranker.rank("he", suggestions)
        explanations = ranker.explain("he", suggestions)
        for exp in explanations:
            assert isinstance(exp, RankingExplanation)

    def test_explain_values_match_suggestions(self) -> None:
        ranker = self.make_ranker()
        suggestions = [
            _make_suggestion("hello", 1.0),
            _make_suggestion("help", 0.8),
        ]
        ranker.rank("he", suggestions)
        explanations = ranker.explain("he", suggestions)
        explanation_values = {e.value for e in explanations}
        suggestion_values = {s.suggestion.value for s in suggestions}
        assert explanation_values == suggestion_values

    def test_explain_invariant_holds(self) -> None:
        """RankingExplanation enforces final == base + boost at construction time.

        This test exists to document the contract: if a ranker produces
        an inconsistent explanation, RankingExplanation.__post_init__ raises
        ValueError. Passing here means the ranker is constructing explanations
        correctly.
        """
        ranker = self.make_ranker()
        suggestions = [
            _make_suggestion("hello", 1.0),
            _make_suggestion("help", 0.8),
        ]
        ranker.rank("he", suggestions)
        # Implicitly tested: explain() must not raise ValueError.
        # If the invariant is violated, the exception surfaces here.
        explanations = ranker.explain("he", suggestions)
        for exp in explanations:
            assert abs(exp.final_score - (exp.base_score + exp.history_boost)) < 1e-9
