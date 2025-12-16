from aac.domain.history import History


def test_history_records_entries() -> None:
    history = History()

    history.record("he", "hello")
    history.record("he", "help")
    history.record("wo", "world")

    entries = history.entries()

    assert len(entries) == 3
    assert entries[0].prefix == "he"
    assert entries[0].value == "hello"
    assert entries[2].prefix == "wo"
    assert entries[2].value == "world"


def test_history_counts_by_prefix() -> None:
    history = History()

    history.record("he", "hello")
    history.record("he", "hello")
    history.record("he", "help")
    history.record("wo", "world")

    counts = history.counts_for_prefix("he")

    assert counts == {
        "hello": 2,
        "help": 1,
    }
