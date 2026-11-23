"""Sensitivity and methodology validation for the visit-matching assumptions.

Run from the repository root (after the main pipeline; it does not modify any
existing output):
    python analysis/sensitivity_analysis.py

Outputs (outputs/sensitivity/):
    same_day_reversed_review.csv      record-level review of the 225 time-reversed matches
    midnight_outcome_split.csv        midnight outcomes split by offset presence
    scenario_comparison.csv           matching stats, LOS and the three findings per scenario
    owner_surrender_verification.csv  numerators/denominators behind the owner-surrender finding
    dog_los_verification.csv          dog LOS baseline/comparison: annual-median average vs pooled,
                                      with/without foster, cohort completeness, per scenario

Scenarios (adjacent-event rule in every case; only the timestamp assumption and
the second pass vary):
    A_all_midnight_dateonly            date-only rule for all 3,788 midnight outcomes (+ second pass) = CURRENT
    A_excl_reversed                    as A without the same-day time-reversed second pass
    B_offset_only_dateonly             date-only rule only for 3,584 offset-bearing outcomes (+ second pass)
    B_offset_only_excl_reversed        as B without the second pass
    C_strict                           strict source timestamps, no adjustment, no second pass
    C_strict_with_reversed             strict timestamps + second pass
No scenario is labelled "confirmed"; the review file is an assessment aid only.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import EXTRACT_END, REPO_ROOT, load_clean, write_csv  # noqa: E402
from matching_engine import attach_times, reconcile_same_day_reversed, run_method  # noqa: E402

OUT = REPO_ROOT / "outputs" / "sensitivity"
PCTS = [0.25, 0.5, 0.75, 0.9, 0.95, 0.99]
BASE, RECENT = list(range(2014, 2020)), [2023, 2024]
OS_YEARS = list(range(2016, 2025))
EOD = pd.Timedelta(hours=23, minutes=59, seconds=59)

SCENARIOS = {
    "A_all_midnight_dateonly": ("all_midnight", True),
    "A_excl_reversed": ("all_midnight", False),
    "B_offset_only_dateonly": ("offset_only", True),
    "B_offset_only_excl_reversed": ("offset_only", False),
    "C_strict": ("strict", False),
    "C_strict_with_reversed": ("strict", True),
}


def seq_key(O: pd.DataFrame, mode: str) -> pd.Series:
    dt = O["outcome_datetime"]
    if mode == "strict":
        return dt
    mask = O["outcome_is_midnight"] if mode == "all_midnight" else O["outcome_time_is_date_only"]
    return dt.where(~mask, dt.dt.normalize() + EOD)


def run_scenario(I, O, mode, second_pass):
    ie = pd.DataFrame({"event_id": I["intake_event_id"], "animal_id": I["animal_id"], "dt": I["intake_datetime"]})
    oe = pd.DataFrame({"event_id": O["outcome_event_id"], "animal_id": O["animal_id"], "dt": O["outcome_datetime"]})
    p1 = run_method(ie, oe.assign(dt=seq_key(O, mode)), "adjacent").assign(match_rule="chronological")
    parts = [p1]
    if second_pass:
        parts.append(reconcile_same_day_reversed(p1, ie, oe).assign(match_rule="same_day_time_reversed"))
    p = pd.concat(parts, ignore_index=True)
    return p, ie, oe


def visits_frame(p, ie, oe, I, O):
    v = attach_times(p, ie, oe)
    v = v.merge(I[["intake_event_id", "intake_type", "animal_type"]], on="intake_event_id") \
         .merge(O[["outcome_event_id", "outcome_group", "outcome_subtype"]], on="outcome_event_id")
    v["los_raw"] = v["los_days"]
    v["los_days"] = v["los_raw"].clip(lower=0)
    v["intake_year"] = v["intake_dt"].dt.year
    v["foster"] = v["outcome_subtype"].isin(["Foster", "In Foster"])
    return v


def overlaps(v):
    s = v.sort_values(["animal_id", "intake_dt"])
    prev = s.groupby("animal_id")["outcome_dt"].shift()
    ok = prev.notna()
    return int((s.loc[ok, "intake_dt"].dt.normalize() < prev[ok].dt.normalize()).sum())


def dog_los(v):
    d = v[v["animal_type"] == "Dog"]
    ann = d.groupby("intake_year")["los_days"].median()
    nf = d[~d["foster"]]
    ann_nf30 = nf.groupby("intake_year")["los_days"].apply(lambda s: (s > 30).mean() * 100)
    r = {
        "dog_median_avg_of_annual_2014_2019": ann.loc[BASE].mean(),
        "dog_median_avg_of_annual_2023_2024": ann.loc[RECENT].mean(),
        "dog_median_pooled_2014_2019": d.loc[d["intake_year"].isin(BASE), "los_days"].median(),
        "dog_median_pooled_2023_2024": d.loc[d["intake_year"].isin(RECENT), "los_days"].median(),
        "dog_median_nonfoster_pooled_2014_2019": nf.loc[nf["intake_year"].isin(BASE), "los_days"].median(),
        "dog_median_nonfoster_pooled_2023_2024": nf.loc[nf["intake_year"].isin(RECENT), "los_days"].median(),
        "dog_nonfoster_over30_avg_of_annual_2014_2019": ann_nf30.loc[BASE].mean(),
        "dog_nonfoster_over30_avg_of_annual_2023_2024": ann_nf30.loc[RECENT].mean(),
        "dog_nonfoster_over30_pooled_2014_2019": (nf.loc[nf["intake_year"].isin(BASE), "los_days"] > 30).mean() * 100,
        "dog_nonfoster_over30_pooled_2023_2024": (nf.loc[nf["intake_year"].isin(RECENT), "los_days"] > 30).mean() * 100,
    }
    return {k: round(float(x), 2) for k, x in r.items()}


def stray_rto(v):
    s = v[(v["animal_type"] == "Dog") & (v["intake_type"] == "Stray")]
    ann = s.groupby("intake_year")["outcome_group"].apply(lambda x: (x == "Return to Owner").mean() * 100)
    pooled = (s.loc[s["intake_year"].isin(BASE), "outcome_group"] == "Return to Owner").mean() * 100
    return {"stray_dog_rto_avg_of_annual_2014_2019": round(ann.loc[BASE].mean(), 2),
            "stray_dog_rto_pooled_2014_2019": round(pooled, 2),
            "stray_dog_rto_2024": round(ann.loc[2024], 2)}


def owner_surrender(v):
    """Previous MATCHED visit of the same animal (by intake time) ended in Adoption."""
    s = v.sort_values(["animal_id", "intake_dt", "intake_event_id"]).copy()
    s["prev_outcome_group"] = s.groupby("animal_id")["outcome_group"].shift()
    s["prev_outcome_dt"] = s.groupby("animal_id")["outcome_dt"].shift()
    os_ = s[s["intake_type"] == "Owner Surrender"].copy()
    os_["after_adoption"] = os_["prev_outcome_group"] == "Adoption"
    os_["days"] = (os_["intake_dt"] - os_["prev_outcome_dt"]).dt.total_seconds() / 86400
    w = os_[os_["intake_year"].isin(OS_YEARS)]
    n, a = len(w), int(w["after_adoption"].sum())
    a7 = int((w["after_adoption"] & (w["days"] <= 7)).sum())
    a30 = int((w["after_adoption"] & (w["days"] <= 30)).sum())
    all_a = os_[os_["after_adoption"]]
    return {
        "os_visits_2016_2024": n, "os_after_any_adoption_2016_2024": a,
        "os_after_any_adoption_pct_2016_2024": round(a / n * 100, 2),
        "os_within_7d_of_adoption_2016_2024": a7, "os_within_7d_pct_of_os_2016_2024": round(a7 / n * 100, 2),
        "os_within_30d_of_adoption_2016_2024": a30, "os_within_30d_pct_of_os_2016_2024": round(a30 / n * 100, 2),
        "returns_within_7d_pct_of_returns_2016_2024": round(a7 / a * 100, 2),
        "returns_within_30d_pct_of_returns_2016_2024": round(a30 / a * 100, 2),
        "adoption_returns_all_years": len(all_a),
        "returns_within_7d_pct_of_returns_all_years": round((all_a["days"] <= 7).mean() * 100, 2),
        "returns_within_30d_pct_of_returns_all_years": round((all_a["days"] <= 30).mean() * 100, 2),
    }


def scenario_metrics(name, mode, second_pass, I, O):
    p, ie, oe = run_scenario(I, O, mode, second_pass)
    v = visits_frame(p, ie, oe, I, O)
    q = v["los_days"].quantile(PCTS)
    r = {
        "scenario": name, "date_only_rule": mode, "same_day_reversed_pass": second_pass,
        "matched_visits": len(v),
        "matched_by_reversed_pass": int((v["match_rule"] == "same_day_time_reversed").sum()),
        "unmatched_intakes": len(ie) - len(v), "unmatched_outcomes": len(oe) - len(v),
        "negative_raw_duration_pairs": int((v["los_raw"] < 0).sum()),
        "zero_day_stays": int((v["los_days"] == 0).sum()),
        "same_day_visits": int((v["intake_dt"].dt.normalize() == v["outcome_dt"].dt.normalize()).sum()),
        "overlapping_visits": overlaps(v),
        "intake_reused": int(v["intake_event_id"].duplicated().sum()),
        **{f"los_p{int(k * 100)}": round(float(x), 2) for k, x in q.items()},
        "los_mean": round(float(v["los_days"].mean()), 2),
        "long_stays_365plus": int((v["los_days"] > 365).sum()),
    }
    r.update(dog_los(v))
    r.update(stray_rto(v))
    r.update(owner_surrender(v))
    return r, v


def review_reversed(v, I, O):
    """Record-level review of the time-reversed matches with a transparent assessment."""
    r = v[v["match_rule"] == "same_day_time_reversed"].copy()
    ic = ["intake_event_id", "source_row", "intake_datetime_raw", "intake_type", "intake_condition",
          "age_upon_intake_raw", "found_location"]
    oc = ["outcome_event_id", "source_row", "outcome_datetime_raw", "outcome_tz_offset", "outcome_is_midnight",
          "outcome_type", "outcome_subtype", "outcome_status_provisional"]
    r = r[["animal_id", "animal_type", "intake_event_id", "outcome_event_id", "intake_dt", "outcome_dt"]] \
        .merge(I[ic].rename(columns={"source_row": "intake_source_row"}), on="intake_event_id") \
        .merge(O[oc].rename(columns={"source_row": "outcome_source_row"}), on="outcome_event_id")
    r["outcome_before_intake_hours"] = ((r["intake_dt"] - r["outcome_dt"]).dt.total_seconds() / 3600).round(2)
    # context: other events of the animal within +/- 1 day, and total events for the animal
    ev = pd.concat([
        I[["animal_id", "intake_event_id", "intake_datetime"]].set_axis(["animal_id", "eid", "dt"], axis=1),
        O[["animal_id", "outcome_event_id", "outcome_datetime"]].set_axis(["animal_id", "eid", "dt"], axis=1)])
    ev = ev[ev["animal_id"].isin(r["animal_id"])]
    x = r[["animal_id", "intake_event_id", "outcome_event_id", "outcome_dt"]].merge(ev, on="animal_id")
    x = x[(x["eid"] != x["intake_event_id"]) & (x["eid"] != x["outcome_event_id"])]
    near = x[(x["dt"] - x["outcome_dt"]).abs() <= pd.Timedelta(days=1)].groupby("outcome_event_id").size()
    r["other_events_within_1_day"] = r["outcome_event_id"].map(near).fillna(0).astype(int)
    r["animal_total_events"] = r["animal_id"].map(ev.groupby("animal_id").size()).astype(int)

    reasons, status = [], []
    for _, row in r.iterrows():
        amb = []
        if row["outcome_type"] == "Adoption":
            amb.append("adoption recorded before the intake on the same day is atypical")
        if row["intake_type"] == "Owner Surrender" and row["outcome_type"] == "Return to Owner":
            amb.append("owner surrender followed by return to owner")
        if row["other_events_within_1_day"] > 0:
            amb.append(f"{row['other_events_within_1_day']} other event(s) for the animal within 1 day")
        if row["outcome_before_intake_hours"] > 8:
            amb.append("outcome more than 8 h before intake")
        if amb:
            status.append("Ambiguous - needs review")
            reasons.append("; ".join(amb))
        else:
            status.append("Plausible - consistent with recording-order lag (unconfirmed)")
            reasons.append(f"{row['outcome_type']} ({row['outcome_subtype'] if pd.notna(row['outcome_subtype']) else 'no subtype'}) "
                           f"after {row['intake_type']} intake, {row['outcome_before_intake_hours']} h reversal, "
                           "no other events within 1 day")
    r["review_assessment"] = status
    r["review_reason"] = reasons
    r = r.rename(columns={"intake_dt": "intake_datetime", "outcome_dt": "outcome_datetime"})
    return r.sort_values(["review_assessment", "outcome_before_intake_hours"], ascending=[True, False])


def dog_los_detail(vA, vX, I, matched_ids_A):
    rows = []
    for name, v in (("A_all_midnight_dateonly (current)", vA), ("A_excl_reversed", vX)):
        d = v[v["animal_type"] == "Dog"]
        for y, g in d.groupby("intake_year"):
            rows.append({"scenario": name, "intake_year": y, "matched_dog_visits": len(g),
                         "median_los_days": round(g["los_days"].median(), 2),
                         "foster_subtype_pct": round(g["foster"].mean() * 100, 2),
                         "nonfoster_median_los_days": round(g.loc[~g["foster"], "los_days"].median(), 2),
                         "nonfoster_over30_pct": round((g.loc[~g["foster"], "los_days"] > 30).mean() * 100, 2)})
    t = pd.DataFrame(rows)
    # cohort completeness: dog intake events per year and share left without an accepted outcome
    di = I[I["animal_type"] == "Dog"]
    tot = di.groupby(di["intake_datetime"].dt.year).size()
    unm = di[~di["intake_event_id"].isin(matched_ids_A)]
    um = unm.groupby(unm["intake_datetime"].dt.year).size()
    comp = pd.DataFrame({"dog_intake_events": tot, "dog_intakes_unmatched_current": um}).fillna(0).astype(int)
    comp["unmatched_pct"] = (comp["dog_intakes_unmatched_current"] / comp["dog_intake_events"] * 100).round(2)
    comp.index.name = "intake_year"
    return t.merge(comp.reset_index(), on="intake_year", how="left")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    I, O = load_clean()
    I, O = I[~I["is_exact_duplicate"]], O[~O["is_exact_duplicate"]]

    mid = O[O["outcome_is_midnight"]]
    split = pd.DataFrame([
        {"group": "Midnight with -05:00 offset", "outcome_events": int(mid["outcome_time_is_date_only"].sum())},
        {"group": "Midnight without offset", "outcome_events": int((~mid["outcome_time_is_date_only"]).sum())},
        {"group": "All midnight outcomes", "outcome_events": len(mid)},
    ])
    for g, m in (("Midnight with -05:00 offset", mid["outcome_time_is_date_only"]),
                 ("Midnight without offset", ~mid["outcome_time_is_date_only"])):
        yrs = mid.loc[m, "outcome_datetime"].dt.year
        split.loc[split["group"] == g, "first_year"] = yrs.min()
        split.loc[split["group"] == g, "last_year"] = yrs.max()
        split.loc[split["group"] == g, "top_outcome_types"] = "; ".join(
            f"{k}={v}" for k, v in mid.loc[m, "outcome_type"].value_counts().head(3).items())
    write_csv(split, OUT / "midnight_outcome_split.csv")

    rows, vis = [], {}
    for name, (mode, sp) in SCENARIOS.items():
        r, v = scenario_metrics(name, mode, sp, I, O)
        rows.append(r)
        vis[name] = v
    comp = pd.DataFrame(rows)
    write_csv(comp, OUT / "scenario_comparison.csv")

    review = review_reversed(vis["A_all_midnight_dateonly"], I, O)
    write_csv(review, OUT / "same_day_reversed_review.csv")

    osv = comp[["scenario"] + [c for c in comp.columns if c.startswith(("os_", "returns_", "adoption_returns"))]]
    write_csv(osv, OUT / "owner_surrender_verification.csv")
    write_csv(dog_los_detail(vis["A_all_midnight_dateonly"], vis["A_excl_reversed"], I,
                             set(vis["A_all_midnight_dateonly"]["intake_event_id"])),
              OUT / "dog_los_verification.csv")
    print(comp.T.to_string())
    print(review["review_assessment"].value_counts().to_string())
    print(split.to_string())


if __name__ == "__main__":
    main()
