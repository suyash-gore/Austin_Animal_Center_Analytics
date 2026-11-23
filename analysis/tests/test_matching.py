"""Visit-matching rules on small synthetic event streams."""
import pandas as pd
import pytest

from matching_engine import attach_times, reconcile_same_day_reversed, run_method, sequencing_key

CHRONO = ["fifo", "lifo", "adjacent"]


def pairs_set(p):
    return set(zip(p["intake_event_id"], p["outcome_event_id"]))


@pytest.mark.parametrize("method", CHRONO)
def test_simple_visit_matches(make_events, method):
    i = make_events([("I1", "A", "2020-01-01 10:00")])
    o = make_events([("O1", "A", "2020-01-05 10:00")])
    assert pairs_set(run_method(i, o, method)) == {("I1", "O1")}


@pytest.mark.parametrize("method", CHRONO)
def test_one_to_one_no_intake_reuse(make_events, method):
    i = make_events([("I1", "A", "2020-01-01 10:00")])
    o = make_events([("O1", "A", "2020-01-02 10:00"), ("O2", "A", "2020-01-03 10:00")])
    p = run_method(i, o, method)
    assert len(p) == 1 and p["intake_event_id"].is_unique and p["outcome_event_id"].is_unique


def test_asof_reuses_intakes_and_is_rejected(make_events):
    i = make_events([("I1", "A", "2020-01-01 10:00")])
    o = make_events([("O1", "A", "2020-01-02 10:00"), ("O2", "A", "2020-01-03 10:00")])
    p = run_method(i, o, "asof")
    assert len(p) == 2 and p["intake_event_id"].duplicated().any()


@pytest.mark.parametrize("method", CHRONO)
def test_no_negative_durations(make_events, method):
    i = make_events([("I1", "A", "2020-01-05 10:00"), ("I2", "A", "2020-02-01 10:00")])
    o = make_events([("O1", "A", "2020-01-01 10:00"), ("O2", "A", "2020-02-03 10:00")])
    p = attach_times(run_method(i, o, method), i, o)
    assert (p["los_days"] >= 0).all()
    assert "O1" not in set(p["outcome_event_id"])  # outcome before any intake stays unmatched
    expected = {"fifo": {("I1", "O2")}, "lifo": {("I2", "O2")}, "adjacent": {("I2", "O2")}}
    assert pairs_set(p) == expected[method]


def test_rank_join_can_create_negative_durations(make_events):
    i = make_events([("I1", "A", "2020-01-05 10:00")])
    o = make_events([("O1", "A", "2020-01-01 10:00")])
    p = attach_times(run_method(i, o, "rank"), i, o)
    assert (p["los_days"] < 0).all()


@pytest.mark.parametrize("method", CHRONO)
def test_unmatched_records_are_left_unmatched(make_events, method):
    i = make_events([("I1", "A", "2020-01-01 10:00"), ("I9", "Z", "2020-01-01 10:00")])
    o = make_events([("O0", "A", "2019-12-01 10:00"), ("O1", "A", "2020-01-02 10:00"), ("O8", "Y", "2020-01-01 00:00")])
    p = run_method(i, o, method)
    assert pairs_set(p) == {("I1", "O1")}
    assert "I9" not in set(p["intake_event_id"]) and "O0" not in set(p["outcome_event_id"])


@pytest.mark.parametrize("method", CHRONO)
def test_same_timestamp_is_a_zero_length_visit(make_events, method):
    i = make_events([("I1", "A", "2020-01-01 10:00")])
    o = make_events([("O1", "A", "2020-01-01 10:00")])
    p = attach_times(run_method(i, o, method), i, o)
    assert pairs_set(p) == {("I1", "O1")} and p["los_days"].iloc[0] == 0


def test_same_day_date_only_outcome_matches_with_precision_rule(make_events):
    i = make_events([("I1", "A", "2016-05-14 11:26")])
    o = make_events([("O1", "A", "2016-05-14 00:00")])  # date-only outcome
    assert run_method(i, o, "adjacent").empty  # strict rule cannot match
    o_seq = o.assign(dt=sequencing_key(o["dt"]))
    assert pairs_set(run_method(i, o_seq, "adjacent")) == {("I1", "O1")}


def test_same_day_time_reversed_second_pass(make_events):
    i = make_events([("I1", "A", "2020-03-01 15:00")])
    o = make_events([("O1", "A", "2020-03-01 09:00")])
    p1 = run_method(i, o, "adjacent")
    p2 = reconcile_same_day_reversed(p1, i, o)
    assert pairs_set(p2) == {("I1", "O1")}


def test_same_day_reversed_not_applied_across_days_or_intervening_events(make_events):
    i = make_events([("I1", "A", "2020-03-02 15:00"), ("I2", "B", "2020-03-01 15:00")])
    o = make_events([("O1", "A", "2020-03-01 09:00"), ("O2", "B", "2020-03-01 09:00"),
                     ("O3", "B", "2020-03-01 12:00")])
    # A: different day -> not paired. B: O3 lies between O2 and I2 -> O2 not paired; O3 is closest -> paired
    p2 = reconcile_same_day_reversed(run_method(i, o, "adjacent"), i, o)
    assert pairs_set(p2) == {("I2", "O3")}


def test_multiple_open_intakes_fifo_lifo_adjacent(make_events):
    # I1, I2 open, then O1, O2
    i = make_events([("I1", "A", "2020-01-01 10:00"), ("I2", "A", "2020-06-01 10:00")])
    o = make_events([("O1", "A", "2020-06-05 10:00"), ("O2", "A", "2020-06-10 10:00")])
    f, l, a = (run_method(i, o, m) for m in CHRONO)
    assert pairs_set(f) == {("I1", "O1"), ("I2", "O2")}      # overlapping visits
    assert pairs_set(l) == {("I2", "O1"), ("I1", "O2")}      # nested visits
    assert pairs_set(a) == {("I2", "O1")}                    # I1 superseded, O2 extra
    assert f["n_eligible"].max() == 2 and l["n_eligible"].max() == 2


def test_adjacent_never_produces_overlapping_visits(make_events):
    i = make_events([("I1", "A", "2020-01-01"), ("I2", "A", "2020-01-03"), ("I3", "A", "2020-02-01")])
    o = make_events([("O1", "A", "2020-01-04"), ("O2", "A", "2020-01-05"), ("O3", "A", "2020-02-02")])
    p = attach_times(run_method(i, o, "adjacent"), i, o).sort_values("intake_dt")
    assert (p["intake_dt"].iloc[1:].to_numpy() >= p["outcome_dt"].iloc[:-1].to_numpy()).all()


def test_repeat_visits_matched_in_order(make_events):
    i = make_events([("I1", "A", "2020-01-01"), ("I2", "A", "2020-03-01"), ("I3", "A", "2020-05-01")])
    o = make_events([("O1", "A", "2020-01-10"), ("O2", "A", "2020-03-10"), ("O3", "A", "2020-05-10")])
    for m in CHRONO:
        assert pairs_set(run_method(i, o, m)) == {("I1", "O1"), ("I2", "O2"), ("I3", "O3")}


def test_matching_is_deterministic_regardless_of_input_order(make_events):
    i = make_events([("I1", "A", "2020-01-01"), ("I2", "A", "2020-01-01"), ("I3", "B", "2020-01-01")])
    o = make_events([("O1", "A", "2020-01-02"), ("O2", "B", "2020-01-02")])
    for m in CHRONO:
        a = run_method(i, o, m)
        b = run_method(i.iloc[::-1], o.iloc[::-1], m)
        assert pairs_set(a) == pairs_set(b)
