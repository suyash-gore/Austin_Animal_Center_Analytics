# Visit-Matching Methodology

**Status:** Recommended method implemented and validated; awaiting candidate approval (DECISION_LOG
D-010 to D-013). **Code:** `analysis/matching_engine.py` (pure functions), `analysis/match_visits.py`
(comparison and outputs). **Outputs:** `outputs/matching/`. **Tests:** `analysis/tests/test_matching.py`,
`analysis/tests/test_pipeline_outputs.py`.

---

## 1. The problem

The intake file records arrivals and the outcome file records departures. Both carry `Animal ID`, but
an animal can come in many times (13,487 Animal IDs have two or more intakes; one has 33). Joining
the files on Animal ID alone multiplies rows and produces nonsense durations. A *visit* — one stay
from intake to outcome — must be reconstructed. Neither file has a visit or sequence number.

## 2. The rule in plain language (for stakeholders)

> **A visit starts when an animal is taken in and ends at the next outcome recorded for that animal,
> as long as the animal was not taken in again in between.**
>
> If an animal is recorded as taken in twice without an outcome in between, the first intake is treated
> as having no recorded outcome. If an outcome has no open intake before it, it is left unmatched.
> When an outcome only has a date (no time), it counts as happening later that same day.

Every intake and every outcome is used at most once, durations are never negative, and an animal can
never be in two visits at the same time.

## 3. Event preparation

* **Analytic events:** exact duplicate rows are excluded (36 intake, 26 outcome excess copies; D-009),
  leaving 173,776 intake and 173,749 outcome events. Same-ID/same-timestamp rows that differ in another
  field are kept and flagged.
* **Timestamps:** source-local wall clock, timezone-naive (D-008). Outcome offsets are metadata only.
* **Event IDs:** `INnnnnnn` / `OUTnnnnnn` = source row order; `source_row` = line in the raw CSV.
* **Ordering:** by Animal ID, timestamp, then event ID (deterministic). On equal timestamps an intake
  sorts before an outcome, so a zero-length visit is possible.

## 4. Methods compared

| Code | Method | One-to-one | Chronological |
|---|---|---|---|
| `rank` | **A. Animal ID + derived sequence.** k-th intake ↔ k-th outcome per animal. The source has no sequence field; this reproduces the earlier "sequence" run. | yes | **no** |
| `fifo` | **B. FIFO.** Each outcome (in time order) takes the *earliest* unmatched intake at or before it. | yes | yes |
| `lifo` | **C. LIFO.** Each outcome takes the *latest* unmatched intake at or before it. | yes | yes |
| `adjacent` | **D. Adjacent-event (state machine).** Walk the animal's events in time order; an intake opens a visit (closing any open one as "no outcome"); an outcome closes the open visit. | yes | yes, and non-overlapping |
| `asof` | Latest preceding intake **without** one-to-one restriction (reconciliation only). | **no** | yes |
| `*_dp` | B, C or D plus the **date-precision rule** (D-011) and the **same-day time-reversed second pass** (D-012). | yes | yes |

### 4.1 Results (exact duplicates removed)

Source: `outputs/matching/method_comparison.csv` (raw-row stage also in that file).

| Method | Matched | Unmatched intakes | Unmatched outcomes | Reused intakes | Negative durations | Outcomes with >1 open intake | Pairs spanning another intake | Same-day | > 365 d | P50 | P90 | P99 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| rank | 172,809 | 967 | 940 | 0 | **784** | – | 30 | 22,346 | 574 | 5.99 | 55.25 | 214.13 |
| asof | 172,220 | 1,638 | 1,529 | **82** | 0 | – | 25 | 21,737 | 587 | 6.02 | 55.84 | 216.79 |
| fifo | 172,170 | 1,606 | 1,579 | 0 | 0 | 60 | 54 | 21,718 | 583 | 6.02 | 55.84 | 216.03 |
| lifo | 172,170 | 1,606 | 1,579 | 0 | 0 | 60 | 31 | 21,733 | 578 | 6.02 | 55.81 | 215.24 |
| adjacent | 172,138 | 1,638 | 1,611 | 0 | 0 | 52 | 4¹ | 21,733 | 577 | 6.02 | 55.80 | 215.05 |
| fifo_dp | 172,799 | 977 | 950 | 0 | 630² | 52 | 42 | 22,350 | 580 | 6.00 | 55.47 | 214.95 |
| lifo_dp | 172,807 | 969 | 942 | 0 | 641² | 52 | 30 | 22,374 | 578 | 6.00 | 55.38 | 214.30 |
| **adjacent_dp** | **172,772** | **1,004** | **977** | **0** | 641² | 46 | **0** | 22,374 | 577 | 6.00 | 55.34 | 214.24 |

