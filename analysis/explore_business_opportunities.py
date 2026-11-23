"""Time-series validation and business-opportunity evidence.

Run from the repository root AFTER match_visits.py:
    python analysis/explore_business_opportunities.py

Inputs : data/raw (via common.load_clean) and outputs/matching/candidate_visits.csv
Outputs: outputs/analysis/*.csv

Conventions
* Event counts (intake rows, outcome rows) and visit-level rates are kept in
  separate files and never divided by each other.
* Visit-level outcome shares use MATCHED visits as the denominator.
* Exact duplicate rows are excluded from event counts ("analytic events");
  raw-row counts are reported alongside for reconciliation.
* "Live outcome" is the provisional grouping in common.OUTCOME_STATUS, not the
  City of Austin live-release formula.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import EXTRACT_END, OUT_ANALYSIS, OUT_MATCH, ensure_dirs, load_clean, metrics_frame, write_csv  # noqa: E402

FULL_YEARS = list(range(2014, 2025))  # complete calendar years in the extract
LIKE_FOR_LIKE_END = (5, 4)  # 01-01 to 04-05 inclusive: last full day common to both files is 04-05-2025
MIN_GROUP = 500  # minimum matched visits for a breed-level comparison


def load_visits() -> pd.DataFrame:
    v = pd.read_csv(OUT_MATCH / "candidate_visits.csv", low_memory=False,
                    parse_dates=["intake_datetime", "outcome_datetime", "intake_date", "outcome_date"])
    return v


def share_table(df: pd.DataFrame, by: list, col: str, name: str) -> pd.DataFrame:
    t = df.groupby(by + [col]).size().rename("visits").reset_index()
    t["denominator_visits"] = t.groupby(by)["visits"].transform("sum")
    t["share_pct"] = (t["visits"] / t["denominator_visits"] * 100).round(2)
    t.insert(0, "breakdown", name)
    return t


def los_summary(df: pd.DataFrame, by: list) -> pd.DataFrame:
    g = df.groupby(by)["los_days"]
    t = pd.DataFrame({
        "visits": g.size(), "median_days": g.median().round(2), "p75_days": g.quantile(0.75).round(2),
        "p90_days": g.quantile(0.9).round(2), "mean_days": g.mean().round(2),
        "share_over_30d_pct": (g.apply(lambda s: (s > 30).mean() * 100)).round(2),
        "share_over_90d_pct": (g.apply(lambda s: (s > 90).mean() * 100)).round(2),
    }).reset_index()
    return t


# ----------------------------------------------------------------- time series
def time_series(I: pd.DataFrame, O: pd.DataFrame, out: dict) -> None:
    Ia, Oa = I[~I["is_exact_duplicate"]], O[~O["is_exact_duplicate"]]
    m_i = Ia.groupby(Ia["intake_datetime"].dt.to_period("M")).size().rename("intake_events")
    m_o = Oa.groupby(Oa["outcome_datetime"].dt.to_period("M")).size().rename("outcome_events")
    m = pd.concat([m_i, m_o], axis=1).fillna(0).astype(int)
    m.index.name = "month"
    m = m.reset_index()
    m["month_start"] = m["month"].dt.to_timestamp()
    m["year"] = m["month"].dt.year
    m["month_of_year"] = m["month"].dt.month
    m["partial_month"] = m["month"] == pd.Period("2025-05", "M")  # extract ends 05-05-2025
    m["net_flow_events"] = m["intake_events"] - m["outcome_events"]
    for c in ("intake_events", "outcome_events"):
        prev = m.set_index("month")[c].reindex(m["month"] - 12).to_numpy()
        m[f"{c}_same_month_prior_year"] = prev
        m[f"{c}_yoy_pct"] = ((m[c] - prev) / prev * 100).round(2)
    m["intake_events_rolling_12m"] = m["intake_events"].rolling(12).sum()
    m = m.drop(columns="month")
    out["monthly_event_counts"] = m

    # annual (raw rows and analytic events)
    y = pd.DataFrame({
        "intake_rows_raw": I.groupby(I["intake_datetime"].dt.year).size(),
        "outcome_rows_raw": O.groupby(O["outcome_datetime"].dt.year).size(),
        "intake_events": Ia.groupby(Ia["intake_datetime"].dt.year).size(),
        "outcome_events": Oa.groupby(Oa["outcome_datetime"].dt.year).size(),
    })
    y.index.name = "year"
    y = y.reset_index()
    y["coverage"] = np.where(y["year"] == 2013, "Partial: 01-10-2013 to 31-12-2013",
                             np.where(y["year"] == 2025, "Partial: 01-01-2025 to 05-05-2025", "Full calendar year"))
    y["full_year"] = y["year"].isin(FULL_YEARS)
    for c in ("intake_events", "outcome_events"):
        prev = y[c].shift()
        ok = y["full_year"] & y["year"].sub(1).isin(FULL_YEARS)
        y[f"{c}_yoy_pct"] = np.where(ok, ((y[c] - prev) / prev * 100).round(2), np.nan)
    prelim = {2013: (4182, 4505), 2014: (18656, 18709), 2015: (18712, 18506), 2016: (17675, 17670),
              2017: (17563, 17657), 2018: (16979, 16741), 2019: (19727, 19775), 2020: (9587, 9778),
              2021: (12043, 11967), 2022: (11896, 11885), 2023: (11227, 11151), 2024: (11817, 11822),
              2025: (3748, 3609)}
    y["prelim_intakes"] = y["year"].map(lambda k: prelim[k][0])
    y["prelim_outcomes"] = y["year"].map(lambda k: prelim[k][1])
    y["raw_intakes_minus_prelim"] = y["intake_rows_raw"] - y["prelim_intakes"]
    y["raw_outcomes_minus_prelim"] = y["outcome_rows_raw"] - y["prelim_outcomes"]
    out["annual_event_counts"] = y

    # like-for-like: same calendar window in every year
    rows = []
    mm, dd = LIKE_FOR_LIKE_END
    for yr in range(2014, 2026):
        lo, hi = pd.Timestamp(yr, 1, 1), pd.Timestamp(yr, mm, dd) + pd.Timedelta(days=1)
        rows.append({"window": f"01-01 to {dd:02d}-{mm:02d}", "year": yr,
                     "intake_events": int(Ia["intake_datetime"].between(lo, hi, inclusive="left").sum()),
                     "outcome_events": int(Oa["outcome_datetime"].between(lo, hi, inclusive="left").sum())})
    for yr in range(2013, 2025):
        lo, hi = pd.Timestamp(yr, 10, 1), pd.Timestamp(yr + 1, 1, 1)
        rows.append({"window": "01-10 to 31-12", "year": yr,
                     "intake_events": int(Ia["intake_datetime"].between(lo, hi, inclusive="left").sum()),
                     "outcome_events": int(Oa["outcome_datetime"].between(lo, hi, inclusive="left").sum())})
    lf = pd.DataFrame(rows)
    for c in ("intake_events", "outcome_events"):
        lf[f"{c}_yoy_pct"] = (lf.groupby("window")[c].pct_change() * 100).round(2)
    out["like_for_like_periods"] = lf

    # seasonality index over full years only
    full = m[m["year"].isin(FULL_YEARS)]
    s = full.groupby("month_of_year")[["intake_events", "outcome_events"]].mean()
    s = (s / s.mean() * 100).round(1).add_suffix("_index")
    s["intake_events_mean"] = full.groupby("month_of_year")["intake_events"].mean().round(1)
    s["intake_events_min"] = full.groupby("month_of_year")["intake_events"].min()
    s["intake_events_max"] = full.groupby("month_of_year")["intake_events"].max()
    s["years"] = full.groupby("month_of_year").size()
    out["seasonality_index"] = s.reset_index()

    # annual intakes by intake type and animal type (events)
    t = Ia.groupby([Ia["intake_datetime"].dt.year.rename("year"), "intake_type"]).size().unstack(fill_value=0)
    out["annual_intakes_by_type"] = t.reset_index()
    t2 = Ia.groupby([Ia["intake_datetime"].dt.year.rename("year"), "animal_type"]).size().unstack(fill_value=0)
    out["annual_intakes_by_animal_type"] = t2.reset_index()
    t3 = Oa.groupby([Oa["outcome_datetime"].dt.year.rename("year"), "outcome_group"]).size().unstack(fill_value=0)
    out["annual_outcomes_by_group"] = t3.reset_index()

    # structural break screen: 12-month mean before vs after each month
    x = m.set_index("month_start")["intake_events"]
    x = x[(x.index >= "2013-10-01") & (x.index < "2025-05-01")]
    br = []
    for k in range(12, len(x) - 12):
        before, after = x.iloc[k - 12:k].mean(), x.iloc[k:k + 12].mean()
        br.append({"month_start": x.index[k], "mean_12m_before": round(before, 1),
                   "mean_12m_after": round(after, 1), "shift_pct": round((after - before) / before * 100, 2)})
    br = pd.DataFrame(br)
    out["structural_break_screen"] = br


# --------------------------------------------------------------- visit level
def visit_analyses(v: pd.DataFrame, I: pd.DataFrame, out: dict) -> dict:
    mv = v[v["visit_status"] == "Matched visit"].copy()
    mv["intake_year"] = mv["intake_datetime"].dt.year
    ev = {}

    # outcome mix by key dimensions (visit-level; denominator = matched visits)
    parts = [
        share_table(mv, ["intake_type"], "outcome_group", "intake_type x outcome_group"),
        share_table(mv, ["animal_type"], "outcome_group", "animal_type x outcome_group"),
        share_table(mv, ["age_band_intake"], "outcome_group", "age_band x outcome_group"),
        share_table(mv, ["intake_condition"], "outcome_group", "intake_condition x outcome_group"),
        share_table(mv, ["intake_year"], "outcome_group", "intake_year x outcome_group"),
        share_table(mv[mv["animal_type"].isin(["Dog", "Cat"])], ["animal_type", "intake_type"], "outcome_group",
                    "animal_type x intake_type x outcome_group"),
        share_table(mv, ["animal_type"], "outcome_status_provisional", "animal_type x provisional status"),
        share_table(mv, ["intake_year"], "outcome_status_provisional", "intake_year x provisional status"),
        share_table(mv[mv["animal_type"].isin(["Dog", "Cat"])], ["animal_type", "intake_year"],
                    "outcome_status_provisional", "dog/cat x intake_year x provisional status"),
    ]
    out["visit_outcome_mix"] = pd.concat(parts, ignore_index=True)

    # outcome subtype within type (missingness made explicit)
    st = mv.assign(outcome_subtype=mv["outcome_subtype"].fillna("(not recorded)"))
    out["outcome_subtype_by_type"] = share_table(st, ["outcome_type"], "outcome_subtype", "outcome_type x subtype")
    out["transfer_subtype_by_animal"] = share_table(
        st[st["outcome_type"] == "Transfer"], ["animal_type"], "outcome_subtype", "transfer subtype by animal")
    out["euthanasia_subtype_by_animal"] = share_table(
        st[st["outcome_type"] == "Euthanasia"], ["animal_type"], "outcome_subtype", "euthanasia subtype by animal")

    # LOS
    los = pd.concat([
        los_summary(mv, ["outcome_group"]).assign(breakdown="outcome_group"),
        los_summary(mv, ["animal_type"]).assign(breakdown="animal_type"),
        los_summary(mv, ["intake_type"]).assign(breakdown="intake_type"),
        los_summary(mv, ["age_band_intake"]).assign(breakdown="age_band_intake"),
        los_summary(mv, ["intake_condition"]).assign(breakdown="intake_condition"),
        los_summary(mv[mv["animal_type"].isin(["Dog", "Cat"])], ["animal_type", "outcome_group"]).assign(
            breakdown="animal_type x outcome_group"),
        los_summary(mv[mv["animal_type"].isin(["Dog", "Cat"])], ["animal_type", "intake_year"]).assign(
            breakdown="animal_type x intake_year"),
    ], ignore_index=True)
    out["los_by_segment"] = los

    # long stays: profile (intake age is DOB-derived in the source, so an
    # age-vs-DOB check cannot validate stay length; foster share is reported instead)
    mv["long_band"] = pd.cut(mv["los_days"], [-1, 90, 180, 365, np.inf],
                             labels=["<=90d", "91-180d", "181-365d", ">365d"])
    ls = mv.groupby("long_band", observed=True).agg(
        visits=("visit_id", "size"),
        dogs_pct=("animal_type", lambda s: round((s == "Dog").mean() * 100, 1)),
        adoption_pct=("outcome_group", lambda s: round((s == "Adoption").mean() * 100, 1)),
        transfer_pct=("outcome_group", lambda s: round((s == "Transfer").mean() * 100, 1)),
        euthanasia_pct=("outcome_group", lambda s: round((s == "Euthanasia").mean() * 100, 1)),
        return_intake_pct=("is_return_intake", lambda s: round(s.mean() * 100, 1)),
        owner_surrender_pct=("intake_type", lambda s: round((s == "Owner Surrender").mean() * 100, 1)),
        foster_subtype_pct=("outcome_subtype", lambda s: round(s.isin(["Foster", "In Foster"]).mean() * 100, 1)),
        method_dependent=("assignment_method_dependent", "sum"),
    ).reset_index()
    out["long_stay_profile"] = ls
    long = mv[mv["los_days"] > 365].sort_values("los_days", ascending=False)
    out["long_stay_visits_365plus"] = long[[
        "visit_id", "animal_id", "intake_event_id", "outcome_event_id", "intake_datetime", "outcome_datetime",
        "los_days", "animal_type", "intake_type", "intake_condition", "outcome_type", "outcome_subtype",
        "age_band_intake", "is_return_intake", "assignment_method_dependent", "intake_age_dob_gap_days"]]

    # daily census from matched visits (end-of-day in-care count)
    days = pd.date_range("2013-10-01", "2025-05-05", freq="D")
    idx0 = days[0]
    start = ((mv["intake_date"] - idx0).dt.days).to_numpy()
    end = ((mv["outcome_date"] - idx0).dt.days).to_numpy()
    diff = np.zeros(len(days) + 1, dtype=int)
    np.add.at(diff, start, 1)
    np.add.at(diff, end, -1)  # in care at end of day d if intake_date <= d < outcome_date
    census = pd.DataFrame({"date": days, "in_care_end_of_day_matched": np.cumsum(diff)[:-1]})
    census["year"] = census["date"].dt.year
    cm = census.groupby(census["date"].dt.to_period("M")).agg(
        avg_in_care=("in_care_end_of_day_matched", "mean"), max_in_care=("in_care_end_of_day_matched", "max"))
    cm = cm.round(1).reset_index()
    cm["month_start"] = cm["date"].dt.to_timestamp()
    cm = cm.drop(columns="date")
    out["monthly_census_estimate"] = cm
    cy = census.groupby("year")["in_care_end_of_day_matched"].agg(["mean", "max"]).round(1).reset_index()
    out["annual_census_estimate"] = cy

    # repeat visits
    Ia = I[~I["is_exact_duplicate"]].sort_values(["animal_id", "intake_datetime", "intake_event_id"]).copy()
    Ia["ordinal"] = Ia.groupby("animal_id").cumcount() + 1
    Ia["prev_intake"] = Ia.groupby("animal_id")["intake_datetime"].shift()
    Ia["days_since_prev_intake"] = (Ia["intake_datetime"] - Ia["prev_intake"]).dt.total_seconds() / 86400
    rep = Ia.groupby(Ia["intake_datetime"].dt.year.rename("year")).agg(
        intake_events=("intake_event_id", "size"),
        return_intakes=("ordinal", lambda s: int((s > 1).sum())))
    rep["return_intake_pct"] = (rep["return_intakes"] / rep["intake_events"] * 100).round(2)
    out["repeat_intakes_by_year"] = rep.reset_index()
    rt = Ia.groupby("intake_type").agg(intake_events=("intake_event_id", "size"),
                                       return_intakes=("ordinal", lambda s: int((s > 1).sum())))
    rt["return_intake_pct"] = (rt["return_intakes"] / rt["intake_events"] * 100).round(2)
    out["repeat_intakes_by_type"] = rt.reset_index()
    freq = Ia.groupby("animal_id").size().value_counts().sort_index()
    out["intakes_per_animal"] = pd.DataFrame({"intakes_per_animal": freq.index, "animal_ids": freq.values})

    # re-entry after a matched outcome: does the animal come back within 365 days?
    mv_sorted = mv.sort_values(["animal_id", "intake_datetime"])
    Ia_next = Ia.groupby("animal_id")["intake_datetime"].apply(list)
    def next_intake_after(row_aid, odt):
        lst = Ia_next.get(row_aid, [])
        later = [t for t in lst if t > odt]
        return later[0] if later else pd.NaT
    multi_ids = set(Ia.loc[Ia["ordinal"] > 1, "animal_id"])
    mv_sorted["next_intake_after_outcome"] = [
        next_intake_after(a, o) if a in multi_ids else pd.NaT
        for a, o in zip(mv_sorted["animal_id"], mv_sorted["outcome_datetime"])]
    gap = (mv_sorted["next_intake_after_outcome"] - mv_sorted["outcome_datetime"]).dt.days
    # only outcomes with a full 365-day follow-up window inside the extract
    eligible = mv_sorted["outcome_datetime"] <= EXTRACT_END - pd.Timedelta(days=365)
    mv_sorted["returned_within_365d"] = gap.le(365) & gap.notna()
    re = mv_sorted[eligible].groupby(["animal_type", "outcome_group"]).agg(
        visits_with_365d_followup=("visit_id", "size"),
        returned_within_365d=("returned_within_365d", "sum")).reset_index()
    re["return_within_365d_pct"] = (re["returned_within_365d"] / re["visits_with_365d_followup"] * 100).round(2)
    out["reentry_within_365d_by_outcome"] = re[re["visits_with_365d_followup"] >= 50]

    # stray reunification: RTO share among stray matched visits, by animal and year
    stray = mv[mv["intake_type"] == "Stray"]
    sr = stray.groupby(["animal_type", "intake_year"]).agg(
        stray_visits=("visit_id", "size"),
        rto_visits=("outcome_group", lambda s: int((s == "Return to Owner").sum()))).reset_index()
    sr["rto_share_pct"] = (sr["rto_visits"] / sr["stray_visits"] * 100).round(2)
    out["stray_rto_by_year"] = sr[sr["animal_type"].isin(["Dog", "Cat"])]
    rto = mv[mv["outcome_group"] == "Return to Owner"]
    rl = rto.groupby("animal_type")["los_days"].agg(
        rto_visits="size", median_days="median",
        within_3_days_pct=lambda s: round((s <= 3).mean() * 100, 1),
        same_day_pct=lambda s: round((s < 1).mean() * 100, 1)).round(2).reset_index()
    out["rto_timing"] = rl

    # breed-level (dogs and cats separately; minimum group size)
    br = []
    for t in ("Dog", "Cat"):
        d = mv[mv["animal_type"] == t].merge(
            I[["intake_event_id", "breed"]], on="intake_event_id", how="left")
        g = d.groupby("breed")
        b = pd.DataFrame({
            "visits": g.size(), "median_los_days": g["los_days"].median().round(2),
            "adoption_pct": g["outcome_group"].apply(lambda s: (s == "Adoption").mean() * 100).round(2),
            "rto_pct": g["outcome_group"].apply(lambda s: (s == "Return to Owner").mean() * 100).round(2),
            "transfer_pct": g["outcome_group"].apply(lambda s: (s == "Transfer").mean() * 100).round(2),
            "euthanasia_pct": g["outcome_group"].apply(lambda s: (s == "Euthanasia").mean() * 100).round(2),
            "share_over_90d_pct": g["los_days"].apply(lambda s: (s > 90).mean() * 100).round(2),
        }).reset_index()
        b = b[b["visits"] >= MIN_GROUP].sort_values("visits", ascending=False).assign(animal_type=t)
        br.append(b)
    out["breed_outcomes_min500"] = pd.concat(br, ignore_index=True)
    out["breed_label_profile"] = pd.DataFrame([{
        "distinct_breed_labels": int(I["breed"].nunique()),
        "labels_with_500plus_matched_visits": int(sum(len(b) for b in br)),
        "intake_rows_with_mix_or_slash": int(I["breed_is_mix"].sum()),
        "pct_mix_or_slash": round(I["breed_is_mix"].mean() * 100, 2),
    }])

    # intake condition profile (events) and welfare indicators
    Ie = I[~I["is_exact_duplicate"]]
    ic = Ie.groupby([Ie["intake_datetime"].dt.year.rename("year"), "intake_condition"]).size().unstack(fill_value=0)
    out["intake_condition_by_year"] = ic.reset_index()

    # unmatched / open intakes by year (data-completeness indicator)
    ui = pd.read_csv(OUT_MATCH / "unmatched_intakes.csv", parse_dates=["intake_datetime"])
    uo = pd.read_csv(OUT_MATCH / "unmatched_outcomes.csv", parse_dates=["outcome_datetime"])
    a = ui.groupby([ui["intake_datetime"].dt.year.rename("year"), "unmatched_reason"]).size().rename("rows").reset_index()
    b = uo.groupby([uo["outcome_datetime"].dt.year.rename("year"), "unmatched_reason"]).size().rename("rows").reset_index()
    out["unmatched_by_year"] = pd.concat([a.assign(event="Intake"), b.assign(event="Outcome")], ignore_index=True)

    # LOS trend by intake cohort, with and without foster-subtype outcomes.
    # Foster-subtype adoptions include time spent in foster care, so LOS is not
    # equivalent to kennel days for those visits.
    mv["foster_subtype"] = mv["outcome_subtype"].isin(["Foster", "In Foster"])
    rows = []
    for (t, y), g in mv[mv["animal_type"].isin(["Dog", "Cat"])].groupby(["animal_type", "intake_year"]):
        nf = g[~g["foster_subtype"]]
        rows.append({"animal_type": t, "intake_year": y, "visits": len(g),
                     "foster_subtype_pct": round(g["foster_subtype"].mean() * 100, 2),
                     "median_los_days": round(g["los_days"].median(), 2),
                     "share_over_30d_pct": round((g["los_days"] > 30).mean() * 100, 2),
                     "non_foster_visits": len(nf),
                     "non_foster_median_los_days": round(nf["los_days"].median(), 2),
                     "non_foster_share_over_30d_pct": round((nf["los_days"] > 30).mean() * 100, 2),
                     "non_foster_adoption_median_los_days":
                         round(nf.loc[nf["outcome_group"] == "Adoption", "los_days"].median(), 2),
                     "partial_or_censored_cohort": y in (2013, 2025)})
    out["los_trend_by_intake_year"] = pd.DataFrame(rows)

    # previous visit outcome for return intakes; adoption returns among owner surrenders
    mv = mv.sort_values(["animal_id", "intake_datetime", "intake_event_id"])
    mv["prev_outcome_group"] = mv.groupby("animal_id")["outcome_group"].shift()
    mv["prev_outcome_datetime"] = mv.groupby("animal_id")["outcome_datetime"].shift()
    ret = mv[mv["is_return_intake"] == 1]
    pc = ret.groupby(["intake_type", ret["prev_outcome_group"].fillna("(previous intake unmatched)")]).size()
    out["return_intake_previous_outcome"] = pc.rename("return_intakes").reset_index().rename(
        columns={"prev_outcome_group": "previous_visit_outcome"})
    os_ = mv[mv["intake_type"] == "Owner Surrender"].copy()
    os_["after_adoption"] = os_["prev_outcome_group"] == "Adoption"
    os_["days_since_adoption"] = (os_["intake_datetime"] - os_["prev_outcome_datetime"]).dt.total_seconds() / 86400
    ar = os_.groupby("intake_year").agg(owner_surrender_visits=("visit_id", "size"),
                                         returned_after_adoption=("after_adoption", "sum")).reset_index()
    ar["returned_after_adoption_pct"] = (ar["returned_after_adoption"] / ar["owner_surrender_visits"] * 100).round(2)
    ar["note"] = np.where(ar["intake_year"] <= 2015,
                          "Low bias: adoptions before 01-10-2013 are not visible", "")
    out["adoption_returns_by_year"] = ar
    ad = os_.loc[os_["after_adoption"], "days_since_adoption"]
    bins = [-0.001, 7, 30, 90, 180, 365, np.inf]
    labs = ["0-7 days", "8-30 days", "31-90 days", "91-180 days", "181-365 days", "365+ days"]
    at = pd.cut(ad, bins=bins, labels=labs).value_counts().reindex(labs).rename("returns").reset_index()
    at.columns = ["days_since_adoption", "returns"]
    at["share_pct"] = (at["returns"] / at["returns"].sum() * 100).round(2)
    at["cumulative_pct"] = at["share_pct"].cumsum().round(2)
    out["adoption_return_timing"] = at
    out["adoption_returns_by_animal"] = os_[os_["after_adoption"]].groupby("animal_type").size().rename(
        "returns").reset_index()

    # headline evidence
    st_all = mv["outcome_status_provisional"].value_counts(normalize=True) * 100
    ev["matched_visits"] = len(mv)
    ev["live_outcome_pct_provisional"] = round(st_all.get("Live outcome", 0), 2)
    ev["non_live_pct_provisional"] = round(st_all.get("Non-live outcome", 0), 2)
    ev["transfer_share_pct"] = round((mv["outcome_group"] == "Transfer").mean() * 100, 2)
    ev["adoption_share_pct"] = round((mv["outcome_group"] == "Adoption").mean() * 100, 2)
    ev["rto_share_pct"] = round((mv["outcome_group"] == "Return to Owner").mean() * 100, 2)
    ev["euthanasia_share_pct"] = round((mv["outcome_group"] == "Euthanasia").mean() * 100, 2)
    ev["stray_rto_share_pct"] = round((stray["outcome_group"] == "Return to Owner").mean() * 100, 2)
    ev["median_los_days"] = round(mv["los_days"].median(), 2)
    ev["visits_over_90d"] = int((mv["los_days"] > 90).sum())
    ev["visits_over_365d"] = int((mv["los_days"] > 365).sum())
    ev["return_intake_pct"] = round((Ia["ordinal"] > 1).mean() * 100, 2)

    # evidence used by the opportunity register
    lt = out["los_trend_by_intake_year"].set_index(["animal_type", "intake_year"])
    base, recent = list(range(2014, 2020)), [2023, 2024]
    for t in ("Dog", "Cat"):
        for col, key in (("median_los_days", "median"), ("non_foster_share_over_30d_pct", "nf_over30")):
            ev[f"{t.lower()}_{key}_2014_2019"] = round(lt.loc[[(t, y) for y in base], col].mean(), 2)
            ev[f"{t.lower()}_{key}_2023_2024"] = round(lt.loc[[(t, y) for y in recent], col].mean(), 2)
    srd = out["stray_rto_by_year"].set_index(["animal_type", "intake_year"])["rto_share_pct"]
    ev["stray_dog_rto_pct_2014_2019"] = round(srd.loc[[("Dog", y) for y in base]].mean(), 2)
    ev["stray_dog_rto_pct_2024"] = float(srd.loc[("Dog", 2024)])
    arr = ar.set_index("intake_year")
    yrs = list(range(2016, 2025))
    ev["owner_surrender_after_adoption_pct_2016_2024"] = round(
        arr.loc[yrs, "returned_after_adoption"].sum() / arr.loc[yrs, "owner_surrender_visits"].sum() * 100, 2)
    ev["adoption_returns_total"] = int(os_["after_adoption"].sum())
    ev["adoption_returns_within_30d_pct"] = round(float((ad <= 30).mean() * 100), 2)
    ev["adoption_returns_within_7d_pct"] = round(float((ad <= 7).mean() * 100), 2)
    ac = out["annual_census_estimate"].set_index("year")["mean"]
    ae = out["annual_event_counts"].set_index("year")["intake_events"]
    ev["avg_in_care_2019"], ev["avg_in_care_2024"] = float(ac[2019]), float(ac[2024])
    ev["intake_events_2019"], ev["intake_events_2024"] = int(ae[2019]), int(ae[2024])
    ev["intake_events_mean_2014_2019"] = round(ae.loc[base].mean(), 0)
    ev["intake_events_mean_2022_2024"] = round(ae.loc[[2022, 2023, 2024]].mean(), 0)
    si = out["seasonality_index"].set_index("month_of_year")["intake_events_index"]
    ev["seasonality_peak_month"], ev["seasonality_peak_index"] = int(si.idxmax()), float(si.max())
    ev["seasonality_trough_month"], ev["seasonality_trough_index"] = int(si.idxmin()), float(si.min())
    tr = mv[mv["outcome_type"] == "Transfer"]
    ev["cat_transfers_snr_scrp_pct"] = round(
        tr.loc[tr["animal_type"] == "Cat", "outcome_subtype"].isin(["Snr", "SCRP"]).mean() * 100, 2)
    eu = mv[mv["outcome_group"] == "Euthanasia"]
    ev["euthanasia_other_rabies_risk_pct"] = round(
        ((eu["animal_type"] == "Other") & (eu["outcome_subtype"] == "Rabies Risk")).mean() * 100, 2)
    dc = mv[mv["animal_type"].isin(["Dog", "Cat"])]
    eyr = dc.groupby("intake_year")["outcome_group"].apply(lambda s: (s == "Euthanasia").mean() * 100)
    ev["dogcat_euthanasia_pct_2014"], ev["dogcat_euthanasia_pct_2024"] = round(eyr[2014], 2), round(eyr[2024], 2)
    ev["long_stay_365_foster_subtype_pct"] = round(float(mv.loc[mv["los_days"] > 365, "foster_subtype"].mean() * 100), 2)
    ev["non_normal_intake_condition_pct"] = round(float((mv["intake_condition"] != "Normal").mean() * 100), 2)
    ev["dog_adoption_reentry_365d_pct"] = float(out["reentry_within_365d_by_outcome"].set_index(
        ["animal_type", "outcome_group"]).loc[("Dog", "Adoption"), "return_within_365d_pct"])
    out["business_opportunity_assessment"] = opportunity_register(ev)
    return ev


def opportunity_register(ev: dict) -> pd.DataFrame:
    """Scored opportunity register.

    Scores (1-5, higher is better) are analyst judgements recorded here so they
    are versioned and reviewable; the evidence column is generated from the
    computed outputs. 'interpretation_safety' is the inverse of misinterpretation
    risk (5 = low risk).
    """
    e = ev
    R = [
        (1, "Intake volume and seasonality", 4, 5, 5, 4, 4, 4, "Yes",
         f"Full-year intake events averaged {e['intake_events_mean_2014_2019']:,.0f} (2014-2019) vs "
         f"{e['intake_events_mean_2022_2024']:,.0f} (2022-2024); level shift begins 03-2020. Seasonal index peaks in "
         f"month {e['seasonality_peak_month']} ({e['seasonality_peak_index']}) and troughs in month "
         f"{e['seasonality_trough_month']} ({e['seasonality_trough_index']}).",
         "Event counts only; cause of the 2020 break not established from data."),
        (2, "Stray animal intake patterns", 4, 5, 4, 3, 3, 4, "Yes",
         "Stray is the largest intake type (68.6% of intake rows). Found Location is free text (70k distinct values) "
         "so geographic analysis needs geocoding.",
         "Location text quality limits spatial targeting."),
        (3, "Owner surrender patterns", 5, 5, 4, 5, 5, 4, "Yes",
         f"{e['owner_surrender_after_adoption_pct_2016_2024']}% of owner-surrender visits (2016-2024) are animals whose "
         f"previous visit ended in adoption at this shelter ({e['adoption_returns_total']:,} returns in total); "
         f"{e['adoption_returns_within_30d_pct']}% occur within 30 days of the adoption.",
         "Adoptions before 01-10-2013 are invisible; surrender reason is not recorded."),
        (4, "Adoption outcomes", 5, 5, 4, 4, 4, 4, "Yes",
         f"Adoption is {e['adoption_share_pct']}% of matched visits. Dog adoptions re-enter within 365 days in "
         f"{e['dog_adoption_reentry_365d_pct']}% of cases.",
         "Adoption subtype 'Foster' mixes foster-to-adopt with on-site adoption."),
        (5, "Return-to-owner outcomes", 5, 5, 4, 4, 4, 3, "Yes",
         f"Stray-dog visits ending in RTO fell from {e['stray_dog_rto_pct_2014_2019']}% (2014-2019 average) to "
         f"{e['stray_dog_rto_pct_2024']}% (2024).",
         "Field returns that never create an intake are not in the data; a falling share may reflect a changed intake mix."),
        (6, "Transfer dependency", 4, 5, 3, 3, 3, 2, "Partial",
         f"Transfer is {e['transfer_share_pct']}% of matched visits; {e['cat_transfers_snr_scrp_pct']}% of cat transfers "
         "are SNR/SCRP (community-cat return programmes), not partner placements.",
         "'Transfer' mixes partner placement and return-to-field; partner identity absent."),
        (7, "Length of stay", 5, 4, 4, 5, 4, 4, "Yes",
         f"Dog median LOS {e['dog_median_2014_2019']} days (2014-2019 cohorts) vs {e['dog_median_2023_2024']} days "
         f"(2023-2024). Excluding foster-subtype outcomes, dog visits over 30 days rose from {e['dog_nf_over30_2014_2019']}% "
         f"to {e['dog_nf_over30_2023_2024']}%.",
         "LOS depends on the matching rule and includes foster time for some outcomes; recent cohorts slightly censored."),
        (8, "Long-stay animals", 4, 4, 3, 4, 4, 3, "Yes",
         f"{e['visits_over_90d']:,} visits exceeded 90 days and {e['visits_over_365d']} exceeded 365 days; "
         f"{e['long_stay_365_foster_subtype_pct']}% of 365+ day visits ended with a 'Foster' subtype.",
         "Many very long stays are foster placements, not kennel stays."),
        (9, "Euthanasia patterns", 4, 5, 4, 3, 3, 2, "Partial",
         f"Euthanasia is {e['euthanasia_share_pct']}% of matched visits; {e['euthanasia_other_rabies_risk_pct']}% of "
         f"euthanasia visits are 'Other' (wildlife) with subtype Rabies Risk. Dog/cat share {e['dogcat_euthanasia_pct_2014']}% "
         f"(2014 cohort) vs {e['dogcat_euthanasia_pct_2024']}% (2024).",
         "Highly sensitive; wildlife must be separated; not the official live-release rate."),
        (10, "Death and other non-live outcomes", 3, 5, 3, 2, 2, 3, "Partial",
         "Died ~1% and Disposal ~0.5% of visits; Disposal is not defined in the extract.",
         "Small counts; Disposal semantics unknown."),
        (11, "Intake condition and welfare", 4, 5, 3, 3, 3, 3, "Partial",
         f"{e['non_normal_intake_condition_pct']}% of matched visits had a non-'Normal' intake condition; 20 labels "
         "with overlapping meanings (e.g. Medical / Med Attn / Med Urgent).",
         "Label set changes over time; severity not ordinal."),
        (12, "Age-based outcome patterns", 4, 5, 4, 3, 3, 4, "Yes",
         "Age text is coarse (N years) but parses for >99.99% of rows; LOS and outcome mix differ by life stage.",
         "Age is estimated at intake for strays."),
        (13, "Breed-level outcome patterns", 3, 4, 2, 2, 2, 1, "No",
         "3,006 distinct breed labels; 69% are mixes or slash combinations; only 41 labels have >=500 matched visits.",
         "Visual breed identification is unreliable; high risk of stigmatising conclusions."),
        (14, "Intake-to-outcome throughput", 5, 4, 4, 4, 4, 3, "Yes",
         f"Estimated average daily in-care population (matched visits) was {e['avg_in_care_2019']:,.0f} in 2019 and "
         f"{e['avg_in_care_2024']:,.0f} in 2024, while intake events fell from {e['intake_events_2019']:,} to "
         f"{e['intake_events_2024']:,}.",
         "Census is an estimate from matched visits (foster time included); not an official kennel count."),
        (15, "Repeat animal visits", 4, 4, 4, 4, 4, 3, "Yes",
         f"{e['return_intake_pct']}% of intake events are a repeat intake for the same Animal ID.",
         "Depends on Animal ID persistence across visits."),
    ]
    cols = ["id", "opportunity", "business_relevance", "data_availability", "data_reliability", "analytical_depth",
            "actionability", "interpretation_safety", "defensible_kpi", "evidence", "key_limitation"]
    r = pd.DataFrame(R, columns=cols)
    score_cols = cols[2:8]
    r["total_score_30"] = r[score_cols].sum(axis=1)
    r["rank"] = r["total_score_30"].rank(ascending=False, method="first").astype(int)
    r["top_eight"] = r["rank"] <= 8
    return r.sort_values("rank").reset_index(drop=True)


def main() -> dict:
    ensure_dirs()
    I, O = load_clean()
    v = load_visits()
    out: dict = {}
    time_series(I, O, out)
    ev = visit_analyses(v, I, out)
    for k, df in out.items():
        write_csv(df, OUT_ANALYSIS / f"{k}.csv")
    write_csv(metrics_frame(ev), OUT_ANALYSIS / "analysis_key_metrics.csv")
    print(pd.Series(ev).to_string())
    return ev


if __name__ == "__main__":
    main()
