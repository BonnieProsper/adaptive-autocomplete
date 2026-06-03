"""Bundled English word frequency data (derived from wordfreq, MIT licensed)."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from types import MappingProxyType

_DATA_DIR = Path(__file__).parent


@lru_cache(maxsize=1)
def load_english_frequencies() -> MappingProxyType[str, int]:
    """Immutable mapping of lowercase word -> frequency score (~48k words). Cached after first load."""
    path = _DATA_DIR / "english_frequencies.json"
    data = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(data, dict):
        raise ValueError(f"Expected dict in {path}, got {type(data).__name__}")

    return MappingProxyType({str(k): int(v) for k, v in data.items()})