¹ Strict `adjacent` cannot overlap under its own timestamps; the 4 are intakes later on the same day as
a midnight-stamped (date-only) outcome, which the overlap check reads as end-of-day.
² Raw durations below zero only for same-date events (date-only outcome or time-reversed pair);
floored to 0 and flagged `los_floored_to_zero`. Accepted visits never have negative LOS.

No method produces an animal-type mismatch between intake and outcome (0 in every run).

### 4.2 How the methods differ

`outputs/matching/method_pairwise_differences.csv`

* **FIFO vs LIFO** (strict): 90 outcomes assigned a different intake across 51 Animal IDs; 81 across 47
  IDs when choices between two intakes with an *identical* timestamp are excluded.
* **LIFO vs adjacent**: identical wherever both match; adjacent leaves 32 (strict) / 35 (`_dp`)
  further outcomes unmatched — exactly the cases where LIFO reaches back past a newer intake.
* **adjacent vs adjacent_dp**: with the date-precision and same-day rules, 637 outcomes are matched only
  under `adjacent_dp`, 3 only under strict `adjacent`, and 4 are reassigned (net +634 visits).
* **rank vs FIFO**: 754 outcomes differ — the rank join pairs events regardless of time order.

### 4.3 Why `adjacent_dp` is recommended

1. **Rejects impossible visits.** FIFO pairs an outcome with the oldest open intake, so when an
   intake's outcome is missing, FIFO links it to a much later outcome and the visit *overlaps* the
   animal's next intake (42 visits under `fifo_dp`). Among outcomes with multiple open intakes, FIFO's
   median LOS is 27.0 days vs 3.9 for LIFO: FIFO is attaching stale intakes. LIFO nests visits instead
   (30). Only the adjacent rule guarantees non-overlapping visits.
2. **Robust to duplicates.** Strict adjacent yields 172,138 matches with or without exact duplicates;
   FIFO and LIFO change by 35 (§6).
3. **Recovers genuine same-day visits.** 621 outcomes were unmatched under strict timestamps although
   an unmatched intake for the same animal existed later that day — 403 stamped midnight (date-only).
   The date-precision rule recovers them inside the event sequence (so later visits stay correct, e.g.
   A554047, returned to owner on the day of intake on 14-05-2016 and again on 26-05-2016), and the second pass recovers 225 more.
4. **Small cost.** 35 fewer matches than `lifo_dp` (0.02%), and those are precisely the ambiguous
   overlap cases, which are listed for review rather than forced.
5. **Explainable** in one sentence (§2).

## 5. Rules for the edge cases

| Situation | Rule | Count (adjacent_dp) | Flag / file |
|---|---|---:|---|
| Intake and outcome on the same calendar date | Matched normally; LOS from timestamps (< 1 day) | 22,374 same-day visits; 32,642 < 24 h | `same_day_visit` |
| Equal intake and outcome timestamps | Eligible (intake sorts first); LOS = 0 | included above | |
| Outcome stamped 00:00:00 (date-only) | Sequenced at end of its day (D-011); stored value unchanged | 3,787 matched visits (3,583 with `-05:00` offset) | `outcome_is_midnight`, `outcome_time_is_date_only` |
| Same-date outcome time earlier than intake | Second pass pairs both if unmatched and nothing between (D-012); LOS = 0 | 225 | `match_rule = same_day_time_reversed` |
| Negative raw duration (same date only) | Floored to 0 | 641 | `los_floored_to_zero`, `los_days_raw` |
| Multiple open intakes before an outcome | Latest intake is used; earlier ones become "superseded" unmatched intakes | 46 outcomes; 38 superseded intakes | `multiple_open_intakes`, `unmatched_intakes.csv` |
| Outcome with no eligible preceding intake | Left unmatched with a reason | 977 | `unmatched_outcomes.csv` |
| Intake with no subsequent outcome | Left unmatched (open or missing outcome) | 1,004 | `unmatched_intakes.csv`, `days_open_at_extract_end` |
| Long stays | Retained; flagged | 577 > 365 d; 7,777 > 90 d | `long_stay_365plus`, `outputs/analysis/long_stay_visits_365plus.csv` |
| Assignment differs between FIFO/LIFO/adjacent, or > 1 open intake | Kept with recommended assignment; flagged for review | 45 animals; 84 matched visits | `assignment_method_dependent`, `ambiguous_matches.csv` |

### 5.1 Unmatched records

