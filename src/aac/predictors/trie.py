from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field

from aac.domain.predictor import Predictor
from aac.domain.types import (
    CompletionContext,
    PredictorExplanation,
    ScoredSuggestion,
    Suggestion,
    ensure_context,
)


@dataclass
class TrieNode:
    children: dict[str, TrieNode] = field(default_factory=dict)
    is_terminal: bool = False
    value: str | None = None


class Trie:
    def __init__(self, words: Iterable[str]) -> None:
        self._root = TrieNode()
        for word in words:
            self.insert(word)

    def insert(self, word: str) -> None:
        node = self._root
        for ch in word:
            node = node.children.setdefault(ch, TrieNode())
        node.is_terminal = True
        node.value = word

    def find_prefix(self, prefix: str, *, limit: int) -> list[str]:
        node = self._root
        for ch in prefix:
            if ch not in node.children:
                return []
            node = node.children[ch]

        results: list[str] = []
        self._collect(node, results, limit)
        return results

    def _collect(self, node: TrieNode, out: list[str], limit: int) -> None:
        if len(out) >= limit:
            return

        if node.is_terminal and node.value is not None:
            out.append(node.value)
            if len(out) >= limit:
                return

        for key in sorted(node.children):
            self._collect(node.children[key], out, limit)
            if len(out) >= limit:
                return


class TriePrefixPredictor(Predictor):
    """
    Prefix predictor backed by a trie for efficient lookup.

    Responsibilities:
    - Efficient prefix recall
    - Deterministic ordering
    - Neutral base scoring
    """

    name: str = "trie_prefix"

    def __init__(self, words: Iterable[str], *, max_results: int = 10) -> None:
        self._trie = Trie(words)
        self._max_results = max_results

    def predict(self, ctx: CompletionContext | str) -> list[ScoredSuggestion]:
        ctx = ensure_context(ctx)
        prefix = ctx.prefix()

        if not prefix:
            return []

        matches = self._trie.find_prefix(prefix, limit=self._max_results)

        results: list[ScoredSuggestion] = []

        for word in matches:
            # Do not repeat exact matches
            if word == prefix:
                continue

            results.append(
                ScoredSuggestion(
                    suggestion=Suggestion(value=word),
                    score=1.0,
                    explanation=PredictorExplanation(
                        value=word,
                        score=1.0,
                        source=self.name,
                    ),
                    trace=[
                        f"prefix='{prefix}'",
                        f"matched='{word}'",
                        "score=1.0",
                    ],
                )
            )

        return results
