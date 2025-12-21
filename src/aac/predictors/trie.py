from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable

from aac.domain.types import CompletionContext, ScoredSuggestion, Suggestion
from aac.domain.predictor import Predictor
from aac.ranking.explanation import RankingExplanation


@dataclass
class TrieNode:
    children: Dict[str, TrieNode] = field(default_factory=dict)
    is_terminal: bool = False
    value: str | None = None


class Trie:
    def __init__(self, words: Iterable[str]) -> None:
        self._root = TrieNode()
        for word in words:
            self._insert(word)

    def _insert(self, word: str) -> None:
        node = self._root
        for ch in word:
            node = node.children.setdefault(ch, TrieNode())
        node.is_terminal = True
        node.value = word

    def find_prefix(self, prefix: str) -> list[str]:
        node = self._root
        for ch in prefix:
            if ch not in node.children:
                return []
            node = node.children[ch]

        results: list[str] = []
        self._collect(node, results)
        return results

    def _collect(self, node: TrieNode, out: list[str]) -> None:
        if node.is_terminal and node.value is not None:
            out.append(node.value)
        for child in node.children.values():
            self._collect(child, out)


class TriePrefixPredictor(Predictor):
    def __init__(self, vocabulary: Iterable[str]) -> None:
        self._trie = Trie(vocabulary)

    @property
    def name(self) -> str:
        return "trie_prefix"

    def predict(self, context: CompletionContext) -> list[ScoredSuggestion]:
        prefix = context.prefix()
        if not prefix:
            return []

        matches = self._trie.find_prefix(prefix)

        return [
            ScoredSuggestion(
                suggestion=Suggestion(value),
                score=1.0,
                explanation=RankingExplanation.base(
                    value=value,
                    score=1.0,
                    source=self.name,
                ),
            )
            for value in matches
        ]

