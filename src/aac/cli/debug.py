"""Verbose pipeline inspection. Unstable output - not public API."""
from __future__ import annotations

from aac.engine.engine import AutocompleteEngine


def run(
    *,
    engine: AutocompleteEngine,
    text: str,
) -> None:
    """Print scored and ranked candidates for a prefix."""
    state = engine.debug(text)

    scored = sorted(state["scored"], key=lambda s: s.score, reverse=True)
    ranked = state["ranked"]

    print(f"Input: {state['input']}")
    print(f"\nScored (top 20 of {len(scored)}, by score):")
    for s in scored[:20]:
        print(f"  {s.suggestion.value:20} score={s.score:.2f}")

    print("\nRanked (top 10):")
    for s in ranked[:10]:
        print(f"  {s.suggestion.value:20} score={s.score:.2f}")

