from __future__ import annotations

from aac.engine import AutocompleteEngine
from aac.presets import create_engine


def build_engine(
    *,
    preset: str,
) -> AutocompleteEngine:
    """
    Construct an AutocompleteEngine from a named preset.

    Presets fully define:
    - predictors
    - rankers
    - learning behavior
    """
    return create_engine(preset)
