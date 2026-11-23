"""Integration checks against the real source files and generated outputs.

These require the pipeline to have been run (python analysis/run_all.py).
"""
import pandas as pd
import pytest

from common import CHECKSUM_FILE, INTAKE_FILE, OUT_MATCH, OUTCOME_FILE, REPO_ROOT, sha256

VISITS = OUT_MATCH / "candidate_visits.csv"
needs_outputs = pytest.mark.skipif(not VISITS.exists(), reason="run analysis/run_all.py first")


def test_source_files_unchanged():
    ref = pd.read_csv(CHECKSUM_FILE).set_index("file")["sha256"]
    for p in (INTAKE_FILE, OUTCOME_FILE):
        assert sha256(p) == ref[str(p.relative_to(REPO_ROOT))]


@pytest.fixture(scope="module")
def visits():
    return pd.read_csv(VISITS, low_memory=False, parse_dates=["intake_datetime", "outcome_datetime"])


@pytest.fixture(scope="module")
def key_metrics():
    km = pd.read_csv(OUT_MATCH / "matching_key_metrics.csv").set_index("metric")["value"]
    return km.astype(float)


@needs_outputs
def test_accepted_visits_are_one_to_one(visits):
    m = visits[visits["visit_status"] == "Matched visit"]
    assert m["intake_event_id"].is_unique and m["outcome_event_id"].is_unique
    assert visits["visit_id"].is_unique
    # an event never appears both matched and unmatched
    assert visits["intake_event_id"].dropna().is_unique
    assert visits["outcome_event_id"].dropna().is_unique


@needs_outputs
def test_accepted_durations_non_negative_and_floors_documented(visits):
    m = visits[visits["visit_status"] == "Matched visit"]
    assert (m["los_days"] >= 0).all()
    floored = m[m["los_floored_to_zero"] == 1]
    assert floored["same_day_visit"].eq(1).all()  # flooring only ever applies to same-date events
    assert (floored["los_days_raw"] < 0).all()


@needs_outputs
def test_no_overlapping_visits_for_an_animal(visits):
    m = visits[visits["visit_status"] == "Matched visit"].sort_values(["animal_id", "intake_datetime"])
    prev_out = m.groupby("animal_id")["outcome_datetime"].shift()
    # next intake may start on the day an earlier outcome is recorded, never before it
    has_prev = prev_out.notna()
    assert (m.loc[has_prev, "intake_datetime"].dt.normalize() >= prev_out[has_prev].dt.normalize()).all()


@needs_outputs
def test_event_totals_reconcile(visits, key_metrics):
    vc = visits["visit_status"].value_counts()
    m, ui, uo = vc["Matched visit"], vc["Intake without matched outcome"], vc["Outcome without matched intake"]
    assert m + ui == key_metrics["analytic_intake_events"]
    assert m + uo == key_metrics["analytic_outcome_events"]
    assert key_metrics["analytic_intake_events"] + 36 == key_metrics["intake_rows"]
    assert key_metrics["analytic_outcome_events"] + 26 == key_metrics["outcome_rows"]
    assert len(pd.read_csv(OUT_MATCH / "unmatched_intakes.csv")) == ui
    assert len(pd.read_csv(OUT_MATCH / "unmatched_outcomes.csv")) == uo


@needs_outputs
def test_no_animal_type_mismatch(visits):
    assert visits["animal_type_mismatch"].sum() == 0


@needs_outputs
def test_key_metrics_reproducible_from_source(key_metrics):
    """Re-run the recommended method from the raw files and compare."""
    from common import load_clean
    from match_visits import event_frames, run_config

    I, O = load_clean()
    I, O = I[~I["is_exact_duplicate"]], O[~O["is_exact_duplicate"]]
    ie, oe, oe_seq = event_frames(I, O)
    p_all = run_config("adjacent_dp", ie, oe, oe_seq)
    p = p_all[p_all["match_rule"] == "chronological"]  # primary dataset excludes reversed candidates (D-018)
    assert len(p) == key_metrics["matched_visits"]
    assert (p_all["match_rule"] == "same_day_time_reversed").sum() == key_metrics["same_day_reversed_candidates_excluded"]
    from matching_engine import attach_times
    los = attach_times(p, ie, oe)["los_days"].clip(lower=0)
    assert round(los.median(), 2) == key_metrics["los_p50"]
    assert round(los.quantile(0.9), 2) == key_metrics["los_p90"]


@needs_outputs
def test_reversed_candidates_excluded_from_primary_and_flagged(visits):
    c = pd.read_csv(OUT_MATCH / "same_day_reversed_candidates.csv")
    assert len(c) == 225
    m = visits[visits["visit_status"] == "Matched visit"]
    assert not m["intake_event_id"].isin(c["intake_event_id"]).any()
    assert not m["outcome_event_id"].isin(c["outcome_event_id"]).any()
    assert (m["match_rule"] == "chronological").all()
    flagged = visits[visits["same_day_reversed_candidate"] == 1]
    assert len(flagged) == 450 and (flagged["visit_status"] != "Matched visit").all()
    assert set(flagged["candidate_partner_event_id"]) == set(c["intake_event_id"]) | set(c["outcome_event_id"])
