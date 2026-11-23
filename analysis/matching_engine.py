"""Visit-matching algorithms (pure functions, no file I/O).

Every algorithm takes two event frames with the columns
``event_id``, ``animal_id`` and ``dt`` (timezone-naive datetime) and returns a
frame of matched pairs with columns ``intake_event_id``, ``outcome_event_id``
and ``n_eligible`` (number of unmatched, eligible intakes available when the
outcome was assigned; NA where not applicable).

Eligibility (all chronological methods): an intake is eligible for an outcome
when ``intake.dt <= outcome.dt`` for the same Animal ID. Equal timestamps are
eligible (zero-length visit). Events are ordered by timestamp and then by
source order (event_id), so results are deterministic.

Methods
-------
rank      Pair the k-th intake with the k-th outcome per animal (a *derived*
          sequence; the source has no sequence field). No chronology check.
fifo      Each outcome, in time order, takes the EARLIEST unmatched eligible
          intake. One-to-one.
lifo      Each outcome, in time order, takes the LATEST unmatched eligible
          intake. One-to-one.
adjacent  Event-stream state machine. Walk the animal's events in time order
          (intake before outcome on ties). An intake opens a visit; if a visit
          is already open, the earlier intake is closed as "no recorded
          outcome". An outcome closes the open visit, or is unmatched when none
          is open. One-to-one AND guarantees non-overlapping visits.
asof      Latest preceding intake with NO one-to-one restriction (intakes can
          be reused). Reconciliation only; never acceptable as a visit key.
"""
from __future__ import annotations

from bisect import bisect_right

import numpy as np
import pandas as pd

METHODS = ("rank", "fifo", "lifo", "adjacent", "asof")
ONE_TO_ONE_CHRONO = ("fifo", "lifo", "adjacent")


def _prep(df: pd.DataFrame) -> pd.DataFrame:
    out = df[["event_id", "animal_id", "dt"]].copy()
    out = out[out["dt"].notna()]
    return out.sort_values(["animal_id", "dt", "event_id"], kind="mergesort").reset_index(drop=True)


def _groups(df: pd.DataFrame) -> dict:
    """animal_id -> (list of dt int64 ns, list of event_id), already time-sorted."""
    ids = df["animal_id"].to_numpy()
    dts = df["dt"].to_numpy("datetime64[ns]").astype(np.int64)
    evs = df["event_id"].to_numpy()
    out: dict = {}
    if len(df) == 0:
        return out
    bounds = np.flatnonzero(ids[1:] != ids[:-1]) + 1
    starts = np.r_[0, bounds]
    ends = np.r_[bounds, len(df)]
    for s, e in zip(starts, ends):
        out[ids[s]] = (dts[s:e].tolist(), evs[s:e].tolist())
    return out


def _pairs_frame(rows: list) -> pd.DataFrame:
    df = pd.DataFrame(rows, columns=["intake_event_id", "outcome_event_id", "n_eligible"])
    df["n_eligible"] = df["n_eligible"].astype("Int64")
    return df


def match_rank(intakes: pd.DataFrame, outcomes: pd.DataFrame) -> pd.DataFrame:
    i = _prep(intakes)
    o = _prep(outcomes)
    i["k"] = i.groupby("animal_id").cumcount()
    o["k"] = o.groupby("animal_id").cumcount()
    m = i.merge(o, on=["animal_id", "k"], suffixes=("_i", "_o"))
    out = pd.DataFrame(
        {"intake_event_id": m["event_id_i"], "outcome_event_id": m["event_id_o"], "n_eligible": pd.NA}
    )
    out["n_eligible"] = out["n_eligible"].astype("Int64")
    return out


def _match_queue(i_dts, i_ids, o_dts, o_ids, latest: bool) -> list:
    rows = []
    used = [False] * len(i_dts)
    for odt, oid in zip(o_dts, o_ids):
        k = bisect_right(i_dts, odt)  # intakes [0, k) have dt <= odt
        eligible = [j for j in range(k) if not used[j]]
        if not eligible:
            continue
        j = eligible[-1] if latest else eligible[0]
        used[j] = True
        rows.append((i_ids[j], oid, len(eligible)))
    return rows


def _match_adjacent(i_dts, i_ids, o_dts, o_ids) -> list:
    # merged stream; kind 0 = intake sorts before kind 1 = outcome on ties
    stream = [(d, 0, e) for d, e in zip(i_dts, i_ids)] + [(d, 1, e) for d, e in zip(o_dts, o_ids)]
    stream.sort(key=lambda t: (t[0], t[1], t[2]))
    rows, open_id, n_open = [], None, 0
    for _, kind, ev in stream:
        if kind == 0:
            n_open += 1
            open_id = ev
        elif open_id is not None:
            rows.append((open_id, ev, n_open))
            open_id, n_open = None, 0
    return rows


def match_chronological(intakes: pd.DataFrame, outcomes: pd.DataFrame, method: str) -> pd.DataFrame:
    if method not in ONE_TO_ONE_CHRONO:
        raise ValueError(f"unknown chronological method {method!r}")
    gi = _groups(_prep(intakes))
    go = _groups(_prep(outcomes))
    rows: list = []
    for aid, (o_dts, o_ids) in go.items():
        if aid not in gi:
            continue
        i_dts, i_ids = gi[aid]
        if method == "adjacent":
            rows.extend(_match_adjacent(i_dts, i_ids, o_dts, o_ids))
        else:
            rows.extend(_match_queue(i_dts, i_ids, o_dts, o_ids, latest=(method == "lifo")))
    return _pairs_frame(rows)


