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
    preset: str = "developer",
) -> AutocompleteEngine:
    """
    Construct an autocomplete engine based on a named preset.

    Presets define:
    - predictor pipeline
    - ranking strategy
    """

    if preset == "developer":
        predictors = build_developer_pipeline(
            vocabulary=[
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
    else:
        raise ValueError(f"Unknown engine preset: {preset}")

    ranker = LearningRanker(
        history=history,
        config=config,
    )

    return AutocompleteEngine(
        predictors=predictors,
        ranker=ranker,
        history=history,
    )