| Unmatched intakes (1,004) | Rows |
|---|---:|
| Animal ID has no outcome records (743 dated 2025, 106 dated 2024 — mostly animals still in care at extract end) | 864 |
| No outcome recorded after this intake (open at extract end or outcome not recorded) | 102 |
| Superseded: animal has a later intake before any outcome | 38 |

| Unmatched outcomes (977) | Rows |
|---|---:|
| Animal ID has no intake records (704 dated 2013 — intake likely before 01-10-2013) | 814 |
| No intake recorded before this outcome (110 dated 2013–2014) | 112 |
| Preceding intake already closed by an earlier outcome (extra / duplicate outcome) | 51 |

Median days open at extract end for unmatched intakes: 35 (`days_open_at_extract_end`). Unmatched
records appear in `candidate_visits.csv` with `visit_status` "Intake without matched outcome" /
"Outcome without matched intake" so that visit-table totals reconcile to event totals:
172,772 + 1,004 = 173,776 intake events; 172,772 + 977 = 173,749 outcome events.

### 5.2 Ambiguous records

`outputs/matching/ambiguous_matches.csv` lists the full event stream for each of the 45 Animal IDs whose
pairing depends on the method, with the partner event assigned by `fifo_dp`, `lifo_dp` and
`adjacent_dp` side by side. Typical patterns: two intakes on the same day (one probably a data
correction, e.g. A672744 recorded as both Public Assist and Owner Surrender at the same minute); an
intake whose outcome was never recorded followed months later by a new intake; two outcomes minutes
apart (e.g. A680834, two Transfers on 13-06-2014). Excluding these 84 method-dependent visits does
not change any LOS percentile by more than 0.04 days (`los_percentiles.csv`).

## 6. Reconciliation with preliminary runs

`outputs/matching/preliminary_reconciliation.csv`, `outputs/matching/deduplication_impact.csv`

| Preliminary figure | Reproduced | Explanation |
|---|---:|---|
| Sequence pairs 172,850; 781 outcome before intake | 172,850; 781 | `rank` on raw rows (exact) |
| Latest preceding intake, no 1:1: 155,448 | 172,245 | **Not reproduced.** Closest related counts: 154,831 Animal IDs with a match, 155,423 IDs present in both files. Variants tested (UTC conversion, date-only, per-animal) do not give 155,448. The method reuses 107 intakes and is rejected either way. |
| Run 1: 172,205 matches; 1,570 / 1,607 unmatched; 96 multi-open | identical | FIFO **or** LIFO on raw rows (they match the same number) |
| Dedup run: 172,170; 1,579 / 1,606; 60 multi-open | identical | FIFO or LIFO after exact-duplicate removal |
| FIFO/LIFO changed 81 assignments, 47 IDs | 81 / 47 | Exact when choices between identical-timestamp intakes are excluded; 90 / 51 otherwise |
| 578 stays > 365 days | 578 | LIFO, deduplicated |
| LOS P50 6.02, P75 19.99, P90 55.81, P95 84.90, P99 215.63 | LIFO dedup: 6.02, 19.98, 55.81, 84.90, 215.24 | P75 and P99 match LIFO on *raw* rows (19.99, 215.63) — the preliminary table appears to mix the two stages |

**The 35-match difference (172,205 → 172,170).** Under FIFO on raw rows, the 36 excess intake copies
were matched: 20 to excess outcome copies (a duplicated intake *and* outcome), 15 to genuine later
outcomes, and 1 raw pair involved an excess outcome only. Removing duplicates loses 38 pairs and
creates 3 new ones (net −35). Unmatched outcomes therefore rise by 9 (35 − 26 removed outcome rows) and
unmatched intakes fall by 1 (36 − 35). The multiple-open-intake count falls from 96 to 60 because
duplicate intake copies are themselves "open intakes". The adjacent rule is unaffected (172,138 both).

## 7. Length of stay

**Definition (D-013):** LOS days = (outcome timestamp − intake timestamp) / 24 h for matched visits,
floored at 0 only under D-011/D-012. In Power BI implement as a measure, e.g.
`Median LOS (days) = MEDIAN(Visits[los_days])` filtered to `visit_status = "Matched visit"`.

`outputs/matching/los_percentiles.csv`, `los_distribution.csv`

