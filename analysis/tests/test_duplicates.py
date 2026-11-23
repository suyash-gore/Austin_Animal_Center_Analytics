"""Exact duplicate rows vs same-ID/timestamp conflicts vs legitimate repeats."""
import pandas as pd

from common import flag_duplicates


def raw():
    return pd.DataFrame({
        "Animal ID": ["A1", "A1", "A1", "A2", "A2", "A3"],
        "DateTime": ["t1", "t1", "t1", "t1", "t1", "t9"],
        "Intake Type": ["Stray", "Stray", "Stray", "Stray", "Owner Surrender", "Stray"],
    })


def test_exact_duplicates_flag_only_excess_copies():
    f = flag_duplicates(raw(), "Animal ID", "DateTime")
    assert f["is_exact_duplicate"].tolist() == [False, True, True, False, False, False]
    assert f.loc[0, "exact_duplicate_group_size"] == 3


def test_conflicting_same_id_timestamp_rows_are_flagged_not_dropped():
    f = flag_duplicates(raw(), "Animal ID", "DateTime")
    assert f.loc[[3, 4], "is_same_id_timestamp_conflict"].all()
    assert not f.loc[[0, 1, 2, 5], "is_same_id_timestamp_conflict"].any()


def test_repeat_visits_are_not_duplicates():
    r = pd.DataFrame({"Animal ID": ["A1", "A1"], "DateTime": ["t1", "t2"], "Intake Type": ["Stray", "Stray"]})
    f = flag_duplicates(r, "Animal ID", "DateTime")
    assert not f["is_exact_duplicate"].any() and not f["is_same_id_timestamp_conflict"].any()
