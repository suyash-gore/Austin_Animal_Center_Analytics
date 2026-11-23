"""Compare intake-outcome visit-matching methods and build the candidate visit table.

Run from the repository root:
    python analysis/match_visits.py

Outputs (outputs/matching/):
    method_comparison.csv          metrics per method and data stage
    method_pairwise_differences.csv assignment differences between methods
    candidate_visits.csv           recommended visit-level dataset (all events accounted for)
    unmatched_intakes.csv          intakes with no accepted outcome, with reason
    unmatched_outcomes.csv         outcomes with no accepted intake, with reason
    ambiguous_matches.csv          event streams for animals whose assignment is method-dependent
    los_percentiles.csv            LOS percentiles (recommended method, several scopes)
    los_distribution.csv           LOS bands
    preliminary_reconciliation.csv preliminary figures vs reproduced figures
    matching_key_metrics.csv       headline metrics used by tests and docs
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import EXTRACT_END, OUT_MATCH, ensure_dirs, load_clean, metrics_frame, write_csv  # noqa: E402
from matching_engine import (  # noqa: E402
    attach_times,
    reconcile_same_day_reversed,
    run_method,
    sequencing_key,
)

RECOMMENDED = "adjacent_dp"
# Primary (confirmed-match) dataset = chronological pass of adjacent_dp only. Pairs from the
# same-day time-reversed pass are kept as flagged candidates, not as matched visits (D-018).
PRIMARY_LABEL = "adjacent_dp_primary"
PCTS = [0.25, 0.5, 0.75, 0.9, 0.95, 0.99]
LOS_BANDS = [
    (-np.inf, 1, "Under 1 day"),
    (1, 7, "1-6 days"),
    (7, 30, "7-29 days"),
    (30, 90, "30-89 days"),
    (90, 180, "90-179 days"),
    (180, 365, "180-364 days"),
    (365, np.inf, "365+ days"),
]
LONG_STAY_DAYS = 365


def los_band(los: pd.Series) -> pd.Series:
    out = pd.Series(pd.NA, index=los.index, dtype=object)
    for lo, hi, lab in LOS_BANDS:
        out[(los >= lo) & (los < hi)] = lab
    return out


def event_frames(intakes: pd.DataFrame, outcomes: pd.DataFrame):
    ie = pd.DataFrame({"event_id": intakes["intake_event_id"], "animal_id": intakes["animal_id"],
                       "dt": intakes["intake_datetime"]})
    oe = pd.DataFrame({"event_id": outcomes["outcome_event_id"], "animal_id": outcomes["animal_id"],
                       "dt": outcomes["outcome_datetime"]})
    oe_seq = oe.assign(dt=sequencing_key(oe["dt"]))
    return ie, oe, oe_seq


def run_config(name: str, ie, oe, oe_seq) -> pd.DataFrame:
    """Run a named configuration; returns pairs with a `match_rule` column."""
    if name.endswith("_dp"):
        base = name[:-3]
        p1 = run_method(ie, oe_seq, base).assign(match_rule="chronological")
        p2 = reconcile_same_day_reversed(p1, ie, oe).assign(match_rule="same_day_time_reversed")
        return pd.concat([p1, p2], ignore_index=True)
    return run_method(ie, oe, name).assign(match_rule="chronological")


def intervening_intakes(pairs: pd.DataFrame, ie: pd.DataFrame) -> pd.Series:
    """Number of other intakes of the same animal strictly inside each pair's window."""
    m = pairs[["outcome_event_id", "intake_event_id", "animal_id", "intake_dt", "outcome_dt"]].merge(
        ie.rename(columns={"event_id": "x", "dt": "xdt"}), on="animal_id")
    end = sequencing_key(m["outcome_dt"])
    m = m[(m["xdt"] > m["intake_dt"]) & (m["xdt"] < end) & (m["x"] != m["intake_event_id"])]
    cnt = m.groupby("outcome_event_id").size()
    return pairs["outcome_event_id"].map(cnt).fillna(0).astype(int)


