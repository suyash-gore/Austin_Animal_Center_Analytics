"""Validate the Power BI model foundation against the validated CSV outputs.

Run from the repository root (reads only; never modifies sources):
    python analysis/validate_powerbi_model.py

It reproduces the Power Query rules in pandas (blank -> null, explicit ISO date parsing, 1/0 flags,
exact-duplicate exclusion for the two event facts, no filtering of the visit fact), checks the M and
DAX source files for consistency with the data, and records reference values for every DAX measure
in an unfiltered context.

Output: outputs/powerbi/model_validation_summary.csv
        columns: check_group, check, expected, actual, status (PASS / FAIL / INFO), note
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import CHECKSUM_FILE, REPO_ROOT, sha256  # noqa: E402

PQ_DIR = REPO_ROOT / "powerbi" / "power_query"
DAX_DIR = REPO_ROOT / "powerbi" / "dax"
OUT_DIR = REPO_ROOT / "outputs" / "powerbi"
SUMMARY = OUT_DIR / "model_validation_summary.csv"

SOURCES = {
    "FactIntakes": REPO_ROOT / "data" / "processed" / "intakes_clean.csv",
    "FactOutcomes": REPO_ROOT / "data" / "processed" / "outcomes_clean.csv",
    "FactVisits": REPO_ROOT / "outputs" / "matching" / "candidate_visits.csv",
    "UnmatchedIntakes": REPO_ROOT / "outputs" / "matching" / "unmatched_intakes.csv",
    "UnmatchedOutcomes": REPO_ROOT / "outputs" / "matching" / "unmatched_outcomes.csv",
    "ScenarioComparison": REPO_ROOT / "outputs" / "sensitivity" / "scenario_comparison.csv",
}
M_FILES = ["RepoRoot.m", "FactIntakes.m", "FactOutcomes.m", "FactVisits.m", "DimDate.m", "DimAnimalType.m",
           "DimIntakeType.m"]
DAX_FILES = ["00_Model_Relationships.md", "01_Core_Measures.dax", "02_Time_Intelligence.dax",
             "03_Visit_Operations.dax", "04_Outcome_Analysis.dax", "05_Diagnostics.dax"]

# Validation targets (from the audit outputs; DECISION_LOG D-009, D-018). Not hardcoded in any measure.
EXPECTED = {
    "intake_events": 173_776, "outcome_events": 173_749, "intake_duplicates_excluded": 36,
    "outcome_duplicates_excluded": 26, "visit_rows": 174_978, "matched": 172_547,
    "unmatched_intake": 1_229, "unmatched_outcome": 1_202, "los_median": 6.00, "los_p90": 55.56,
    "reversed_pairs": 225, "date_start": "2013-10-01", "date_end": "2025-05-05", "date_days": 4_235,
}
REQUIRED_MEASURES = [
    "Total Intakes", "Total Outcomes", "Matched Visits", "Unmatched Intake Events", "Unmatched Outcome Events",
    "Distinct Animals Intake", "Distinct Animals Outcome",
    "Median LOS (Days)", "Average LOS (Days)", "P90 LOS (Days)", "Visits Over 30 Days", "Visits Over 90 Days",
    "Visits Over 365 Days", "Same-Day Visits", "Share of Matched Visits Over 30 Days",
    "Intake Events PY", "Intake Events YoY Change", "Intake Events YoY %",
    "Outcome Events PY", "Outcome Events YoY Change", "Outcome Events YoY %",
    "Adoption Outcomes", "Return to Owner Outcomes", "Transfer Outcomes", "Euthanasia Outcomes", "Died Outcomes",
    "Provisional Live Outcomes", "Provisional Non-Live Outcomes", "Indeterminate Outcomes",
    "Open Intake Visits", "Long Stay Visits", "Repeat Intake Visits", "Method-Dependent Visits",
    "Same-Day Reversed Candidates",
    "Visits Under 24 Hours", "Zero-Duration Visits (Diagnostic)", "LOS Floored to Zero (Diagnostic)",
    "Identical Timestamp Visits (Diagnostic)",
]
MATCHED, U_IN, U_OUT = "Matched visit", "Intake without matched outcome", "Outcome without matched intake"
REASON_CODES = [  # mirrors FactVisits.m
    ("Same-day time-reversed candidate", "REVERSED_CANDIDATE"), ("Animal ID has no outcome records", "NO_OUTCOME_RECORDS"),
    ("No outcome recorded after this intake", "NO_LATER_OUTCOME"), ("Superseded", "SUPERSEDED"),
    ("Later outcomes already assigned", "LATER_OUTCOMES_ASSIGNED"), ("Animal ID has no intake records", "NO_INTAKE_RECORDS"),
    ("No intake recorded before this outcome", "NO_EARLIER_INTAKE"), ("Preceding intake already closed", "EXTRA_OUTCOME"),
]


class Checks:
    def __init__(self):
        self.rows = []

    def add(self, group, check, expected, actual, ok=None, note=""):
        status = "INFO" if ok is None else ("PASS" if ok else "FAIL")
        self.rows.append({"check_group": group, "check": check, "expected": expected, "actual": actual,
                          "status": status, "note": note})

    def eq(self, group, check, expected, actual, note=""):
        self.add(group, check, expected, actual, expected == actual, note)

    def frame(self):
        return pd.DataFrame(self.rows)


# ----------------------------------------------------------------------------- parsing helpers
def read_text_csv(path: Path) -> pd.DataFrame:
    """Read every column as text; blank -> None (mirrors the M BlankToNull step)."""
    df = pd.read_csv(path, dtype=str, keep_default_na=False, na_filter=False)
    return df.where(df != "", None)


def m_expected_columns(m_file: str) -> list[str]:
    text = (PQ_DIR / m_file).read_text(encoding="utf-8")
    block = re.search(r"ExpectedColumns\s*=\s*\{(.*?)\}", text, re.S).group(1)
    return re.findall(r'"([^"]+)"', block)


def m_added_columns(m_file: str) -> list[str]:
    text = (PQ_DIR / m_file).read_text(encoding="utf-8")
    return re.findall(r'Table\.AddColumn\(\s*\w+\s*,\s*"([^"]+)"', text)


def parse_dates(s: pd.Series, fmt: str) -> tuple[pd.Series, int]:
    """Explicit-format parse; returns parsed series and number of non-null values that failed."""
    out = pd.to_datetime(s, format=fmt, errors="coerce")
    return out, int((s.notna() & out.isna()).sum())


def flag_values_ok(s: pd.Series) -> bool:
    return set(s.dropna().unique()) <= {"0", "1"}


def to_flag(s: pd.Series) -> pd.Series:
    return s.map({"1": True, "0": False})


def reason_code(r):
    if r is None or (isinstance(r, float) and pd.isna(r)):
        return None
    for prefix, code in REASON_CODES:
        if str(r).startswith(prefix):
            return code
    return "OTHER"


def dax_definitions() -> dict:
    """{measure name: (home table, file)} for every MEASURE in the .dax files."""
    defs = {}
    for f in DAX_FILES:
        if not f.endswith(".dax"):
            continue
        for table, name in re.findall(r"MEASURE\s+(\w+)\[([^\]]+)\]\s*=", (DAX_DIR / f).read_text(encoding="utf-8")):
            defs.setdefault(name, []).append((table, f))
    return defs


def dimdate_frame() -> pd.DataFrame:
    """Python equivalent of DimDate.m (used for date-range and YoY-rule checks)."""
    d = pd.DataFrame({"Date": pd.date_range(EXPECTED["date_start"], EXPECTED["date_end"], freq="D")})
    start, end = d["Date"].min(), d["Date"].max()
    years = d["Date"].dt.year
    full = years.map(lambda y: pd.Timestamp(y, 1, 1) >= start and pd.Timestamp(y, 12, 31) <= end)
    d["Year"] = years
    d["Is Full Calendar Year"] = full
    d["Is YoY Comparable Year"] = full & (years - 1).map(lambda y: pd.Timestamp(y, 1, 1) >= start
                                                         and pd.Timestamp(y, 12, 31) <= end)
    d["Is Jan to 04-May Window"] = (d["Date"].dt.month < 5) | ((d["Date"].dt.month == 5) & (d["Date"].dt.day <= 4))
    return d


# ----------------------------------------------------------------------------- checks
def run_checks() -> pd.DataFrame:
    c = Checks()

    # 1. files exist ------------------------------------------------------------------------
    for name, p in SOURCES.items():
        c.eq("files", f"source exists: {p.relative_to(REPO_ROOT)}", True, p.exists())
    for f in M_FILES:
        c.eq("files", f"Power Query file exists: {f}", True, (PQ_DIR / f).exists())
    for f in DAX_FILES:
        c.eq("files", f"DAX/model file exists: {f}", True, (DAX_DIR / f).exists())
    if not all(p.exists() for p in SOURCES.values()):
        return c.frame()

    I_raw = read_text_csv(SOURCES["FactIntakes"])
    O_raw = read_text_csv(SOURCES["FactOutcomes"])
    V = read_text_csv(SOURCES["FactVisits"])
    UI = read_text_csv(SOURCES["UnmatchedIntakes"])
    UO = read_text_csv(SOURCES["UnmatchedOutcomes"])

    # 2. columns: CSV header == ExpectedColumns declared in the M query ------------------------
    for table, df, m in (("FactIntakes", I_raw, "FactIntakes.m"), ("FactOutcomes", O_raw, "FactOutcomes.m"),
                         ("FactVisits", V, "FactVisits.m")):
        exp = m_expected_columns(m)
        c.eq("columns", f"{table}: CSV columns match M ExpectedColumns", exp, list(df.columns),
             "order and names")
    for name, df in (("unmatched_intakes", UI), ("unmatched_outcomes", UO)):
        c.eq("columns", f"{name}: has visit_id and unmatched_reason", True,
             {"visit_id", "unmatched_reason"} <= set(df.columns))

    # 3. typing rules (mirror M parsers) -----------------------------------------------------
    for table, df, dcols, dtcols in (
            ("FactIntakes", I_raw, ["intake_date"], ["intake_datetime"]),
            ("FactOutcomes", O_raw, ["outcome_date", "date_of_birth"], ["outcome_datetime"]),
            ("FactVisits", V, ["intake_date", "outcome_date"], ["intake_datetime", "outcome_datetime"])):
        for col in dcols:
            _, bad = parse_dates(df[col], "%Y-%m-%d")
            c.eq("types", f"{table}[{col}] parses as yyyy-MM-dd", 0, bad, "failures")
        for col in dtcols:
            _, bad = parse_dates(df[col], "%Y-%m-%d %H:%M:%S")
            c.eq("types", f"{table}[{col}] parses as yyyy-MM-dd HH:mm:ss", 0, bad, "failures")
    for table, df, m in (("FactIntakes", I_raw, "FactIntakes.m"), ("FactOutcomes", O_raw, "FactOutcomes.m"),
                         ("FactVisits", V, "FactVisits.m")):
        flag_cols = re.findall(r'\{"(\w+)", ParseFlag', (PQ_DIR / m).read_text(encoding="utf-8"))
        bad = [col for col in flag_cols if not flag_values_ok(df[col])]
        c.eq("types", f"{table}: all ParseFlag columns contain only 1/0/blank", [], bad)
        num_cols = re.findall(r'\{"(\w+)", Parse(?:Number|Int)', (PQ_DIR / m).read_text(encoding="utf-8"))
        bad = [col for col in num_cols if pd.to_numeric(df[col], errors="coerce").isna().sum() != df[col].isna().sum()]
        c.eq("types", f"{table}: all numeric columns parse", [], bad)

    # 4. duplicate exclusion and row totals -------------------------------------------------
    I = I_raw[I_raw["is_exact_duplicate"] != "1"]
    O = O_raw[O_raw["is_exact_duplicate"] != "1"]
    c.eq("rows", "FactIntakes: exact duplicates excluded", EXPECTED["intake_duplicates_excluded"], len(I_raw) - len(I))
    c.eq("rows", "FactOutcomes: exact duplicates excluded", EXPECTED["outcome_duplicates_excluded"], len(O_raw) - len(O))
    c.eq("rows", "FactIntakes rows (analytic events)", EXPECTED["intake_events"], len(I))
    c.eq("rows", "FactOutcomes rows (analytic events)", EXPECTED["outcome_events"], len(O))
    c.eq("rows", "FactIntakes: no is_exact_duplicate = 1 remains", 0, int((I["is_exact_duplicate"] == "1").sum()))
    c.eq("rows", "FactOutcomes: no is_exact_duplicate = 1 remains", 0, int((O["is_exact_duplicate"] == "1").sum()))
    c.eq("rows", "FactVisits rows (all statuses retained)", EXPECTED["visit_rows"], len(V))
    vc = V["visit_status"].value_counts()
    c.eq("rows", "FactVisits: Matched visit", EXPECTED["matched"], int(vc.get(MATCHED, 0)))
    c.eq("rows", "FactVisits: Intake without matched outcome", EXPECTED["unmatched_intake"], int(vc.get(U_IN, 0)))
    c.eq("rows", "FactVisits: Outcome without matched intake", EXPECTED["unmatched_outcome"], int(vc.get(U_OUT, 0)))
    c.eq("rows", "FactVisits: no other visit_status values", [], sorted(set(vc.index) - {MATCHED, U_IN, U_OUT}))
    c.eq("rows", "Reconciliation: matched + unmatched intake rows = FactIntakes rows", len(I),
         int(vc.get(MATCHED, 0) + vc.get(U_IN, 0)))
    c.eq("rows", "Reconciliation: matched + unmatched outcome rows = FactOutcomes rows", len(O),
         int(vc.get(MATCHED, 0) + vc.get(U_OUT, 0)))

    # 5. keys ---------------------------------------------------------------------------------
    c.eq("keys", "FactIntakes[intake_event_id] unique and non-null", True,
         bool(I["intake_event_id"].notna().all() and I["intake_event_id"].is_unique))
    c.eq("keys", "FactOutcomes[outcome_event_id] unique and non-null", True,
         bool(O["outcome_event_id"].notna().all() and O["outcome_event_id"].is_unique))
    c.eq("keys", "FactVisits[visit_id] unique and non-null", True,
         bool(V["visit_id"].notna().all() and V["visit_id"].is_unique))
    M = V[V["visit_status"] == MATCHED]
    c.eq("keys", "Matched visits: intake_event_id unique", True, bool(M["intake_event_id"].is_unique))
    c.eq("keys", "Matched visits: outcome_event_id unique", True, bool(M["outcome_event_id"].is_unique))
    c.eq("keys", "FactVisits intake_event_id values all exist in FactIntakes", 0,
         int((~V["intake_event_id"].dropna().isin(I["intake_event_id"])).sum()))
    c.eq("keys", "FactVisits outcome_event_id values all exist in FactOutcomes", 0,
         int((~V["outcome_event_id"].dropna().isin(O["outcome_event_id"])).sum()))
    c.eq("keys", "Every analytic intake appears exactly once in FactVisits", True,
         bool(V["intake_event_id"].dropna().is_unique and set(V["intake_event_id"].dropna()) == set(I["intake_event_id"])))
    c.eq("keys", "Every analytic outcome appears exactly once in FactVisits", True,
         bool(V["outcome_event_id"].dropna().is_unique and set(V["outcome_event_id"].dropna()) == set(O["outcome_event_id"])))

    # 6. LOS ----------------------------------------------------------------------------------
    los = pd.to_numeric(M["los_days"])
    c.eq("los", "All matched visits have los_days", 0, int(los.isna().sum()))
    c.eq("los", "All matched los_days >= 0", 0, int((los < 0).sum()))
    c.eq("los", "Unmatched rows have no los_days", 0, int(V.loc[V["visit_status"] != MATCHED, "los_days"].notna().sum()))
    c.eq("los", "Median LOS (days, matched)", EXPECTED["los_median"], round(float(los.median()), 2),
         "MEDIAN; PERCENTILE.INC equivalent")
    c.eq("los", "P90 LOS (days, matched)", EXPECTED["los_p90"], round(float(los.quantile(0.9)), 2),
         "linear interpolation = PERCENTILE.INC")
    km = pd.read_csv(REPO_ROOT / "outputs" / "matching" / "matching_key_metrics.csv").set_index("metric")["value"]
    c.eq("los", "Median/P90 agree with outputs/matching/matching_key_metrics.csv",
         (float(km["los_p50"]), float(km["los_p90"])), (round(float(los.median()), 2), round(float(los.quantile(0.9)), 2)))
    sc = pd.read_csv(SOURCES["ScenarioComparison"]).set_index("scenario")
    c.eq("los", "Primary visits = sensitivity scenario A_excl_reversed",
         int(sc.loc["A_excl_reversed", "matched_visits"]), len(M))

    # 7. dates ----------------------------------------------------------------------------------
    D = dimdate_frame()
    c.eq("dates", "DimDate first date", EXPECTED["date_start"], D["Date"].min().strftime("%Y-%m-%d"))
    c.eq("dates", "DimDate last date", EXPECTED["date_end"], D["Date"].max().strftime("%Y-%m-%d"))
    c.eq("dates", "DimDate continuous day count", EXPECTED["date_days"], len(D))
    dm = (PQ_DIR / "DimDate.m").read_text(encoding="utf-8")
    c.eq("dates", "DimDate.m bounds match", True,
         "#date(2013, 10, 1)" in dm and "#date(2025, 5, 5)" in dm and "#date(2025, 5, 4)" in dm)
    lo, hi = D["Date"].min(), D["Date"].max()
    for table, df, col in (("FactIntakes", I, "intake_date"), ("FactOutcomes", O, "outcome_date"),
                           ("FactVisits", V, "intake_date"), ("FactVisits", V, "outcome_date")):
        d, _ = parse_dates(df[col], "%Y-%m-%d")
        d = d.dropna()
        c.eq("dates", f"{table}[{col}] within DimDate range", True, bool(d.min() >= lo and d.max() <= hi),
             f"{d.min():%d-%m-%Y} to {d.max():%d-%m-%Y}")
    c.eq("dates", "FactIntakes/FactOutcomes date keys have no blanks", (0, 0),
         (int(I["intake_date"].isna().sum()), int(O["outcome_date"].isna().sum())))
    c.eq("dates", "FactVisits blank intake_date only on outcome-only rows", True,
         bool((V["intake_date"].isna() == (V["visit_status"] == U_OUT)).all()))
    c.eq("dates", "FactVisits blank outcome_date only on intake-only rows", True,
         bool((V["outcome_date"].isna() == (V["visit_status"] == U_IN)).all()))
    c.eq("dates", "Full calendar years", list(range(2014, 2025)),
         sorted(D.loc[D["Is Full Calendar Year"], "Year"].unique().tolist()))
    c.eq("dates", "YoY-comparable full years", list(range(2015, 2025)),
         sorted(D.loc[D["Is YoY Comparable Year"], "Year"].unique().tolist()))

    # 8. animal type dimension compatibility ------------------------------------------------
    vals = {t: set(df["animal_type"].dropna()) for t, df in (("FactIntakes", I), ("FactOutcomes", O), ("FactVisits", V))}
    c.eq("dimensions", "animal_type has no blanks in any fact", (0, 0, 0),
         tuple(int(df["animal_type"].isna().sum()) for df in (I, O, V)))
    c.eq("dimensions", "animal_type values identical across facts", True,
         vals["FactIntakes"] == vals["FactOutcomes"] == vals["FactVisits"], ", ".join(sorted(vals["FactVisits"])))
    c.eq("dimensions", "DimAnimalType members", ["Bird", "Cat", "Dog", "Livestock", "Other"],
         sorted(set().union(*vals.values())))

    # 8b. intake type dimension: conformed domain, nothing excluded
    iv, vv = I["intake_type"], V["intake_type"]
    dom = set(iv.dropna()) | set(vv.dropna())
    c.eq("dimensions", "DimIntakeType members", ["Abandoned", "Euthanasia Request", "Owner Surrender",
                                                 "Public Assist", "Stray", "Wildlife"], sorted(dom))
    c.eq("dimensions", "intake_type values identical in FactIntakes and FactVisits", True,
         set(iv.dropna()) == set(vv.dropna()))
    c.eq("dimensions", "FactIntakes[intake_type] has no blanks", 0, int(iv.isna().sum()))
    c.eq("dimensions", "FactVisits[intake_type] blank only on outcome-only rows", True,
         bool((vv.isna() == (V["visit_status"] == U_OUT)).all()), f"{int(vv.isna().sum())} blank rows retained")
    c.eq("dimensions", "No leading/trailing whitespace in intake_type", 0,
         int(sum((s.dropna() != s.dropna().str.strip()).sum() for s in (iv, vv))))
    c.eq("dimensions", "FactIntakes rows under a DimIntakeType member (none excluded)", len(I),
         int(iv.isin(dom).sum()))
    c.eq("dimensions", "FactVisits rows under a member or the blank member (none excluded)", len(V),
         int(vv.isin(dom).sum() + vv.isna().sum()))
    c.eq("dimensions", "Intake events by type = visit rows by intake type", True,
         iv.value_counts().to_dict() == vv.value_counts().to_dict())

    # 9. unmatched reasons and reversed candidates --------------------------------------------
    R = pd.concat([UI[["visit_id", "unmatched_reason"]], UO[["visit_id", "unmatched_reason"]]])
    c.eq("visits", "Unmatched reason files: one row per visit_id", True, bool(R["visit_id"].is_unique))
    Vr = V.merge(R, on="visit_id", how="left")
    c.eq("visits", "Every unmatched row has a reason; matched rows none", True,
         bool(((Vr["visit_status"] != MATCHED) == Vr["unmatched_reason"].notna()).all()))
    codes = Vr["unmatched_reason"].map(reason_code)
    c.eq("visits", "All reasons map to a known code (no OTHER)", 0, int((codes == "OTHER").sum()))
    cand = to_flag(V["same_day_reversed_candidate"])
    c.eq("visits", "Reversed candidates: flagged rows", 2 * EXPECTED["reversed_pairs"], int(cand.sum()))
    c.eq("visits", "Reversed candidates: none are matched visits", 0, int((cand & (V["visit_status"] == MATCHED)).sum()))
    c.eq("visits", "Reversed candidate pairs (intake-only rows)", EXPECTED["reversed_pairs"],
         int((cand & (V["visit_status"] == U_IN)).sum()))
    cf = pd.read_csv(REPO_ROOT / "outputs" / "matching" / "same_day_reversed_candidates.csv")
    flagged_ids = set(V.loc[cand, "intake_event_id"].dropna()) | set(V.loc[cand, "outcome_event_id"].dropna())
    c.eq("visits", "Flagged events = events in same_day_reversed_candidates.csv", True,
         flagged_ids == set(cf["intake_event_id"]) | set(cf["outcome_event_id"]))

    # 10. M / DAX static consistency ---------------------------------------------------------
    for m in ("FactIntakes.m", "FactOutcomes.m"):
        t = (PQ_DIR / m).read_text(encoding="utf-8")
        c.eq("artefacts", f"{m}: filters is_exact_duplicate", True, "each [is_exact_duplicate] = false" in t)
    tv = (PQ_DIR / "FactVisits.m").read_text(encoding="utf-8")
    c.eq("artefacts", "FactVisits.m: no row filter (Table.SelectRows absent)", False, "Table.SelectRows" in tv)
    for m in ("FactIntakes.m", "FactOutcomes.m", "FactVisits.m"):
        t = (PQ_DIR / m).read_text(encoding="utf-8")
        c.eq("artefacts", f"{m}: UTF-8 + explicit ISO formats + RepoRoot path", True,
             "Encoding = 65001" in t and 'Format = "yyyy-MM-dd"' in t and "RepoRoot &" in t
             and "DateTimeZone" not in t)
    defs = dax_definitions()
    c.eq("artefacts", "All required DAX measures defined", [], [m for m in REQUIRED_MEASURES if m not in defs])
    c.eq("artefacts", "No DAX measure defined twice", [], sorted(k for k, v in defs.items() if len(v) > 1))
    cols = {
        "FactIntakes": set(m_expected_columns("FactIntakes.m")),
        "FactOutcomes": set(m_expected_columns("FactOutcomes.m")),
        "FactVisits": set(m_expected_columns("FactVisits.m")) | {"unmatched_reason", "unmatched_reason_code"},
        "DimDate": {"Date"} | set(m_added_columns("DimDate.m")),
        "DimAnimalType": {"Animal Type"} | set(m_added_columns("DimAnimalType.m")),
        "DimIntakeType": {"intake_type"} | set(m_added_columns("DimIntakeType.m")),
    }
    unknown = []
    for f in DAX_FILES:
        if not f.endswith(".dax"):
            continue
        for table, col in re.findall(r"\b(FactIntakes|FactOutcomes|FactVisits|DimDate|DimAnimalType|DimIntakeType)\[([^\]]+)\]",
                                     (DAX_DIR / f).read_text(encoding="utf-8")):
            if col not in cols[table] and col not in defs:
                unknown.append(f"{f}: {table}[{col}]")
    c.eq("artefacts", "DAX column references exist in the model", [], sorted(set(unknown)))
    dg = (DAX_DIR / "05_Diagnostics.dax").read_text(encoding="utf-8").split("EVALUATE")[0]
    c.eq("artefacts", "Diagnostics use strict == and the matched-visit filter", True,
         "FactVisits[los_days] == 0" in dg and "FactVisits[los_days] = 0" not in dg
         and dg.count('FactVisits[visit_status] = "Matched visit"') == 3)
    rel = (DAX_DIR / "00_Model_Relationships.md").read_text(encoding="utf-8")
    c.eq("artefacts", "Relationship spec has 9 relationships incl. inactive outcome_date and DimIntakeType",
         True, rel.count("| R") >= 9
         and "`DimIntakeType[intake_type]` | `FactIntakes[intake_type]` | 1 : * | Single | Yes" in rel
         and "`DimIntakeType[intake_type]` | `FactVisits[intake_type]` | 1 : * | Single | Yes" in rel and "`FactVisits[outcome_date]` | 1 : * | Single | **No**" in rel)

    # 11. sources not modified ----------------------------------------------------------------
    ref = pd.read_csv(CHECKSUM_FILE).set_index("file")["sha256"]
    for f, h in ref.items():
        c.eq("sources", f"raw file unchanged: {f}", h, sha256(REPO_ROOT / f))
    tracked = ["data", "outputs/matching", "outputs/sensitivity", "outputs/analysis", "outputs/audit"]
    try:
        r = subprocess.run(["git", "status", "--porcelain", "--", *tracked], cwd=REPO_ROOT,
                           capture_output=True, text=True, check=True)
        c.eq("sources", "validated inputs and outputs unchanged vs git HEAD", "", r.stdout.strip())
    except (OSError, subprocess.CalledProcessError) as e:
        c.add("sources", "validated inputs and outputs unchanged vs git HEAD", "", f"git unavailable: {e}", None)
    for name, p in SOURCES.items():
        c.add("sources", f"sha256 {p.relative_to(REPO_ROOT)}", "", sha256(p), None, "recorded for traceability")

    # 12. DAX reference values (unfiltered) and cross-checks ---------------------------------
    ref_rows = dax_reference(I, O, V, Vr.assign(unmatched_reason_code=codes), D)
    for name, (val, exp, note) in ref_rows.items():
        val = "BLANK" if val is None else val
        if exp is None:
            c.add("dax_reference", name, "", val, None, note)
        else:
            c.eq("dax_reference", name, exp, val, note)
    return c.frame()


def dax_reference(I, O, V, Vr, D) -> dict:
    """Expected unfiltered results of each DAX measure (value, cross-check value or None, note)."""
    M = V[V["visit_status"] == MATCHED]
    los = pd.to_numeric(M["los_days"])
    ak = pd.read_csv(REPO_ROOT / "outputs" / "analysis" / "analysis_key_metrics.csv").set_index("metric")["value"].astype(float)
    km = pd.read_csv(REPO_ROOT / "outputs" / "matching" / "matching_key_metrics.csv").set_index("metric")["value"].astype(float)
    ld = pd.read_csv(REPO_ROOT / "outputs" / "matching" / "los_distribution.csv").set_index("los_band")
    sc = pd.read_csv(SOURCES["ScenarioComparison"]).set_index("scenario")
    ann = pd.read_csv(REPO_ROOT / "outputs" / "analysis" / "annual_event_counts.csv").set_index("year")
    lfl = pd.read_csv(REPO_ROOT / "outputs" / "analysis" / "like_for_like_periods.csv")
    lfl = lfl[lfl["window"] == "01-01 to 04-05"].set_index("year")
    og = O["outcome_group"].value_counts()
    st = O["outcome_status_provisional"].value_counts()
    flag = lambda s: to_flag(s).fillna(False)  # noqa: E731
    r = {
        "Total Intakes": (len(I), None, ""), "Total Outcomes": (len(O), None, ""),
        "Distinct Animals Intake": (int(I["animal_id"].nunique()), 156_287, "audit unique IDs"),
        "Distinct Animals Outcome": (int(O["animal_id"].nunique()), 156_237, "audit unique IDs"),
        "Matched Visits": (len(M), None, ""),
        "Unmatched Intake Events": (int((V["visit_status"] == U_IN).sum()), None, ""),
        "Unmatched Outcome Events": (int((V["visit_status"] == U_OUT).sum()), None, "via USERELATIONSHIP outcome_date"),
        "Median LOS (Days)": (round(float(los.median()), 4), None, ""),
        "Average LOS (Days)": (round(float(los.mean()), 4), None, ""),
        "P90 LOS (Days)": (round(float(los.quantile(0.9)), 4), None, ""),
        "Visits Over 30 Days": (int((los > 30).sum()), None, ""),
        "Visits Over 90 Days": (int((los > 90).sum()), int(ak["visits_over_90d"]), "analysis_key_metrics"),
        "Visits Over 365 Days": (int((los > 365).sum()), int(ak["visits_over_365d"]), "analysis_key_metrics"),
        "Same-Day Visits": (int(flag(M["same_day_visit"]).sum()), int(km["same_day_visits"]),
                            "same calendar date; matching_key_metrics"),
        "Visits Under 24 Hours": (int((los < 1).sum()), int(ld.loc["Under 1 day", "visits"]),
                                  "LOS < 1 day; los_distribution"),
        "Zero-Duration Visits (Diagnostic)": (int((los == 0).sum()), int(sc.loc["A_excl_reversed", "zero_day_stays"]),
                                              "LOS exactly 0; scenario_comparison zero_day_stays"),
        "LOS Floored to Zero (Diagnostic)": (int(flag(M["los_floored_to_zero"]).sum()), int(km["los_floored_to_zero"]),
                                             "matching_key_metrics"),
        "Identical Timestamp Visits (Diagnostic)": (
            int((pd.to_datetime(M["outcome_datetime"]) == pd.to_datetime(M["intake_datetime"])).sum()),
            int((los == 0).sum()) - int(flag(M["los_floored_to_zero"]).sum()), "= zero-duration - floored"),
        "Blank-trap check: rows matching los_days = 0 if unmatched rows were not excluded": (
            int((los == 0).sum()) + int(V["los_days"].isna().sum()), None,
            "what a DAX '= 0' filter without the matched filter would return; must NOT be reported"),
        "Share of Matched Visits Over 30 Days": (round(float((los > 30).mean()), 6), None, ""),
        "Adoption Outcomes": (int(og.get("Adoption", 0)), None, "outcome events"),
        "Return to Owner Outcomes": (int(og.get("Return to Owner", 0)), None, "outcome events incl. Rto-Adopt"),
        "Transfer Outcomes": (int(og.get("Transfer", 0)), None, "outcome events"),
        "Euthanasia Outcomes": (int(og.get("Euthanasia", 0)), None, "outcome events"),
        "Died Outcomes": (int(og.get("Died", 0)), None, "outcome events"),
        "Provisional Live Outcomes": (int(st.get("Live outcome", 0)), None, "PROVISIONAL, not official live-release"),
        "Provisional Non-Live Outcomes": (int(st.get("Non-live outcome", 0)), None, "PROVISIONAL"),
        "Indeterminate Outcomes": (int(st.get("Other / indeterminate", 0)), None, "PROVISIONAL"),
        "Provisional Live Share of Matched Visits": (
            round(float((M["outcome_status_provisional"] == "Live outcome").mean() * 100), 2),
            float(ak["live_outcome_pct_provisional"]), "percent; analysis_key_metrics"),
        "Adoption Share of Matched Visits": (round(float((M["outcome_group"] == "Adoption").mean() * 100), 2),
                                             float(ak["adoption_share_pct"]), "percent; analysis_key_metrics"),
        "Open Intake Visits": (int(Vr["unmatched_reason_code"].isin(["NO_OUTCOME_RECORDS", "NO_LATER_OUTCOME"]).sum()),
                               None, ""),
        "Long Stay Visits": (int(flag(M["long_stay_365plus"]).sum()), None, "= Visits Over 365 Days"),
        "Repeat Intake Visits": (int((flag(V["is_return_intake"]) & (V["visit_status"] != U_OUT)).sum()),
                                 int(I.groupby("animal_id").cumcount().gt(0).sum()),
                                 "cross-check: 2nd+ analytic intakes per Animal ID"),
        "Method-Dependent Visits": (int(flag(M["assignment_method_dependent"]).sum()), None, ""),
        "Same-Day Reversed Candidates": (int((flag(V["same_day_reversed_candidate"]) & (V["visit_status"] == U_IN)).sum()),
                                         EXPECTED["reversed_pairs"], "pairs, counted once"),
    }
    # time intelligence: annual events and YoY at year level (guarded rule) + like-for-like window
    iy = pd.to_datetime(I["intake_date"]).dt.year.value_counts().sort_index()
    oy = pd.to_datetime(O["outcome_date"]).dt.year.value_counts().sort_index()
    for y in (2014, 2019, 2020, 2025):
        comparable = bool(D.loc[D["Year"] == y, "Is YoY Comparable Year"].all())
        yoy_i = round((iy[y] - iy[y - 1]) / iy[y - 1] * 100, 2) if comparable else None
        yoy_o = round((oy[y] - oy[y - 1]) / oy[y - 1] * 100, 2) if comparable else None
        r[f"Intake Events YoY % ({y})"] = (yoy_i, None if yoy_i is None else float(ann.loc[y, "intake_events_yoy_pct"]),
                                           "BLANK expected (partial year)" if not comparable else "annual_event_counts")
        r[f"Outcome Events YoY % ({y})"] = (yoy_o, None if yoy_o is None else float(ann.loc[y, "outcome_events_yoy_pct"]),
                                            "BLANK expected (partial year)" if not comparable else "annual_event_counts")
        r[f"Total Intakes ({y})"] = (int(iy[y]), int(ann.loc[y, "intake_events"]), "annual_event_counts")
    idt = pd.to_datetime(I["intake_date"])
    w = (idt.dt.month < 5) | ((idt.dt.month == 5) & (idt.dt.day <= 4))
    c25, c24 = int((w & (idt.dt.year == 2025)).sum()), int((w & (idt.dt.year == 2024)).sum())
    r["Intake Events (01-01 to 04-05) (2025)"] = (c25, int(lfl.loc[2025, "intake_events"]), "like_for_like_periods")
    r["Intake Events (01-01 to 04-05) PY (2025)"] = (c24, int(lfl.loc[2024, "intake_events"]), "like_for_like_periods")
    r["Intake Events (01-01 to 04-05) YoY % (2025)"] = (round((c25 - c24) / c24 * 100, 2),
                                                        float(lfl.loc[2025, "intake_events_yoy_pct"]), "percent")
    return r


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = run_checks()
    df["expected"] = df["expected"].astype(str)
    df["actual"] = df["actual"].astype(str)
    df.to_csv(SUMMARY, index=False, lineterminator="\n")
    counts = df["status"].value_counts().to_dict()
    print(df[df["status"] == "FAIL"].to_string() if counts.get("FAIL") else "All checks passed.")
    print(counts)
    return 1 if counts.get("FAIL") else 0


if __name__ == "__main__":
    sys.exit(main())
