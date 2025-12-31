from aac.domain.history import History
from aac.domain.types import WeightedPredictor
from aac.predictors.frequency import FrequencyPredictor
from aac.predictors.history import HistoryPredictor
from aac.predictors.static_prefix import StaticPrefixPredictor
from aac.predictors.trie import TriePrefixPredictor


DEFAULT_FREQUENCIES: dict[str, int] = {
    # minimal dev-safe defaults
    "print": 100,
    "import": 90,
    "def": 80,
    "class": 70,
}


def build_developer_pipeline(
    vocabulary: list[str],
    history: History,
) -> list[WeightedPredictor]:
    return [
        WeightedPredictor(
            predictor=StaticPrefixPredictor(vocabulary),
            weight=1.0,
        ),
        WeightedPredictor(
            predictor=TriePrefixPredictor(vocabulary),
            weight=1.0,
        ),
        WeightedPredictor(
            predictor=HistoryPredictor(history),
            weight=2.0,  # user intent matters more
        ),
        WeightedPredictor(
            predictor=FrequencyPredictor(frequencies=DEFAULT_FREQUENCIES, max_results=10),
            weight=0.5,  # weak global bias
        ),
    ]