def metrics(name: str, stage: str, pairs: pd.DataFrame, ie, oe, types_i, types_o) -> dict:
    p = attach_times(pairs.drop(columns=[c for c in ("intake_dt", "outcome_dt") if c in pairs]), ie, oe)
    neg = p["los_days"] < 0
    los = p["los_days"].clip(lower=0) if name.endswith("_dp") else p["los_days"]
    q = los.quantile(PCTS)
    same_day = p["intake_dt"].dt.normalize() == p["outcome_dt"].dt.normalize()
    tmis = p["intake_event_id"].map(types_i) != p["outcome_event_id"].map(types_o)
    reuse = int(p["intake_event_id"].duplicated().sum())
    return {
        "stage": stage,
        "method": name,
        "intake_events": len(ie),
        "outcome_events": len(oe),
        "matched_pairs": len(p),
        "matched_same_day_reversed_rule": int((p["match_rule"] == "same_day_time_reversed").sum()),
        "unmatched_intakes": len(ie) - p["intake_event_id"].nunique(),
        "unmatched_outcomes": len(oe) - p["outcome_event_id"].nunique(),
        "reused_intake_assignments": reuse,
        "negative_duration_pairs": int(neg.sum()),
        "outcomes_with_multiple_open_intakes": int((p["n_eligible"].fillna(0) > 1).sum()),
        "pairs_spanning_another_intake": int((intervening_intakes(p, ie) > 0).sum()),
        "animal_type_mismatch_pairs": int(tmis.sum()),
        "same_day_pairs": int(same_day.sum()),
        "long_stay_pairs_365plus": int((los > LONG_STAY_DAYS).sum()),
        **{f"los_p{int(k*100)}": round(float(v), 2) for k, v in q.items()},
        "los_mean": round(float(los.mean()), 2),
        "los_max": round(float(los.max()), 2),
    }


def pairwise(a: str, b: str, pa: pd.DataFrame, pb: pd.DataFrame, animal_of: pd.Series,
             intake_dt: pd.Series) -> dict:
    sa = pa.set_index("outcome_event_id")["intake_event_id"]
    sb = pb.set_index("outcome_event_id")["intake_event_id"]
    common = sa.index.intersection(sb.index)
    changed = common[sa[common].to_numpy() != sb[common].to_numpy()]
    # substantive = the two assigned intakes have different timestamps (excludes
    # choices between same-Animal-ID records sharing an identical timestamp)
    subst = changed[intake_dt.reindex(sa[changed]).to_numpy() != intake_dt.reindex(sb[changed]).to_numpy()]
    only_a = sa.index.difference(sb.index)
    only_b = sb.index.difference(sa.index)
    affected = set(changed) | set(only_a) | set(only_b)
    ia = pa.set_index("intake_event_id")["outcome_event_id"]
    ib = pb.set_index("intake_event_id")["outcome_event_id"]
    ci = ia.index.intersection(ib.index)
    return {
        "method_a": a,
        "method_b": b,
        "outcomes_assigned_different_intake": len(changed),
        "substantive_changes_different_intake_time": len(subst),
        "animal_ids_affected_substantive": int(animal_of.reindex(list(subst)).nunique()),
        "intakes_assigned_different_outcome": int((ia[ci].to_numpy() != ib[ci].to_numpy()).sum()),
        "outcomes_matched_only_in_a": len(only_a),
        "outcomes_matched_only_in_b": len(only_b),
        "animal_ids_affected": int(animal_of.reindex(list(affected)).nunique()),
        "identical_pair_sets": len(affected) == 0,
    }


