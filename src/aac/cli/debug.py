"""
DEBUG COMMAND

This output is verbose, unstable and 
intended for engine inspection, not end users
"""
from __future__ import annotations

from aac.engine.engine import AutocompleteEngine
from aac.pipelines.debug import debug_pipeline


def run(
    *,
    engine: AutocompleteEngine,
    text: str,
) -> None:
    debug_pipeline(engine, text)
