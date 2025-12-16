from aac.domain.history import HistoryEntry, History


def test_history_window_last_n():
    entries = [
        HistoryEntry(context="git", chosen="git status"),
        HistoryEntry(context="git ch", chosen="checkout"),
        HistoryEntry(context="git ch", chosen="cherry-pick"),
    ]

    window = History(entries=entries)

    last_two = window.last_n(2)

    assert len(last_two) == 2
    assert last_two[0].chosen == "checkout"
    assert last_two[1].chosen == "cherry-pick"

