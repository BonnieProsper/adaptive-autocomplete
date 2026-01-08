"""
DEBUG COMMAND

Verbose, unstable output intended for engine inspection,
not end users. Not part of the public API.
"""
from __future__ import annotations

from aac.engine.engine import AutocompleteEngine


def run(
    *,
    engine: AutocompleteEngine,
    text: str,
) -> None:
    """
    Invoke engine debug mode.

    This deliberately routes through the engine
    to avoid leaking internal pipeline structure
    into the CLI layer.
    """
    engine.debug(text)
