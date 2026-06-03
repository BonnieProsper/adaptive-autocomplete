"""Query log structures and generators for offline evaluation."""
from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aac.domain.history import History


@dataclass
class QueryLogEntry:
    """A single evaluation query: a prefix and the set of relevant completions (ground truth)."""
    prefix: str
    relevant: set[str]
    grades: dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.prefix:
            raise ValueError("QueryLogEntry prefix must be non-empty")
        if not self.relevant:
            raise ValueError(
                f"QueryLogEntry for prefix {self.prefix!r} has no relevant completions. "
                "An entry with no relevant completions cannot contribute to any metric."
            )


#: A query log is a list of entries.
QueryLog = list[QueryLogEntry]


def make_query_log_from_history(
    history: History,
    *,
    min_count: int = 1,
    max_entries: int | None = None,
    seed: int = 42,
) -> QueryLog:
    """Build a QueryLog from recorded selections. relevant = values selected >= min_count times."""
    counts = history.snapshot_counts()

    entries: list[QueryLogEntry] = []
    for prefix, word_counts in counts.items():
        relevant_words = {
            word: count
            for word, count in word_counts.items()
            if count >= min_count
        }
        if not relevant_words:
            continue

        max_count = max(relevant_words.values())
        grades = {
            word: count / max_count
            for word, count in relevant_words.items()
        }

        entries.append(QueryLogEntry(
            prefix=prefix,
            relevant=set(relevant_words.keys()),
            grades=grades,
        ))

    if max_entries is not None and len(entries) > max_entries:
        # Use a seeded RNG so the same history always produces the same
        # subsample. Without seeding, evaluation results vary between runs
        # even with identical inputs, making metric comparisons meaningless.
        rng = random.Random(seed)
        entries = rng.sample(entries, max_entries)

    return entries


def make_synthetic_query_log(
    vocabulary: list[str],
    *,
    prefix_lengths: list[int] | None = None,
    include_typos: bool = True,
    seed: int = 42,
) -> QueryLog:
    """Generate a synthetic QueryLog from a vocabulary for testing. No real user data needed."""
    rng = random.Random(seed)
    if prefix_lengths is None:
        prefix_lengths = [2, 3, 4]

    entries: dict[str, QueryLogEntry] = {}

    for word in vocabulary:
        for length in prefix_lengths:
            if len(word) <= length:
                continue
            prefix = word[:length]
            if prefix in entries:
                entries[prefix].relevant.add(word)
            else:
                entries[prefix] = QueryLogEntry(
                    prefix=prefix,
                    relevant={word},
                )

    if include_typos:
        # Add a small number of typo entries from a random sample
        sample = rng.sample(vocabulary, min(50, len(vocabulary)))
        for word in sample:
            if len(word) < 4:
                continue
            # Single character deletion typo
            pos = rng.randint(1, len(word) - 2)
            typo = word[:pos] + word[pos + 1:]
            if typo not in entries:
                entries[typo] = QueryLogEntry(
                    prefix=typo,
                    relevant={word},
                )

    return list(entries.values())


def load_jsonl(path: Path) -> QueryLog:
    """
    Load a JSONL query log. Each line: {"prefix": str, "relevant": [str], "grades": {str: float}}.
    grades is optional.
    """
    entries = []
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                obj = json.loads(line)
                if not isinstance(obj, dict):
                    raise ValueError(f"expected a JSON object, got {type(obj).__name__}")
                entries.append(QueryLogEntry(
                    prefix=obj["prefix"],
                    relevant=set(obj["relevant"]),
                    grades=obj.get("grades", {}),
                ))
            except (KeyError, json.JSONDecodeError, ValueError) as e:
                raise ValueError(
                    f"Invalid query log entry at line {i} in {path}: {e}\n"
                    f"Expected: {{\"prefix\": \"...\", \"relevant\": [...], \"grades\": {{...}}}}"
                ) from e
    return entries


def save_jsonl(log: QueryLog, path: Path) -> None:
    """Save a QueryLog to JSONL. Creates parent directories if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for entry in log:
            obj: dict[str, object] = {
                "prefix": entry.prefix,
                "relevant": sorted(entry.relevant),
            }
            if entry.grades:
                obj["grades"] = entry.grades
            f.write(json.dumps(obj) + "\n")
