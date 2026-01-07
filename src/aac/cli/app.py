from __future__ import annotations

from aac.domain.history import History
from aac.engine.engine import AutocompleteEngine
from aac.presets import developer_engine


def build_engine(
    *,
    history: History,
    preset: str = "developer",
) -> AutocompleteEngine:
    if preset == "developer":
        return developer_engine(
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

    raise ValueError(f"Unknown engine preset: {preset}")
