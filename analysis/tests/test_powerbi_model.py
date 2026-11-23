"""Power BI model foundation: data validations, M/DAX consistency and DAX design rules."""
import re

import pandas as pd
import pytest

import validate_powerbi_model as v

pytestmark = pytest.mark.skipif(not v.SOURCES["FactVisits"].exists(), reason="run analysis/run_all.py first")


@pytest.fixture(scope="module")
def checks():
    return v.run_checks()


def measure_bodies() -> dict:
    """{measure name: DAX expression text} parsed from the .dax files."""
    out = {}
    for f in v.DAX_FILES:
        if not f.endswith(".dax"):
            continue
        text = (v.DAX_DIR / f).read_text(encoding="utf-8").split("EVALUATE")[0]
        parts = re.split(r"\n\s*MEASURE\s+\w+\[([^\]]+)\]\s*=", text)
        for name, body in zip(parts[1::2], parts[2::2]):
            out[name] = re.sub(r"//[^\n]*", "", body)
    return out


def test_no_validation_failures(checks):
    failed = checks[checks["status"] == "FAIL"]
    assert failed.empty, failed[["check", "expected", "actual"]].to_string()


@pytest.mark.parametrize("check,expected", [
    ("FactIntakes rows (analytic events)", 173_776),
    ("FactOutcomes rows (analytic events)", 173_749),
    ("FactVisits rows (all statuses retained)", 174_978),
    ("FactVisits: Matched visit", 172_547),
    ("FactVisits: Intake without matched outcome", 1_229),
    ("FactVisits: Outcome without matched intake", 1_202),
    ("Median LOS (days, matched)", 6.0),
    ("P90 LOS (days, matched)", 55.56),
])
def test_reconciliation_targets(checks, check, expected):
    row = checks[checks["check"] == check].iloc[0]
    assert row["status"] == "PASS" and float(row["actual"]) == expected


def test_every_check_group_ran(checks):
    assert {"files", "columns", "types", "rows", "keys", "los", "dates", "dimensions", "visits",
            "artefacts", "sources", "dax_reference"} <= set(checks["check_group"])


def test_m_column_lists_parse():
    assert len(v.m_expected_columns("FactIntakes.m")) == 22
    assert len(v.m_expected_columns("FactOutcomes.m")) == 28
    assert len(v.m_expected_columns("FactVisits.m")) == 40
    added = v.m_added_columns("DimDate.m")
    for col in ["Year", "Month Number", "Month Name", "Month Short Name", "Quarter", "Year-Month",
                "Year-Month Sort", "Month-Year Display", "Day", "Day of Week", "Day of Week Number",
                "Is Full Calendar Year", "Is Partial Extract Year"]:
        assert col in added, col


def test_dimdate_rules():
    d = v.dimdate_frame()
    assert len(d) == 4_235 and d["Date"].is_monotonic_increasing and d["Date"].diff().dropna().dt.days.eq(1).all()
    assert not d.loc[d["Year"].isin([2013, 2025]), "Is Full Calendar Year"].any()
    assert not d.loc[d["Year"] == 2014, "Is YoY Comparable Year"].any()


def test_reason_codes_and_flags():
    assert v.reason_code("Animal ID has no outcome records") == "NO_OUTCOME_RECORDS"
    assert v.reason_code("Same-day time-reversed candidate pair (excluded ...)") == "REVERSED_CANDIDATE"
    assert v.reason_code("something new") == "OTHER" and v.reason_code(None) is None
    assert v.to_flag(pd.Series(["1", "0", None])).tolist()[:2] == [True, False]


def test_visit_measures_filter_status_explicitly():
    b = measure_bodies()
    for m in ["Matched Visits", "Median LOS (Days)", "Average LOS (Days)", "P90 LOS (Days)", "Visits Over 30 Days",
              "Visits Over 90 Days", "Visits Over 365 Days", "Same-Day Visits", "Long Stay Visits",
              "Method-Dependent Visits"]:
        assert 'FactVisits[visit_status] = "Matched visit"' in b[m], m
    assert "PERCENTILE.INC" in b["P90 LOS (Days)"]


def test_reversed_candidates_counted_once_per_pair():
    body = measure_bodies()["Same-Day Reversed Candidates"]
    assert 'visit_status] = "Intake without matched outcome"' in body
    assert "same_day_reversed_candidate] = TRUE" in body


def test_outcome_date_role_uses_inactive_relationship():
    b = measure_bodies()
    for m in ["Unmatched Outcome Events", "Matched Visits (by Outcome Date)"]:
        assert "USERELATIONSHIP ( DimDate[Date], FactVisits[outcome_date] )" in b[m], m


def test_time_intelligence_guards_partial_years():
    b = measure_bodies()
    for m in ["Intake Events PY", "Outcome Events PY"]:
        assert "[Is Comparable YoY Period]" in b[m] and "SAMEPERIODLASTYEAR" in b[m]
    assert "Is Complete Extract Day" in b["Is Comparable YoY Period"]


def test_relationship_spec_has_no_bidirectional_or_animal_id_joins():
    text = (v.DAX_DIR / "00_Model_Relationships.md").read_text(encoding="utf-8")
    table = [l for l in text.splitlines() if l.startswith("| R")]
    assert len(table) == 9
    assert all("| Single |" in l for l in table)
    assert not any("animal_id" in l for l in table)


def test_provisional_outcome_caveat_present():
    text = (v.DAX_DIR / "04_Outcome_Analysis.dax").read_text(encoding="utf-8")
    assert "NOT AUSTIN'S OFFICIAL LIVE-RELEASE RATE" in text


def test_intake_type_dimension(checks):
    names = ["DimIntakeType members", "intake_type values identical in FactIntakes and FactVisits",
             "FactIntakes[intake_type] has no blanks", "FactVisits[intake_type] blank only on outcome-only rows",
             "FactIntakes rows under a DimIntakeType member (none excluded)",
             "FactVisits rows under a member or the blank member (none excluded)",
             "Intake events by type = visit rows by intake type"]
    sub = checks[checks["check"].isin(names)]
    assert len(sub) == len(names) and (sub["status"] == "PASS").all()
    m = (v.PQ_DIR / "DimIntakeType.m").read_text(encoding="utf-8")
    assert "FactIntakes[intake_type], FactVisits[intake_type]" in m and "List.RemoveNulls" in m
    assert "FactOutcomes" not in m.split("let", 1)[1]  # not sourced from / related to outcomes
    assert "intake_type" in v.m_added_columns("DimIntakeType.m") or "[intake_type = text]" in m
