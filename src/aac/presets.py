from __future__ import annotations

from aac.domain.history import History
from aac.engine.engine import AutocompleteEngine
from aac.pipelines.developer import build_developer_pipeline
from aac.ranking.learning import LearningRanker
from aac.ranking.score import ScoreRanker


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