def build_visits(pairs, intakes, outcomes, ie, ambiguous_animals) -> pd.DataFrame:
    i_cols = ["intake_event_id", "animal_id", "intake_datetime", "intake_date", "intake_type",
              "intake_condition", "animal_type", "sex_upon_intake", "age_upon_intake_days",
              "age_band_intake", "breed", "breed_is_mix", "is_same_id_timestamp_conflict"]
    o_cols = ["outcome_event_id", "animal_id", "outcome_datetime", "outcome_date", "outcome_type",
              "outcome_subtype", "outcome_group", "outcome_status_provisional", "animal_type",
              "sex_upon_outcome", "age_upon_outcome_days", "outcome_is_midnight",
              "outcome_time_is_date_only", "date_of_birth"]
    I = intakes[i_cols].rename(columns={"animal_type": "animal_type_intake",
                                         "is_same_id_timestamp_conflict": "intake_id_timestamp_conflict"})
    O = outcomes[o_cols].rename(columns={"animal_type": "animal_type_outcome", "animal_id": "animal_id_outcome"})
    m = pairs[["intake_event_id", "outcome_event_id", "n_eligible", "match_rule"]]
    v = m.merge(I, on="intake_event_id", how="left").merge(O, on="outcome_event_id", how="left")
    v["visit_status"] = "Matched visit"
    # unmatched intakes and outcomes as rows so totals reconcile to events
    ui = I[~I["intake_event_id"].isin(pairs["intake_event_id"])].assign(
        visit_status="Intake without matched outcome", match_rule="unmatched")
    uo = O[~O["outcome_event_id"].isin(pairs["outcome_event_id"])].assign(
        visit_status="Outcome without matched intake", match_rule="unmatched")
    v = pd.concat([v, ui, uo], ignore_index=True)
    v["animal_id"] = v["animal_id"].fillna(v["animal_id_outcome"])
    v = v.drop(columns=["animal_id_outcome"])
    v["visit_id"] = np.where(v["intake_event_id"].notna(), "V-" + v["intake_event_id"].fillna(""),
                             "V-" + v["outcome_event_id"].fillna(""))
    v["animal_type"] = v["animal_type_intake"].fillna(v["animal_type_outcome"])
    v["animal_type_mismatch"] = (v["visit_status"] == "Matched visit") & (
        v["animal_type_intake"] != v["animal_type_outcome"])
    raw_los = (v["outcome_datetime"] - v["intake_datetime"]).dt.total_seconds() / 86400.0
    v["los_floored_to_zero"] = raw_los < 0
    v["los_days"] = raw_los.clip(lower=0)
    # raw (negative) duration retained only where it was floored, to keep the file compact
    v["los_days_raw"] = raw_los.where(raw_los < 0)
    v["same_day_visit"] = v["intake_date"] == v["outcome_date"]
    v["los_band"] = los_band(v["los_days"])
    v["long_stay_365plus"] = v["los_days"] > LONG_STAY_DAYS
    v["multiple_open_intakes"] = v["n_eligible"].fillna(0) > 1
    v["assignment_method_dependent"] = v["animal_id"].isin(ambiguous_animals)
    # intake age vs DOB-implied age at intake (DOB comes from the outcome record)
    dob_age = (v["intake_date"] - v["date_of_birth"]).dt.days
    v["intake_age_dob_gap_days"] = (v["age_upon_intake_days"] - dob_age).abs()
    # intake ordinal for the animal across all analytic intake events (repeat visits)
    ordinal = ie.sort_values(["animal_id", "dt", "event_id"]).assign(
        k=lambda d: d.groupby("animal_id").cumcount() + 1).set_index("event_id")["k"]
    v["animal_intake_ordinal"] = v["intake_event_id"].map(ordinal).astype("Int64")
    v["is_return_intake"] = v["animal_intake_ordinal"] > 1
    v["days_open_at_extract_end"] = np.where(
        v["visit_status"] == "Intake without matched outcome",
        (EXTRACT_END.normalize() - v["intake_date"]).dt.days, np.nan)
    v["matching_method"] = PRIMARY_LABEL
    order = ["visit_id", "visit_status", "matching_method", "match_rule", "animal_id",
             "intake_event_id", "outcome_event_id", "intake_datetime", "outcome_datetime",
             "intake_date", "outcome_date", "los_days", "los_days_raw",
             "los_floored_to_zero", "los_band", "same_day_visit", "long_stay_365plus",
             "animal_type", "animal_type_mismatch",
             "intake_type", "intake_condition", "outcome_type", "outcome_subtype", "outcome_group",
             "outcome_status_provisional", "age_upon_intake_days", "age_band_intake", "breed_is_mix",
             "animal_intake_ordinal", "is_return_intake", "multiple_open_intakes", "n_eligible",
             "assignment_method_dependent", "intake_id_timestamp_conflict", "outcome_is_midnight",
             "outcome_time_is_date_only", "intake_age_dob_gap_days", "days_open_at_extract_end"]
    # (same_day_reversed_candidate and candidate_partner_event_id are appended in main)
    return v[order].sort_values(["animal_id", "intake_datetime", "outcome_datetime"],
                                na_position="last", kind="mergesort").reset_index(drop=True)


