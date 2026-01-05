from __future__ import annotations

from aac.config import EngineConfig
from aac.domain.history import History
from aac.engine.engine import AutocompleteEngine
from aac.pipelines.developer import build_developer_pipeline
from aac.ranking.learning import LearningRanker


def build_engine(
    *,
    history: History,
    config: EngineConfig,
) -> AutocompleteEngine:
    """
    Construct the default CLI engine.

    This uses the developer pipeline:
    - prefix matching
    - trie-based completion
    - history-based learning
    - global frequency bias
    """

    predictors = build_developer_pipeline(
        vocabulary=[
            # demo-safe vocabulary (will be replaced later)
            "hello",
            "help",
            "helium",
            "hero",
            "heap",
            "hex",
            "height",
        ],
        history=history,
    )

    ranker = LearningRanker(
        history=history,
        config=config,
    )

    return AutocompleteEngine(
        predictors=predictors,
        ranker=ranker,
        history=history,
    )