def match_asof(intakes: pd.DataFrame, outcomes: pd.DataFrame) -> pd.DataFrame:
    i = _prep(intakes).sort_values(["dt", "event_id"], kind="mergesort")
    o = _prep(outcomes).sort_values(["dt", "event_id"], kind="mergesort")
    m = pd.merge_asof(
        o, i.rename(columns={"event_id": "intake_event_id", "dt": "idt"}),
        left_on="dt", right_on="idt", by="animal_id", direction="backward",
    )
    m = m[m["intake_event_id"].notna()]
    out = pd.DataFrame(
        {"intake_event_id": m["intake_event_id"].to_numpy(), "outcome_event_id": m["event_id"].to_numpy()}
    )
    out["n_eligible"] = pd.array([pd.NA] * len(out), dtype="Int64")
    return out


def run_method(intakes: pd.DataFrame, outcomes: pd.DataFrame, method: str) -> pd.DataFrame:
    if method == "rank":
        return match_rank(intakes, outcomes)
    if method == "asof":
        return match_asof(intakes, outcomes)
    return match_chronological(intakes, outcomes, method)


def attach_times(pairs: pd.DataFrame, intakes: pd.DataFrame, outcomes: pd.DataFrame) -> pd.DataFrame:
    """Join timestamps/animal IDs back onto a pair frame and compute duration."""
    i = intakes[["event_id", "animal_id", "dt"]].rename(
        columns={"event_id": "intake_event_id", "dt": "intake_dt", "animal_id": "animal_id"})
    o = outcomes[["event_id", "animal_id", "dt"]].rename(
        columns={"event_id": "outcome_event_id", "dt": "outcome_dt", "animal_id": "outcome_animal_id"})
    m = pairs.merge(i, on="intake_event_id", how="left").merge(o, on="outcome_event_id", how="left")
    m["los_days"] = (m["outcome_dt"] - m["intake_dt"]).dt.total_seconds() / 86400.0
    return m


# ----------------------------------------------------------- date precision
def sequencing_key(outcome_dt: pd.Series) -> pd.Series:
    """Ordering key for outcomes under the date-precision rule (D-012).

    Outcomes stamped exactly 00:00:00 carry no reliable time of day (3,584 of
    them also carry a constant '-05:00' offset). For *ordering and eligibility
    only*, they are placed at the end of their calendar day, i.e. after any
    intake recorded on the same date. The stored timestamp is not modified.
    """
    midnight = outcome_dt.dt.strftime("%H:%M:%S") == "00:00:00"
    eod = outcome_dt.dt.normalize() + pd.Timedelta(hours=23, minutes=59, seconds=59)
    return outcome_dt.where(~midnight, eod)


def reconcile_same_day_reversed(pairs: pd.DataFrame, intakes: pd.DataFrame, outcomes: pd.DataFrame) -> pd.DataFrame:
    """Second-pass rule for same-calendar-day, time-reversed events.

    After the primary pass, an UNMATCHED outcome may be paired with an
    UNMATCHED intake of the same animal when (a) both fall on the same calendar
    date, (b) the intake timestamp is later than the outcome timestamp, and
    (c) no other event for that animal lies between them. Candidates are
    resolved one-to-one, closest-in-time first. Returns the additional pairs.
    ``intakes``/``outcomes`` must carry the *stored* timestamps in ``dt``.
    """
    ui = intakes[~intakes["event_id"].isin(pairs["intake_event_id"])]
    uo = outcomes[~outcomes["event_id"].isin(pairs["outcome_event_id"])]
    c = uo.merge(ui, on="animal_id", suffixes=("_o", "_i"))
    c = c[(c["dt_i"] > c["dt_o"]) & (c["dt_i"].dt.normalize() == c["dt_o"].dt.normalize())]
    if c.empty:
        return _pairs_frame([])
    # (c) no intervening event of the same animal
    allev = pd.concat([intakes[["animal_id", "event_id", "dt"]], outcomes[["animal_id", "event_id", "dt"]]])
    allev = allev[allev["animal_id"].isin(c["animal_id"])]
    x = c[["animal_id", "event_id_o", "event_id_i", "dt_o", "dt_i"]].merge(allev, on="animal_id")
    between = x[(x["dt"] > x["dt_o"]) & (x["dt"] < x["dt_i"])]
    blocked = set(zip(between["event_id_o"], between["event_id_i"]))
    c = c[[(a, b) not in blocked for a, b in zip(c["event_id_o"], c["event_id_i"])]]
    c = c.assign(gap=(c["dt_i"] - c["dt_o"])).sort_values(["gap", "event_id_o", "event_id_i"], kind="mergesort")
    rows, used_o, used_i = [], set(), set()
    for o_id, i_id in zip(c["event_id_o"], c["event_id_i"]):
        if o_id in used_o or i_id in used_i:
            continue
        used_o.add(o_id)
        used_i.add(i_id)
        rows.append((i_id, o_id, 1))
    return _pairs_frame(rows)