| Scope | Visits | P25 | P50 | P75 | P90 | P95 | P99 | Mean | > 365 d |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| All matched visits (recommended) | 172,772 | 2.00 | **6.00** | **19.89** | **55.34** | **84.72** | **214.24** | 21.01 | 577 |
| Primary rule only (excl. 225 same-day reversed) | 172,547 | 2.01 | 6.00 | 19.93 | 55.56 | 84.81 | 214.46 | 21.03 | 577 |
| Excluding same-day visits | 150,398 | 3.97 | 7.25 | 25.06 | 60.96 | 91.83 | 231.85 | 24.11 | 577 |
| Excluding method-dependent visits | 172,688 | 2.00 | 6.00 | 19.89 | 55.38 | 84.75 | 214.24 | 21.01 | 577 |
| Dogs | 94,015 | 2.71 | 5.99 | 15.20 | 50.33 | 87.12 | 253.11 | 20.93 | 445 |
| Cats | 68,899 | 2.14 | 7.18 | 31.09 | 62.91 | 86.38 | 174.78 | 23.24 | 123 |

LOS bands: < 1 day 18.89%; 1–6 days 35.53%; 7–29 days 26.30%; 30–89 days 14.77%; 90–179 days 3.13%;
180–364 days 1.03%; 365+ days 0.33%.

Versus the preliminary distribution, the median moves from 6.02 to 6.00 days and the upper
percentiles fall slightly (P90 55.81 → 55.34) because 634 additional visits (net), almost all
same-day, are now matched. The conclusions are not sensitive to the matching variant: every one-to-one chronological
method gives P50 6.00–6.02 and P90 55.3–55.8.

**Interpretation limits.** LOS is time in the shelter's custody, not necessarily kennel time:
the 18,136 visits ending with subtype `Foster` / `In Foster` have median LOS 54.05 days vs 5.03 for all
other visits (`outputs/analysis/los_by_foster_subtype.csv`), and 75.2% of 365+ day visits end with a
foster subtype. Intake cohorts near 05-05-2025 are right-censored (long stays still open).

## 8. Candidate visit dataset

`outputs/matching/candidate_visits.csv` — 174,753 rows = 172,772 matched + 1,004 intake-only + 977
outcome-only. Column definitions: `docs/DATA_DICTIONARY.md`. Key traceability fields: `visit_id`
(`V-` + intake event ID, or outcome event ID for outcome-only rows), `intake_event_id`,
`outcome_event_id`, `matching_method` (`adjacent_dp`), `match_rule`.

## 9. Validation performed

* One-to-one: every intake and outcome event ID appears at most once (test).
* Non-negative: all accepted `los_days` ≥ 0; flooring only on same-date events (test).
* No overlapping visits for any animal (test).
* Totals reconcile to event counts, and unmatched files equal unmatched rows (test).
* Key metrics recomputed from the raw files inside the test suite (test).
* Pipeline run twice: all outputs byte-identical.

## 10. Limitations and open points

* The rule cannot know the truth for the 45 ambiguous animals; any rule is a choice. They are listed.
* "Superseded" intakes may be genuine visits whose outcome was not recorded; their LOS is unknown.
* Outcomes before 01-10-2013 intakes cannot be matched (data starts mid-stream).
* The same-day reversed rule assumes recording lag (median reversal 4.0 hours; outcomes mostly Transfer,
  Euthanasia, RTO). A genuine leave-and-return within one day would be mis-paired; this cannot be
  verified from the extract, so the 225 visits are flagged for sensitivity analysis.
* Approval of D-010 to D-013 is pending (DECISION_LOG Stage 2).

## 11. Sensitivity validation (added 23-11-2026)

Script: `analysis/sensitivity_analysis.py` → `outputs/sensitivity/`. The current outputs in
`outputs/matching/` are unchanged; every scenario below uses the same adjacent-event rule and analytic
events (exact duplicates removed). Test: `analysis/tests/test_sensitivity_outputs.py`.

### 11.1 Midnight outcomes split (`midnight_outcome_split.csv`)

| Group (analytic events) | Outcome events | Most common outcome types |
|---|---:|---|
| Midnight with `-05:00` offset | 3,583 | Transfer 2,490; Adoption 768; RTO 146 |
| Midnight without offset | 204 | Transfer 148; Euthanasia 28; Died 12 |
| All midnight | 3,787 | (3,788 / 3,584 in raw rows; one offset row is an exact duplicate) |

Original timestamps and offsets are untouched (`outcome_datetime`, `outcome_tz_offset` in the cleaned file).

### 11.2 Scenario comparison (`scenario_comparison.csv`)