def classify_unmatched(visits, ie, oe_seq, pairs):
    """Attach a reason to every unmatched intake and outcome (recommended method)."""
    first_out = oe_seq.groupby("animal_id")["dt"].min()
    last_out = oe_seq.groupby("animal_id")["dt"].max()
    first_in = ie.groupby("animal_id")["dt"].min()
    ui = visits[visits["visit_status"] == "Intake without matched outcome"].copy()
    # next event after this intake for the same animal
    nxt_in = ie.sort_values(["animal_id", "dt", "event_id"]).assign(
        nxt=lambda d: d.groupby("animal_id")["dt"].shift(-1)).set_index("event_id")["nxt"]
    ui["next_intake_datetime"] = ui["intake_event_id"].map(nxt_in)
    has_out = ui["animal_id"].isin(oe_seq["animal_id"])
    later_out = ui["intake_datetime"] <= ui["animal_id"].map(last_out)
    ui["unmatched_reason"] = np.select(
        [~has_out, ~later_out, ui["next_intake_datetime"].notna()],
        ["Animal ID has no outcome records",
         "No outcome recorded after this intake (open at extract end or outcome not recorded)",
         "Superseded: animal has a later intake before any outcome"],
        default="Later outcomes already assigned to later intakes",
    )
    uo = visits[visits["visit_status"] == "Outcome without matched intake"].copy()
    has_in = uo["animal_id"].isin(ie["animal_id"])
    seqd = sequencing_key(uo["outcome_datetime"])
    before = uo["animal_id"].map(first_in) <= seqd
    uo["unmatched_reason"] = np.select(
        [~has_in, ~before],
        ["Animal ID has no intake records",
         "No intake recorded before this outcome (intake may pre-date extract or be missing)"],
        default="Preceding intake already closed by an earlier outcome (extra/duplicate outcome)",
    )
    uo["is_first_event_for_animal"] = seqd <= uo["animal_id"].map(first_out)
    return ui, uo


def ambiguous_stream(animals, ie, oe, assignments: dict, intakes, outcomes) -> pd.DataFrame:
    a = ie[ie["animal_id"].isin(animals)].assign(event_kind="Intake")
    b = oe[oe["animal_id"].isin(animals)].assign(event_kind="Outcome")
    s = pd.concat([a, b], ignore_index=True)
    s = s.merge(intakes[["intake_event_id", "intake_type"]], left_on="event_id",
                right_on="intake_event_id", how="left").drop(columns="intake_event_id")
    s = s.merge(outcomes[["outcome_event_id", "outcome_type", "outcome_is_midnight"]], left_on="event_id",
                right_on="outcome_event_id", how="left").drop(columns="outcome_event_id")
    for name, p in assignments.items():
        fwd = dict(zip(p["intake_event_id"], p["outcome_event_id"]))
        rev = dict(zip(p["outcome_event_id"], p["intake_event_id"]))
        s[f"paired_event_{name}"] = s["event_id"].map(lambda e: fwd.get(e, rev.get(e)))
    s["kind_order"] = (s["event_kind"] == "Outcome").astype(int)
    s = s.sort_values(["animal_id", "dt", "kind_order", "event_id"]).drop(columns="kind_order")
    return s.rename(columns={"dt": "event_datetime"})


