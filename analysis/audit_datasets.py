"""Independent source-data audit of the Austin Animal Center intake and outcome files.

Run from the repository root:
    python analysis/audit_datasets.py

Reads data/raw/*.csv (read-only), verifies their checksums, and writes:
    data/processed/intakes_clean.csv, data/processed/outcomes_clean.csv
    outputs/audit/*.csv   (profiles, distributions, exception records)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (  # noqa: E402
    metrics_frame,
    CHECKSUM_FILE, EXTRACT_END, INTAKE_FILE, OUT_AUDIT, OUTCOME_FILE, PROCESSED_DIR, REPO_ROOT,
    build_intakes, build_outcomes, ensure_dirs, read_raw, sha256, write_csv,
)
from matching_engine import sequencing_key  # noqa: E402

CATEGORICAL = {
    "intakes": ["Intake Type", "Intake Condition", "Animal Type", "Sex upon Intake", "Age upon Intake"],
    "outcomes": ["Outcome Type", "Outcome Subtype", "Animal Type", "Sex upon Outcome", "Age upon Outcome"],
}
# Labels that are distinct strings but plausibly overlapping in meaning.
# Recorded for review; NOT merged in the derived data (D-014).
SEMANTIC_REVIEW = [
    ("intakes", "Intake Condition", ["Medical", "Med Attn", "Med Urgent"], "Medical-need labels of differing urgency; definitions not published in the extract"),
    ("intakes", "Intake Condition", ["Neonatal", "Nursing"], "Life-stage labels used as a 'condition'"),
    ("intakes", "Intake Condition", ["Sick", "Parvo", "Panleuk", "Neurologic"], "Specific diseases coexist with the generic 'Sick'"),
    ("intakes", "Intake Condition", ["Unknown", "Other", "Space"], "Non-clinical / indeterminate labels"),
    ("outcomes", "Outcome Type", ["Return to Owner", "Rto-Adopt"], "Rto-Adopt: owner reclaim processed as an adoption; grouped with RTO"),
    ("outcomes", "Outcome Type", ["Missing", "Lost", "Stolen"], "Animal left custody without a placement"),
    ("outcomes", "Outcome Subtype", ["Emergency", "Emer"], "Abbreviation variant"),
    ("outcomes", "Outcome Subtype", ["Foster", "In Foster"], "Foster as adoption/transfer subtype vs location while died/missing"),
    ("outcomes", "Outcome Subtype", ["Snr", "SCRP"], "Community-cat return programmes (spelling/case conventions differ)"),
]


EXPORT_DROP = ["intake_datetime_raw", "outcome_datetime_raw", "monthyear_raw", "exact_duplicate_group_size"]


def verify_checksums() -> pd.DataFrame:
    rows = []
    for p in (INTAKE_FILE, OUTCOME_FILE):
        rows.append({"file": str(p.relative_to(REPO_ROOT)), "bytes": p.stat().st_size, "sha256": sha256(p)})
    cur = pd.DataFrame(rows)
    if CHECKSUM_FILE.exists():
        ref = pd.read_csv(CHECKSUM_FILE)
        merged = cur.merge(ref, on="file", suffixes=("", "_ref"))
        bad = merged[merged["sha256"] != merged["sha256_ref"]]
        if len(merged) != len(cur) or not bad.empty:
            raise SystemExit(f"Source checksum mismatch - raw data changed:\n{bad}")
    else:
        write_csv(cur, CHECKSUM_FILE)
    return cur


def infer_type(s: pd.Series) -> str:
    v = s[s != ""]
    if v.empty:
        return "empty"
    if v.str.fullmatch(r"-?\d+").all():
        return "integer"
    if v.str.fullmatch(r"\d{4}-\d{2}-\d{2}").all():
        return "date (YYYY-MM-DD)"
    if v.str.fullmatch(r"\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2} [AP]M").all():
        return "datetime (MM/DD/YYYY hh:mm:ss AM/PM)"
    if v.str.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}([+-]\d{2}:\d{2})?").all():
        return "datetime (ISO-8601, offset on some rows)"
    if v.str.fullmatch(r"[A-Z][a-z]+ \d{4}").all():
        return "month-year text (Month YYYY)"
    if v.str.fullmatch(r"\d{2}-\d{4}").all():
        return "month-year text (MM-YYYY)"
    if v.str.fullmatch(r"-?\d+ (day|week|month|year)s?").all():
        return "age text (N unit)"
    if v.str.fullmatch(r"A\d{6}").all():
        return "identifier (A + 6 digits)"
    return "text / categorical"


def column_profile(name: str, raw: pd.DataFrame) -> pd.DataFrame:
    rows = []
    n = len(raw)
    for c in raw.columns:
        s = raw[c]
        empty = int((s == "").sum())
        null_tok = int((s.str.strip() == "NULL").sum())
        unknown = int((s.str.strip().str.lower() == "unknown").sum())
        top = s.value_counts().head(5)
        rows.append({
            "dataset": name, "column": c, "inferred_type": infer_type(s), "rows": n,
            "empty_string": empty, "null_token": null_tok, "missing_total": empty + null_tok,
            "missing_pct": round((empty + null_tok) / n * 100, 3),
            "unknown_label": unknown, "distinct_values": int(s.nunique()),
            "leading_trailing_whitespace": int((s != s.str.strip()).sum()),
            "repeated_internal_spaces": int(s.str.contains(r"\s{2,}", regex=True).sum()),
            "top_values": "; ".join(f"{k!r}={v}" for k, v in top.items()),
        })
    return pd.DataFrame(rows)


def categorical_distributions(name: str, raw: pd.DataFrame, cols: list) -> pd.DataFrame:
    out = []
    for c in cols:
        vc = raw[c].replace("", "(blank)").value_counts()
        out.append(pd.DataFrame({"dataset": name, "column": c, "value": vc.index, "rows": vc.values,
                                 "pct_of_rows": (vc.values / len(raw) * 100).round(3)}))
    return pd.concat(out, ignore_index=True)


def label_variants(name: str, raw: pd.DataFrame) -> pd.DataFrame:
    """Distinct labels that collapse to the same key after case/space/punct normalisation."""
    out = []
    for c in raw.columns:
        if c in ("Animal ID", "DateTime", "Date of Birth", "MonthYear", "Age upon Intake", "Age upon Outcome"):
            continue
        vc = raw[c].value_counts()
        if len(vc) > 5000:
            continue
        key = vc.index.to_series().str.lower().str.replace(r"[^a-z0-9]", "", regex=True)
        g = pd.DataFrame({"value": vc.index, "rows": vc.values, "key": key.values})
        multi = g[g.duplicated("key", keep=False)]
        for k, grp in multi.groupby("key"):
            out.append({"dataset": name, "column": c, "normalised_key": k, "n_variants": len(grp),
                        "variants": " | ".join(f"{v!r} ({r})" for v, r in zip(grp["value"], grp["rows"])),
                        "rows": int(grp["rows"].sum())})
    return pd.DataFrame(out, columns=["dataset", "column", "normalised_key", "n_variants", "variants", "rows"])


def id_frequency(name: str, ids: pd.Series) -> pd.DataFrame:
    per = ids.value_counts()
    dist = per.value_counts().sort_index()
    return pd.DataFrame({"dataset": name, "events_per_animal_id": dist.index, "animal_ids": dist.values,
                         "rows": dist.index * dist.values})


def suspected_duplicates(I: pd.DataFrame, O: pd.DataFrame) -> pd.DataFrame:
    """Consecutive same-kind events (no opposite event between) less than 24h apart."""
    ie = I.loc[~I["is_exact_duplicate"], ["intake_event_id", "animal_id", "intake_datetime", "intake_type"]]
    oe = O.loc[~O["is_exact_duplicate"], ["outcome_event_id", "animal_id", "outcome_datetime", "outcome_type"]]
    s = pd.concat([
        pd.DataFrame({"animal_id": ie["animal_id"], "event_id": ie["intake_event_id"], "kind": "Intake",
                      "dt": ie["intake_datetime"], "seq": ie["intake_datetime"], "label": ie["intake_type"]}),
        pd.DataFrame({"animal_id": oe["animal_id"], "event_id": oe["outcome_event_id"], "kind": "Outcome",
                      "dt": oe["outcome_datetime"], "seq": sequencing_key(oe["outcome_datetime"]),
                      "label": oe["outcome_type"]}),
    ])
    s["k"] = (s["kind"] == "Outcome").astype(int)
    s = s.sort_values(["animal_id", "seq", "k", "event_id"]).reset_index(drop=True)
    g = s.groupby("animal_id")
    prev = pd.DataFrame({c: g[c].shift() for c in ("event_id", "kind", "dt", "label")})
    gap_h = (s["dt"] - prev["dt"]).dt.total_seconds() / 3600
    m = (s["kind"] == prev["kind"]) & (gap_h.abs() < 24)
    r = pd.DataFrame({
        "animal_id": s.loc[m, "animal_id"], "event_kind": s.loc[m, "kind"],
        "earlier_event_id": prev.loc[m, "event_id"], "later_event_id": s.loc[m, "event_id"],
        "earlier_datetime": prev.loc[m, "dt"], "later_datetime": s.loc[m, "dt"],
        "gap_hours": gap_h[m].round(3), "earlier_label": prev.loc[m, "label"], "later_label": s.loc[m, "label"],
    })
    r["same_label"] = r["earlier_label"] == r["later_label"]
    r["same_timestamp"] = r["gap_hours"] == 0
    return r.reset_index(drop=True)


def conflict_detail(raw: pd.DataFrame, derived: pd.DataFrame, id_event: str) -> pd.DataFrame:
    """Same Animal ID + timestamp, differing in other columns: which columns differ."""
    d = derived[derived["is_same_id_timestamp_conflict"]]
    r = raw.loc[d.index].copy()
    r.insert(0, id_event, d[id_event])
    diffs = r.groupby(["Animal ID", "DateTime"]).agg(lambda x: x.nunique() > 1)
    cols = [c for c in raw.columns if c not in ("Animal ID", "DateTime")]
    r["differing_columns"] = r.set_index(["Animal ID", "DateTime"]).index.map(
        lambda k: ", ".join(c for c in cols if diffs.loc[k, c]))
    return r.sort_values(["Animal ID", "DateTime"]).reset_index(drop=True)


def date_quality(I: pd.DataFrame, O: pd.DataFrame, Iraw, Oraw) -> pd.DataFrame:
    rows = []

    def add(ds, metric, value, note=""):
        rows.append({"dataset": ds, "metric": metric, "value": value, "note": note})

    for ds, d, col in (("intakes", I, "intake_datetime"), ("outcomes", O, "outcome_datetime")):
        add(ds, "timestamp parse failures", int(d[col].isna().sum()))
        add(ds, "min timestamp", d[col].min().strftime("%Y-%m-%d %H:%M:%S"), "source-local wall clock")
        add(ds, "max timestamp", d[col].max().strftime("%Y-%m-%d %H:%M:%S"))
        add(ds, "timestamps after extract end", int((d[col] > EXTRACT_END).sum()))
        add(ds, "MonthYear inconsistent with timestamp", int((~d["monthyear_consistent"]).sum()))
        add(ds, "timestamps exactly 00:00:00", int((d[col].dt.strftime("%H:%M:%S") == "00:00:00").sum()))
        add(ds, "timestamps with non-zero seconds", int((d[col].dt.second != 0).sum()))
        yr = d[col].dt.year
        add(ds, "first year coverage", f"{d[col].min():%Y-%m-%d} to {yr.min()}-12-31", "partial year")
        add(ds, "last year coverage", f"{yr.max()}-01-01 to {d[col].max():%Y-%m-%d}", "partial year")
    add("intakes", "timestamp format", "MM/DD/YYYY hh:mm:ss AM/PM, no offset", "100% of rows")
    off = O["outcome_tz_offset"].value_counts(dropna=False)
    for k, v in off.items():
        add("outcomes", f"offset {k if isinstance(k, str) else 'none'}", int(v))
    od = O[O["outcome_time_is_date_only"]]
    add("outcomes", "offset rows at exactly 00:00:00", int(od["outcome_is_midnight"].sum()),
        "all offset rows are midnight -> date-only records")
    m = od["outcome_datetime"].dt.month
    add("outcomes", "offset -05:00 rows in Nov-Feb (CST months, true offset -06:00)",
        int(m.isin([11, 12, 1, 2]).sum()), "offset is not a reliable timezone")
    add("outcomes", "date of birth parse failures", int(O["date_of_birth"].isna().sum()))
    add("outcomes", "date of birth after outcome date", int(O["dob_after_outcome"].sum()))
    add("outcomes", "date of birth range",
        f"{O['date_of_birth'].min():%Y-%m-%d} to {O['date_of_birth'].max():%Y-%m-%d}")
    return pd.DataFrame(rows)


def age_exceptions(I: pd.DataFrame, O: pd.DataFrame) -> pd.DataFrame:
    a = I[I["age_upon_intake_invalid"]][["intake_event_id", "animal_id", "intake_datetime", "age_upon_intake_raw"]]
    a = a.rename(columns={"intake_event_id": "event_id", "intake_datetime": "event_datetime",
                          "age_upon_intake_raw": "age_raw"}).assign(dataset="intakes", issue="negative or unparseable age")
    b = O[O["age_upon_outcome_invalid"]][["outcome_event_id", "animal_id", "outcome_datetime", "age_upon_outcome_raw",
                                         "date_of_birth"]]
    b = b.rename(columns={"outcome_event_id": "event_id", "outcome_datetime": "event_datetime",
                          "age_upon_outcome_raw": "age_raw"}).assign(dataset="outcomes", issue="negative or unparseable age")
    c = O[O["dob_after_outcome"]][["outcome_event_id", "animal_id", "outcome_datetime", "age_upon_outcome_raw",
                                  "date_of_birth"]]
    c = c.rename(columns={"outcome_event_id": "event_id", "outcome_datetime": "event_datetime",
                          "age_upon_outcome_raw": "age_raw"}).assign(dataset="outcomes", issue="date of birth after outcome date")
    return pd.concat([a, b, c], ignore_index=True)


def main() -> dict:
    ensure_dirs()
    checks = verify_checksums()
    Iraw, Oraw = read_raw(INTAKE_FILE), read_raw(OUTCOME_FILE)
    I, O = build_intakes(Iraw), build_outcomes(Oraw)

    # file-level profile
    prof = []
    for ds, raw, d, col in (("intakes", Iraw, I, "intake_datetime"), ("outcomes", Oraw, O, "outcome_datetime")):
        prof.append({"dataset": ds, "rows": len(raw), "columns": raw.shape[1],
                     "exact_duplicate_excess_rows": int(d["is_exact_duplicate"].sum()),
                     "exact_duplicate_groups": int(raw[raw.duplicated(keep=False)].drop_duplicates().shape[0]),
                     "rows_after_exact_dedup": int((~d["is_exact_duplicate"]).sum()),
                     "unique_animal_ids": int(d["animal_id"].nunique()),
                     "animal_ids_with_2plus_rows": int((d["animal_id"].value_counts() > 1).sum()),
                     "rows_belonging_to_repeated_ids": int(d["animal_id"].map(d["animal_id"].value_counts()).gt(1).sum()),
                     "same_id_timestamp_conflict_rows": int(d["is_same_id_timestamp_conflict"].sum()),
                     "min_datetime": d[col].min(), "max_datetime": d[col].max()})
    prof = pd.DataFrame(prof).merge(
        checks.assign(dataset=["intakes", "outcomes"])[["dataset", "file", "bytes", "sha256"]], on="dataset")
    write_csv(prof, OUT_AUDIT / "source_file_profile.csv")

    write_csv(pd.concat([column_profile("intakes", Iraw), column_profile("outcomes", Oraw)]),
              OUT_AUDIT / "column_profile.csv")
    write_csv(pd.concat([categorical_distributions("intakes", Iraw, CATEGORICAL["intakes"]),
                         categorical_distributions("outcomes", Oraw, CATEGORICAL["outcomes"])]),
              OUT_AUDIT / "categorical_distributions.csv")
    lv = pd.concat([label_variants("intakes", Iraw), label_variants("outcomes", Oraw)])
    write_csv(lv, OUT_AUDIT / "label_variants.csv")
    sem = []
    for ds, col, labels, note in SEMANTIC_REVIEW:
        raw = Iraw if ds == "intakes" else Oraw
        vc = raw[col].value_counts()
        sem.append({"dataset": ds, "column": col, "labels": " | ".join(f"{l} ({int(vc.get(l, 0))})" for l in labels),
                    "note": note, "action": "Retained as-is in derived data; review before grouping"})
    write_csv(pd.DataFrame(sem), OUT_AUDIT / "semantic_label_review.csv")

    write_csv(pd.concat([id_frequency("intakes", I["animal_id"]), id_frequency("outcomes", O["animal_id"])]),
              OUT_AUDIT / "animal_id_frequency.csv")

    ex_i = Iraw[Iraw.duplicated(keep=False)].assign(dataset="intakes", event_id=I["intake_event_id"],
                                                    is_excess_copy=I["is_exact_duplicate"])
    ex_o = Oraw[Oraw.duplicated(keep=False)].assign(dataset="outcomes", event_id=O["outcome_event_id"],
                                                    is_excess_copy=O["is_exact_duplicate"])
    write_csv(ex_i, OUT_AUDIT / "exact_duplicate_rows_intakes.csv")
    write_csv(ex_o, OUT_AUDIT / "exact_duplicate_rows_outcomes.csv")
    cf = pd.concat([conflict_detail(Iraw, I, "intake_event_id").assign(dataset="intakes"),
                    conflict_detail(Oraw, O, "outcome_event_id").assign(dataset="outcomes")], ignore_index=True)
    write_csv(cf, OUT_AUDIT / "same_id_timestamp_conflicts.csv")
    sd = suspected_duplicates(I, O)
    write_csv(sd, OUT_AUDIT / "suspected_duplicate_events.csv")

    write_csv(date_quality(I, O, Iraw, Oraw), OUT_AUDIT / "date_quality.csv")
    write_csv(age_exceptions(I, O), OUT_AUDIT / "age_and_dob_exceptions.csv")

    # cross-dataset consistency
    si, so = set(I["animal_id"]), set(O["animal_id"])
    cross = pd.DataFrame([
        {"metric": "Animal IDs in both datasets", "value": len(si & so)},
        {"metric": "Animal IDs only in intakes", "value": len(si - so)},
        {"metric": "Animal IDs only in outcomes", "value": len(so - si)},
        {"metric": "Intake rows whose Animal ID has no outcome", "value": int((~I["animal_id"].isin(so)).sum())},
        {"metric": "Outcome rows whose Animal ID has no intake", "value": int((~O["animal_id"].isin(si)).sum())},
        {"metric": "Animal IDs with >1 animal type across both files",
         "value": int(pd.concat([I[["animal_id", "animal_type"]], O[["animal_id", "animal_type"]]])
                      .drop_duplicates().groupby("animal_id").size().gt(1).sum())},
        {"metric": "Intake rows with Found Location ending '(TX)'",
         "value": int(I["found_location"].str.contains(r"\(TX\)$", regex=True, na=False).sum())},
        {"metric": "Intake rows with Found Location 'Outside Jurisdiction'",
         "value": int(I["found_location"].str.contains("Outside Jurisdiction", na=False).sum())},
        {"metric": "Names starting with '*' (intakes)", "value": int(I["name_has_asterisk"].sum())},
        {"metric": "Names starting with '*' (outcomes)", "value": int(O["name_has_asterisk"].sum())},
    ])
    write_csv(cross, OUT_AUDIT / "cross_dataset_consistency.csv")

    # summary of duplicate classes
    dup = pd.DataFrame([
        {"dataset": "intakes", "class": "Exact duplicate rows (excess copies)", "rows": int(I["is_exact_duplicate"].sum()),
         "treatment": "Excluded from analytic events; retained and flagged in cleaned file"},
        {"dataset": "outcomes", "class": "Exact duplicate rows (excess copies)", "rows": int(O["is_exact_duplicate"].sum()),
         "treatment": "Excluded from analytic events; retained and flagged in cleaned file"},
        {"dataset": "intakes", "class": "Same Animal ID + timestamp, other fields differ",
         "rows": int(I["is_same_id_timestamp_conflict"].sum()), "treatment": "Retained; flagged; see ambiguity list"},
        {"dataset": "outcomes", "class": "Same Animal ID + timestamp, other fields differ",
         "rows": int(O["is_same_id_timestamp_conflict"].sum()), "treatment": "Retained; flagged; see ambiguity list"},
        {"dataset": "intakes", "class": "Consecutive intakes < 24h apart, no outcome between (suspected duplicate event)",
         "rows": int((sd["event_kind"] == "Intake").sum()), "treatment": "Retained; resolved by matching rule"},
        {"dataset": "outcomes", "class": "Consecutive outcomes < 24h apart, no intake between (suspected duplicate event)",
         "rows": int((sd["event_kind"] == "Outcome").sum()), "treatment": "Retained; second becomes unmatched outcome"},
        {"dataset": "intakes", "class": "Repeat intake for the same Animal ID (legitimate repeat visits likely)",
         "rows": int(I.loc[~I["is_exact_duplicate"], "animal_id"].duplicated().sum()),
         "treatment": "Retained; each intake is a separate visit candidate"},
    ])
    write_csv(dup, OUT_AUDIT / "duplicate_summary.csv")

    # derived (cleaned) event tables
    # Raw-text copies of timestamps are omitted from the export to keep file size
    # manageable; every row is traceable to the raw file through `source_row`.
    write_csv(I.drop(columns=EXPORT_DROP, errors="ignore"), PROCESSED_DIR / "intakes_clean.csv")
    write_csv(O.drop(columns=EXPORT_DROP, errors="ignore"), PROCESSED_DIR / "outcomes_clean.csv")

    km = {
        "intake_rows": len(I), "outcome_rows": len(O),
        "intake_exact_dup_excess": int(I["is_exact_duplicate"].sum()),
        "outcome_exact_dup_excess": int(O["is_exact_duplicate"].sum()),
        "intake_unique_ids": int(I["animal_id"].nunique()), "outcome_unique_ids": int(O["animal_id"].nunique()),
        "intake_id_ts_conflicts": int(I["is_same_id_timestamp_conflict"].sum()),
        "outcome_id_ts_conflicts": int(O["is_same_id_timestamp_conflict"].sum()),
        "outcome_offset_rows": int(O["outcome_time_is_date_only"].sum()),
        "outcome_midnight_rows": int(O["outcome_is_midnight"].sum()),
        "intake_negative_age": int((I["age_upon_intake_days"] < 0).sum()),
        "outcome_negative_age": int((O["age_upon_outcome_days"] < 0).sum()),
        "outcome_age_unparseable": int(O["age_upon_outcome_days"].isna().sum()),
        "dob_after_outcome": int(O["dob_after_outcome"].sum()),
        "outcome_type_missing": int(O["outcome_type_missing"].sum()),
        "outcome_subtype_missing": int(O["outcome_subtype"].isna().sum()),
        "intake_name_missing": int(I["name"].isna().sum()), "outcome_name_missing": int(O["name"].isna().sum()),
        "suspected_dup_intake_events": int((sd["event_kind"] == "Intake").sum()),
        "suspected_dup_outcome_events": int((sd["event_kind"] == "Outcome").sum()),
    }
    write_csv(metrics_frame(km), OUT_AUDIT / "audit_key_metrics.csv")
    print(prof.T.to_string())
    print(pd.Series(km).to_string())
    print(dup.to_string())
    print(cross.to_string())
    print(lv.to_string())
    return km


if __name__ == "__main__":
    main()
