from __future__ import annotations

from aac.domain.history import History
from aac.engine.engine import AutocompleteEngine
from aac.presets import get_preset


def build_engine(
    *,
    preset: str,
    history: History | None = None,
) -> AutocompleteEngine:
    """
    Construct an AutocompleteEngine from a named preset.

    The application layer is responsible for:
    - selecting the preset
    - hydrating persistence (History)

    Presets define:
    - predictors
    - rankers
    - learning behavior
    """
    preset_def = get_preset(preset)

    return AutocompleteEngine(
        predictors=preset_def.predictors,
        ranker=preset_def.rankers,
        history=history,
    )