def main() -> dict:
    ensure_dirs()
    intakes, outcomes = load_clean()
    I_raw, O_raw = intakes, outcomes
    I_an = intakes[~intakes["is_exact_duplicate"]]
    O_an = outcomes[~outcomes["is_exact_duplicate"]]
    types_i = intakes.set_index("intake_event_id")["animal_type"]
    types_o = outcomes.set_index("outcome_event_id")["animal_type"]

    rows, results = [], {}
    for stage, (Ii, Oo) in {"raw_rows": (I_raw, O_raw), "exact_duplicates_removed": (I_an, O_an)}.items():
        ie, oe, oe_seq = event_frames(Ii, Oo)
        names = ["rank", "asof", "fifo", "lifo", "adjacent"]
        if stage == "exact_duplicates_removed":
            names += ["fifo_dp", "lifo_dp", "adjacent_dp"]
        for n in names:
            p = run_config(n, ie, oe, oe_seq)
            results[(stage, n)] = p
            rows.append(metrics(n, stage, p, ie, oe, types_i, types_o))
    comp = pd.DataFrame(rows)
    write_csv(comp, OUT_MATCH / "method_comparison.csv")

    # explain the raw -> dedup change (preliminary 172,205 -> 172,170)
    dup_i = set(I_raw.loc[I_raw["is_exact_duplicate"], "intake_event_id"])
    dup_o = set(O_raw.loc[O_raw["is_exact_duplicate"], "outcome_event_id"])
    dimp = []
    for n in ("fifo", "lifo", "adjacent"):
        pr, pd_ = results[("raw_rows", n)], results[("exact_duplicates_removed", n)]
        di, do = pr["intake_event_id"].isin(dup_i), pr["outcome_event_id"].isin(dup_o)
        keys_r = set(zip(pr["intake_event_id"], pr["outcome_event_id"]))
        keys_d = set(zip(pd_["intake_event_id"], pd_["outcome_event_id"]))
        dimp.append({
            "method": n,
            "raw_matches": len(pr), "dedup_matches": len(pd_), "net_change": len(pd_) - len(pr),
            "raw_pairs_dup_intake_and_dup_outcome": int((di & do).sum()),
            "raw_pairs_dup_intake_only": int((di & ~do).sum()),
            "raw_pairs_dup_outcome_only": int((~di & do).sum()),
            "raw_pairs_lost": len(keys_r - keys_d), "new_pairs_after_dedup": len(keys_d - keys_r),
            "dup_intake_rows_removed": len(dup_i), "dup_outcome_rows_removed": len(dup_o),
        })
    write_csv(pd.DataFrame(dimp), OUT_MATCH / "deduplication_impact.csv")
    print(pd.DataFrame(dimp).to_string())

    # pairwise differences (analytic stage)
    ie, oe, oe_seq = event_frames(I_an, O_an)
    animal_of = oe.set_index("event_id")["animal_id"]
    st = "exact_duplicates_removed"
    idt = ie.set_index("event_id")["dt"]
    pw = [pairwise(a, b, results[(st, a)], results[(st, b)], animal_of, idt) for a, b in [
        ("fifo", "lifo"), ("fifo", "adjacent"), ("lifo", "adjacent"),
        ("fifo_dp", "lifo_dp"), ("fifo_dp", "adjacent_dp"), ("lifo_dp", "adjacent_dp"),
        ("adjacent", "adjacent_dp"), ("rank", "fifo"),
    ]]
    pw = pd.DataFrame(pw)
    write_csv(pw, OUT_MATCH / "method_pairwise_differences.csv")

    # ambiguity: animals whose pair set differs between the three one-to-one dp methods,
    # or where an outcome had more than one open intake.
    cand = {k: results[(st, k)] for k in ("fifo_dp", "lifo_dp", "adjacent_dp")}
    sets = {k: set(zip(v["intake_event_id"], v["outcome_event_id"])) for k, v in cand.items()}
    diff_pairs = (sets["fifo_dp"] ^ sets["adjacent_dp"]) | (sets["lifo_dp"] ^ sets["adjacent_dp"])
    i_animal = ie.set_index("event_id")["animal_id"]
    amb = {i_animal[i] for i, _ in diff_pairs}
    for p in cand.values():
        amb |= set(p.loc[p["n_eligible"].fillna(0) > 1, "intake_event_id"].map(i_animal))
    amb_stream = ambiguous_stream(sorted(amb), ie, oe, cand, intakes, outcomes)
    write_csv(amb_stream, OUT_MATCH / "ambiguous_matches.csv")

    rec_all = results[(st, RECOMMENDED)]
    rec = rec_all[rec_all["match_rule"] == "chronological"]
    cands = rec_all[rec_all["match_rule"] == "same_day_time_reversed"]
    visits = build_visits(rec, I_an, O_an, ie, amb)
    partner = {**dict(zip(cands["intake_event_id"], cands["outcome_event_id"])),
               **dict(zip(cands["outcome_event_id"], cands["intake_event_id"]))}
    own = visits["intake_event_id"].fillna(visits["outcome_event_id"])
    visits["same_day_reversed_candidate"] = (visits["visit_status"] != "Matched visit") & own.isin(partner)
    visits["candidate_partner_event_id"] = own.map(partner).where(visits["same_day_reversed_candidate"])
    ui, uo = classify_unmatched(visits, ie, oe_seq, rec)
    for d in (ui, uo):
        d.loc[d["same_day_reversed_candidate"], "unmatched_reason"] = \
            "Same-day time-reversed candidate pair (excluded from primary; see same_day_reversed_candidates.csv)"
    cv = attach_times(cands, ie, oe).rename(columns={"intake_dt": "intake_datetime", "outcome_dt": "outcome_datetime"})
    cv["outcome_before_intake_hours"] = (-cv["los_days"] * 24).round(2)
    cv = cv.drop(columns=["los_days", "outcome_animal_id", "n_eligible"]).assign(
        status="Candidate - unconfirmed; excluded from primary matched visits")
    write_csv(cv, OUT_MATCH / "same_day_reversed_candidates.csv")
    full_mv = build_visits(rec_all, I_an, O_an, ie, amb).query("visit_status == 'Matched visit'")
    # breed/sex/name live in data/processed/*_clean.csv, joined by event ID
    write_csv(visits, OUT_MATCH / "candidate_visits.csv")
    write_csv(ui, OUT_MATCH / "unmatched_intakes.csv")
    write_csv(uo, OUT_MATCH / "unmatched_outcomes.csv")

    # LOS summaries on the recommended matched set
    mv = visits[visits["visit_status"] == "Matched visit"]
    scopes = {
        "All matched visits": mv,
        "Including 225 same-day reversed candidates (sensitivity)": full_mv,
        "Excluding same-day visits": mv[~mv["same_day_visit"]],
        "Excluding method-dependent assignments": mv[~mv["assignment_method_dependent"]],
    }
    for t in ("Dog", "Cat", "Other", "Bird", "Livestock"):
        scopes[f"Animal type: {t}"] = mv[mv["animal_type"] == t]
    lp = []
    for scope, d in scopes.items():
        q = d["los_days"].quantile(PCTS)
        lp.append({"scope": scope, "visits": len(d), **{f"p{int(k*100)}": round(float(x), 2) for k, x in q.items()},
                   "mean": round(float(d["los_days"].mean()), 2), "max": round(float(d["los_days"].max()), 2),
                   "same_day_visits": int(d["same_day_visit"].sum()),
                   "long_stays_365plus": int(d["long_stay_365plus"].sum())})
    write_csv(pd.DataFrame(lp), OUT_MATCH / "los_percentiles.csv")
    band_order = [b[2] for b in LOS_BANDS]
    ld = mv.groupby("los_band").size().reindex(band_order, fill_value=0).rename("visits").reset_index()
    ld["share_pct"] = (ld["visits"] / ld["visits"].sum() * 100).round(2)
    write_csv(ld, OUT_MATCH / "los_distribution.csv")

    # preliminary reconciliation
    c = comp.set_index(["stage", "method"])
    r, d = "raw_rows", "exact_duplicates_removed"
    recon = [
        ("Intake rows", 173812, len(I_raw), "Source row count"),
        ("Outcome rows", 173775, len(O_raw), "Source row count"),
        ("Unique Animal IDs - intakes", 156287, I_raw["animal_id"].nunique(), ""),
        ("Unique Animal IDs - outcomes", 156237, O_raw["animal_id"].nunique(), ""),
        ("Exact duplicate excess rows - intakes", 36, int(I_raw["is_exact_duplicate"].sum()), ""),
        ("Exact duplicate excess rows - outcomes", 26, int(O_raw["is_exact_duplicate"].sum()), ""),
        ("Sequence (derived rank) pairs", 172850, c.loc[(r, "rank"), "matched_pairs"], "Raw rows; rank join"),
        ("Sequence pairs with outcome before intake", 781, c.loc[(r, "rank"), "negative_duration_pairs"], "Raw rows"),
        ("Latest preceding intake, no 1:1", 155448, c.loc[(r, "asof"), "matched_pairs"],
         "Not reproduced by any tested variant; method rejected (reuses intakes)"),
        ("Chronological 1:1 matches (run 1)", 172205, c.loc[(r, "fifo"), "matched_pairs"], "FIFO or LIFO on raw rows"),
        ("Unmatched outcomes (run 1)", 1570, c.loc[(r, "fifo"), "unmatched_outcomes"], ""),
        ("Unmatched intakes (run 1)", 1607, c.loc[(r, "fifo"), "unmatched_intakes"], ""),
        ("Multiple-open-intake instances (run 1)", 96, c.loc[(r, "fifo"), "outcomes_with_multiple_open_intakes"], ""),
        ("Chronological 1:1 matches (dedup run)", 172170, c.loc[(d, "fifo"), "matched_pairs"],
         "FIFO or LIFO after exact-duplicate removal"),
        ("Unmatched outcomes (dedup run)", 1579, c.loc[(d, "fifo"), "unmatched_outcomes"], ""),
        ("Unmatched intakes (dedup run)", 1606, c.loc[(d, "fifo"), "unmatched_intakes"], ""),
        ("Multiple-open-intake instances (dedup run)", 60, c.loc[(d, "fifo"), "outcomes_with_multiple_open_intakes"], ""),
        ("FIFO vs LIFO changed assignments (dedup)", 81,
         int(pw.set_index(["method_a", "method_b"]).loc[("fifo", "lifo"), "substantive_changes_different_intake_time"]),
         "Strict timestamps; excludes 9 choices between identical-timestamp intakes (90 incl.)"),
        ("FIFO vs LIFO Animal IDs affected (dedup)", 47,
         int(pw.set_index(["method_a", "method_b"]).loc[("fifo", "lifo"), "animal_ids_affected_substantive"]), ""),
        ("Stays > 365 days (dedup run)", 578, c.loc[(d, "lifo"), "long_stay_pairs_365plus"], "Matches dedup LIFO"),
        ("LOS P50 (dedup run)", 6.02, c.loc[(d, "lifo"), "los_p50"], "dedup LIFO"),
        ("LOS P75 (dedup run)", 19.99, c.loc[(d, "lifo"), "los_p75"], "dedup LIFO; raw LIFO gives 19.99"),
        ("LOS P90 (dedup run)", 55.81, c.loc[(d, "lifo"), "los_p90"], "dedup LIFO"),
        ("LOS P95 (dedup run)", 84.90, c.loc[(d, "lifo"), "los_p95"], "dedup LIFO"),
        ("LOS P99 (dedup run)", 215.63, c.loc[(d, "lifo"), "los_p99"], "dedup LIFO; raw LIFO gives 215.63"),
    ]
    recon = pd.DataFrame(recon, columns=["metric", "preliminary", "reproduced", "note"])
    recon["difference"] = (pd.to_numeric(recon["reproduced"]) - recon["preliminary"]).round(2)
    recon["status"] = np.where(recon["difference"].abs() < 0.005, "Reproduced exactly", "Differs")
    write_csv(recon, OUT_MATCH / "preliminary_reconciliation.csv")

    km = {
        "intake_rows": len(I_raw), "outcome_rows": len(O_raw),
        "analytic_intake_events": len(I_an), "analytic_outcome_events": len(O_an),
        "matched_visits": int((visits["visit_status"] == "Matched visit").sum()),
        "same_day_reversed_candidates_excluded": len(cands),
        "unmatched_intakes": len(ui), "unmatched_outcomes": len(uo),
        "method_dependent_matched_visits": int(mv["assignment_method_dependent"].sum()),
        "ambiguous_animals": len(amb),
        "same_day_visits": int(mv["same_day_visit"].sum()),
        "los_floored_to_zero": int(mv["los_floored_to_zero"].sum()),
        "long_stays_365plus": int(mv["long_stay_365plus"].sum()),
        "animal_type_mismatch": int(mv["animal_type_mismatch"].sum()),
        **{f"los_p{int(k*100)}": round(float(x), 2) for k, x in mv["los_days"].quantile(PCTS).items()},
    }
    write_csv(metrics_frame(km), OUT_MATCH / "matching_key_metrics.csv")
    print(comp.to_string())
    print(pw.to_string())
    print(pd.Series(km).to_string())
    print(recon.to_string())
    print(ui["unmatched_reason"].value_counts().to_string())
    print(uo["unmatched_reason"].value_counts().to_string())
    return km


if __name__ == "__main__":
    main()
