"""adaptive-autocomplete: autocomplete engine with typo recovery, learning, and explainable ranking."""

from aac.domain.history import History
from aac.domain.thread_safe_history import ThreadSafeHistory
from aac.engine.engine import AutocompleteEngine
from aac.presets import create_engine
from aac.ranking.explanation import RankingExplanation
from aac.storage.json_store import JsonHistoryStore
from aac.vocabulary import vocabulary_from_file, vocabulary_from_text, vocabulary_from_wordlist

__version__ = "1.0.4"
__author__ = "Bonnie McConnell"
__license__ = "MIT"
__all__ = [
    "__version__",
    "__author__",
    "__license__",
    "AutocompleteEngine",
    "History",
    "JsonHistoryStore",
    "RankingExplanation",
    "ThreadSafeHistory",
    "create_engine",
    "vocabulary_from_file",
    "vocabulary_from_text",
    "vocabulary_from_wordlist",
]
