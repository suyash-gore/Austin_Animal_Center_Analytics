"""Sensitivity outputs: consistency with the current results and safety properties."""
import pandas as pd
import pytest

from common import OUT_ANALYSIS, OUT_MATCH, REPO_ROOT

SENS = REPO_ROOT / "outputs" / "sensitivity"
pytestmark = pytest.mark.skipif(not (SENS / "scenario_comparison.csv").exists(),
                                reason="run analysis/sensitivity_analysis.py first")


@pytest.fixture(scope="module")
def comp():
    return pd.read_csv(SENS / "scenario_comparison.csv").set_index("scenario")


def test_current_scenario_reproduces_published_results(comp):
    km = pd.read_csv(OUT_MATCH / "matching_key_metrics.csv").set_index("metric")["value"].astype(float)
    ev = pd.read_csv(OUT_ANALYSIS / "analysis_key_metrics.csv").set_index("metric")["value"].astype(float)
    a = comp.loc["A_all_midnight_dateonly"]
    assert a["matched_visits"] == km["matched_visits"]
    assert a["matched_by_reversed_pass"] == km["matched_same_day_reversed_rule"] == 225
    assert a["unmatched_intakes"] == km["unmatched_intakes"] and a["unmatched_outcomes"] == km["unmatched_outcomes"]
    for p in ("p50", "p90", "p99"):
        assert a[f"los_{p}"] == km[f"los_{p}"]
    assert a["os_after_any_adoption_pct_2016_2024"] == ev["owner_surrender_after_adoption_pct_2016_2024"]
    assert a["returns_within_30d_pct_of_returns_all_years"] == ev["adoption_returns_within_30d_pct"]
    assert a["dog_median_avg_of_annual_2014_2019"] == ev["dog_median_2014_2019"]
    assert a["stray_dog_rto_2024"] == ev["stray_dog_rto_pct_2024"]


def test_every_scenario_is_one_to_one_and_non_overlapping(comp):
    assert (comp["intake_reused"] == 0).all() and (comp["overlapping_visits"] == 0).all()
    assert (comp["matched_visits"] + comp["unmatched_intakes"]).nunique() == 1
    assert (comp["matched_visits"] + comp["unmatched_outcomes"]).nunique() == 1
    assert comp.loc["C_strict", "negative_raw_duration_pairs"] == 0


def test_reversed_review_is_complete_and_not_marked_confirmed():
    r = pd.read_csv(SENS / "same_day_reversed_review.csv")
    assert len(r) == 225 and r["outcome_event_id"].is_unique and r["intake_event_id"].is_unique
    assert (r["outcome_before_intake_hours"] > 0).all()
    assert not r["review_assessment"].str.contains("^Confirmed", regex=True).any()
    assert r["review_reason"].notna().all()


def test_sensitivity_figures_quoted_correctly(comp):
    reg = (REPO_ROOT / "docs" / "BUSINESS_OPPORTUNITY_REGISTER.md").read_text()
    meth = (REPO_ROOT / "docs" / "VISIT_MATCHING_METHODOLOGY.md").read_text()
    a, x = comp.loc["A_all_midnight_dateonly"], comp.loc["A_excl_reversed"]
    for k in ("os_after_any_adoption_pct_2016_2024", "os_within_30d_pct_of_os_2016_2024",
              "os_within_7d_pct_of_os_2016_2024", "returns_within_30d_pct_of_returns_2016_2024",
              "dog_median_pooled_2014_2019", "dog_median_pooled_2023_2024",
              "dog_median_nonfoster_pooled_2023_2024"):
        assert f"{a[k]:.2f}" in reg, k
    assert f"{int(x['matched_visits']):,}" in meth and f"{x['los_p90']:.2f}" in meth
    assert "recent adoption" not in reg
