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
    Construct an AutocompleteEngine.

    Presets define predictor composition and weighting.
    This mirrors how a production system would expose modes.
    """
    if preset == "developer":
        predictors = build_developer_pipeline(
            vocabulary=[
                "print",
                "private",
                "priority",
                "import",
                "class",
                "def",
            ],
            history=history,
        )
    else:
        raise ValueError(f"Unknown preset: {preset}")

    return AutocompleteEngine(
        predictors=predictors,
        ranker=LearningRanker(
            history=history,
            config=config,
        ),
        history=history,
    )
