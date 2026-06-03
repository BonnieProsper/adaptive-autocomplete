"""
Contract tests: every Ranker implementation must satisfy the
RankerContractTestMixin invariants. Add new rankers here.
"""
from __future__ import annotations

from datetime import datetime, timezone

from aac.domain.history import History
from aac.ranking.base import Ranker
from aac.ranking.decay import DecayFunction, DecayRanker
from aac.ranking.learning import LearningRanker
from aac.ranking.score import ScoreRanker
from tests.contracts.ranker_contract import RankerContractTestMixin

_NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


class TestScoreRankerContract(RankerContractTestMixin):
    def make_ranker(self) -> Ranker:
        return ScoreRanker()


class TestLearningRankerContract(RankerContractTestMixin):
    """LearningRanker with empty history - no boost applied, but contracts still hold."""

    def make_ranker(self) -> Ranker:
        return LearningRanker(History(), boost=1.0)


class TestLearningRankerWithHistoryContract(RankerContractTestMixin):
    """LearningRanker with pre-populated history - exercises the boost path."""

    def make_ranker(self) -> Ranker:
        history = History()
        history.record("he", "hello")
        history.record("he", "hello")
        history.record("he", "help")
        return LearningRanker(history, boost=1.5, dominance_ratio=2.0)


class TestDecayRankerContract(RankerContractTestMixin):
    """DecayRanker with empty history - no boost applied, but contracts still hold."""

    def make_ranker(self) -> Ranker:
        return DecayRanker(
            History(),
            DecayFunction(half_life_seconds=3600.0),
            now=_NOW,
        )


class TestDecayRankerWithHistoryContract(RankerContractTestMixin):
    """DecayRanker with recent history - exercises the decay boost path."""

    def make_ranker(self) -> Ranker:
        history = History()
        ts = datetime(2025, 12, 31, 23, 0, tzinfo=timezone.utc)  # 1h before _NOW
        history.record("he", "hello", timestamp=ts)
        history.record("he", "hello", timestamp=ts)
        history.record("he", "help", timestamp=ts)
        return DecayRanker(
            history,
            DecayFunction(half_life_seconds=3600.0),
            now=_NOW,
        )
