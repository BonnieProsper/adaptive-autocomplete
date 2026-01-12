from __future__ import annotations

from aac.domain.history import History
from aac.engine.engine import AutocompleteEngine
from aac.pipelines.developer import build_developer_pipeline
from aac.ranking.learning import LearningRanker
from aac.ranking.score import ScoreRanker
from aac.domain.command_palette import COMMANDS
from aac.predictors.static_prefix import StaticPrefixPredictor
from aac.predictors.trie import TriePrefixPredictor
from aac.predictors.history import HistoryPredictor
from aac.predictors.frequency import FrequencyPredictor
from aac.ranking.learning import LearningRanker
from aac.ranking.decay import DecayRanker
from aac.ranking.weighted import WeightedRanker


def command_palette_engine() -> AutocompleteEngine:
    predictors = [
        StaticPrefixPredictor(COMMANDS),
        TriePrefixPredictor(COMMANDS),
        FrequencyPredictor(),
        HistoryPredictor(),
    ]

    rankers = [
        WeightedRanker(
            LearningRanker(),
            weight=1.0,
        ),
        DecayRanker(
            half_life=3600.0 * 24 * 7,  # 7-day decay
        ),
        ScoreRanker(),
    ]

    return AutocompleteEngine(
        predictors=predictors,
        rankers=rankers,
    )


def developer_engine(
    *,
    vocabulary: list[str],
    history: History | None = None,
) -> AutocompleteEngine:
    """
    Developer-oriented autocomplete preset.

    Characteristics:
    - Prefix + trie-based prediction
    - History-aware personalization
    - Balanced learning influence
    - Stable, explainable ranking

    This is the recommended default preset.
    """
    history = history or History()

    predictors = build_developer_pipeline(
        vocabulary=vocabulary,
        history=history,
    )

    rankers = [
        ScoreRanker(),
        LearningRanker(
            history=history,
            boost=0.75,
            dominance_ratio=1.0,
        ),
    ]

    return AutocompleteEngine(
        predictors=predictors,
        ranker=rankers,
        history=history,
    )