| Scenario | Matched | Unmatched intakes / outcomes | By reversed pass | Negative raw (floored) | Zero-day stays | P50 | P75 | P90 | P95 | P99 | > 365 d |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **A** all midnight date-only + reversed pass (**current**) | 172,772 | 1,004 / 977 | 225 | 641 | 664 | 6.00 | 19.89 | 55.34 | 84.72 | 214.24 | 577 |
| A excluding the 225 reversed matches | 172,547 | 1,229 / 1,202 | 0 | 416 | 439 | 6.00 | 19.93 | 55.56 | 84.81 | 214.46 | 577 |
| **B** offset-only date-only + reversed pass | 172,772 | 1,004 / 977 | 304 | 641 | 664 | 6.00 | 19.89 | 55.34 | 84.72 | 214.24 | 577 |
| B without reversed pass | 172,468 | 1,308 / 1,281 | 0 | 337 | 360 | 6.00 | 19.94 | 55.65 | 84.83 | 214.62 | 577 |
| **C** strict source timestamps | 172,138 | 1,638 / 1,611 | 0 | 0 | 23 | 6.02 | 19.98 | 55.80 | 84.90 | 215.05 | 577 |
| C strict + reversed pass | 172,773 | 1,003 / 976 | 635 | 635 | 658 | 6.00 | 19.89 | 55.35 | 84.73 | 214.27 | 577 |

All six scenarios: 0 reused intakes, 0 overlapping visits. "Zero-day stays" = floored cases plus 23
visits with identical intake and outcome timestamps.

**Reading.** A and B produce the *same* final pair set size: the 204 non-offset midnight outcomes that
B does not treat as date-only are recovered by the second pass instead (304 vs 225). Strict timestamps
(C) lose 634 visits, almost all same-day. The LOS distribution moves by at most 0.46 days at P90 and
0.81 days at P99 across all scenarios; no long stay is affected.

### 11.3 Effect on the three candidate findings

| Metric | A (current) | A excl. 225 reversed | B | C strict | Max spread |
|---|---:|---:|---:|---:|---:|
| Dog median LOS, 2014–2019 (avg of annual medians) | 5.12 | 5.12 | 5.12 | 5.13 | 0.01 |
| Dog median LOS, 2023–2024 (avg of annual medians) | 12.35 | 12.38 | 12.35 | 12.39 | 0.04 |
| Dog non-foster > 30 d, 2014–2019 (pooled %) | 8.66 | 8.67 | 8.66 | 8.70 | 0.04 |
| Dog non-foster > 30 d, 2023–2024 (pooled %) | 22.55 | 22.58 | 22.55 | 22.60 | 0.05 |
| Owner surrenders after any prior adoption, 2016–2024 (%) | 24.45 | 24.46 | 24.45 | 24.49 | 0.04 |
| Owner surrenders within 30 d of adoption, 2016–2024 (% of surrenders) | 14.87 | 14.89 | 14.87 | 14.90 | 0.03 |
| Stray-dog RTO share, 2014–2019 (avg of annual %) | 29.50 | 29.47 | 29.50 | 29.47 | 0.03 |
| Stray-dog RTO share, 2024 (%) | 12.49 | 12.51 | 12.49 | 12.48 | 0.03 |

None of the three findings depends on the date-only or time-reversed assumptions.

### 11.4 Record-level review of the 225 time-reversed matches (`same_day_reversed_review.csv`)

Each row carries both event IDs and source rows, raw timestamp text, offset, the reversal in hours,
intake type/condition/age/location, outcome type/subtype, other events for the animal within one day and
an assessment with its reason. Assessments are **not confirmations**:

| Assessment | Rows | Rule |
|---|---:|---|
| Plausible — consistent with recording-order lag (unconfirmed) | 188 | Outcome ≤ 8 h before intake, not an adoption, no other event for the animal within 1 day, no owner-surrender → RTO contradiction |
| Ambiguous — needs review | 37 | 30 with outcome > 8 h before intake; 5 adoptions logged before intake; 1 with another event within 1 day; 1 owner surrender returned to owner |

Pattern: outcomes are logged mostly 07:00–12:00 and the intake later the same day (median reversal
4.0 h, max 11.7 h). Outcome mix: Transfer 96 (mostly Partner/SCRP), Euthanasia 60 (36 Rabies Risk, all
animal type Other, 35 of them Wildlife intakes), RTO 38, Died 17, Disposal 7, Adoption 5, Relocate 1 — outcomes that commonly occur on the intake
day. None is a midnight outcome. Excluding all 225 changes no headline by more than 0.22 days (P90).

### 11.5 Conclusion

No sensitivity reveals a material problem; the recommended method (`adjacent_dp`, scenario A) is
retained. D-011 and D-012 remain **pending approval** (DECISION_LOG D-016). For conservative reporting,
filter `match_rule <> "same_day_time_reversed"` (scenario "A excluding") — results in §11.2–11.3.
