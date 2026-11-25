# Claude Project Knowledge Kit — Austin Animal Center Analytics

**Purpose.** A standalone handover of everything established in this project — what was built, how, why,
what the numbers are, how they were checked, and what is still open — written so that another assistant (or
the candidate) can continue without re-deriving context.

**Prepared:** 25-11-2026, from the repository at commit `a5a83ef` (`main`), plus the author's implementation
record from the working sessions. **Repository:** https://github.com/suyash-gore/Austin_Animal_Center_Analytics

**Companion document:** `Austin_Animal_Center_Project_Knowledge_Kit_and_Action_Plan.docx` (repository root,
commit `a5a83ef`) — the candidate's own handover and remaining-work plan (10-slide website, policy research,
speaking script, interview kit, rehearsal). This file does not repeat its plan; it adds the implementation
detail, evidence trail and reasoning behind the work.

### Evidence labels used throughout

| Label | Meaning |
|---|---|
| **[Verified]** | Produced by repository scripts and present in `outputs/`; re-checked 25-11-2026 (`validate_powerbi_model.py`, `pytest`) or read directly from repository files |
| **[Decision]** | Recorded analytical decision in `DECISION_LOG.md` (D-0xx) |
| **[Metadata]** | Read from the PBIX's *readable* report metadata (page/visual JSON) — not from the compressed data model |
| **[User-reported]** | Stated by the candidate (e.g. in the DOCX handover); not observable from the repository |
| **[Assumption]** | Working assumption, documented as such |
| **[Unresolved]** | Open question or gap |

Dates are written `DD-MM-YYYY`. Numbers use US separators.

---

## Contents

1. Project overview
2. Project chronology
3. Source data
4. Analytical methodology
5. Analytical findings
6. Python implementation
7. Power BI implementation
8. Validation and testing
9. Important decisions and rationale
10. Limitations and unresolved questions
11. Current project status
12. Interview defence notes
- Appendix A — Number sheet (single source for quoting)
- Appendix B — File index
- Appendix C — Instructions for the next assistant

---

## 1. Project overview

### 1.1 Assignment

A Power BI & CRM interview exercise. The hiring-team brief (`DECISION_LOG.md` §2):

> *You are the analyst for an animal shelter. The director wants to know how animals come in, what happens to
> them, and where to act.*

**Required deliverable:** one Power BI report (`.pbix`), 2–3 pages, using both supplied CSV datasets.
**Mandatory elements:**

1. A data model linking intakes to outcomes, with a date table.
2. Length of stay (LOS) per visit, implemented as a measure.
3. A trend over time including a year-over-year comparison.
4. Slicers for animal type, intake type and date.
5. Three findings the director should act on.

**Dates stated in the brief [Decision §2]:** PBIX due Wednesday 25-11-2026; interview requested Thursday
26-11-2026, 17:00–19:00 IST, 45–50 minutes.

### 1.2 Business problem and scope

* Translate two event logs (intakes, outcomes) into a defensible picture of shelter demand, outcomes and time to
  outcome, and select three evidence-backed, actionable findings.
* **Guiding principle [Decision]:** correctness, traceability and business usefulness over decorative complexity;
  every headline number must be reproducible from scripts and documented definitions.
* **D-001:** investigate broadly (15 opportunities), present selectively (top 8 internally, 3 for the director).
* **D-002:** three-page report (Executive Summary, Shelter Overview, Operational Insights).
* **D-003/D-004:** a separate single-page interactive presentation website, using
  `references/design/Vetology_Week6_Presentation.html` only as visual inspiration (not content). **Not started.**
* **D-005:** US number format; dates displayed `DD-MM-YYYY` while stored as real date types.
* **D-006:** keep dataset evidence, local policy context and interpretation as separate layers.
* **D-007:** no dashboard build before the audit and matching were validated (followed).

### 1.3 Deliverables and their state

| Deliverable | State |
|---|---|
| Power BI report | `powerbi/Austin_Animal_Center_Analytics_Final.pbix` — **submitted [User-reported]**; in repo [Verified] |
| Data audit, visit matching, analysis | Complete and validated [Verified] |
| Power Query / DAX source files, model documentation | Complete [Verified]; loaded into the PBIX manually by the candidate [User-reported] |
| README, docs, decision log, changelog | Complete; two stale filename references (§10.4) |
| Presentation website (10 slides) | **Not started** (placeholders `website/`, `presentation/`) |
| Policy / environmental-health research, speaking script, interview kit | **Not started** (planned in the DOCX) |

---

## 2. Project chronology

All commit hashes are on `main`. "Claude" commits were made by the assistant; "Suyash Gore" commits by the
candidate.

| Date | Commit(s) | Phase / milestone |
|---|---|---|
| 23-11-2026 | `427e1ac` (candidate) | Initial structure: `DECISION_LOG.md`, README, CHANGELOG, raw CSVs, blank PBIX (`powerbi/Austin_Animal_Center_Analytics.pbix`, 16,674 bytes), design reference, folder placeholders |
| 23-11-2026 | `e3d6b24` | **Audit + matching framework:** `common.py`, `matching_engine.py`, `audit_datasets.py`, `match_visits.py`, `explore_business_opportunities.py`, `run_all.py`, 41 tests, `CLAUDE.md`, D-008–D-015 |
| 23-11-2026 | `1552ba8` | **Validated outputs:** `data/processed/`, `outputs/audit/`, `outputs/matching/`, `outputs/analysis/` (byte-identical on rerun) |
| 23-11-2026 | `5b7e9cf` | **Reports:** audit report, data dictionary, matching methodology, data-quality register (31 issues), business opportunity register |
| 23-11-2026 | `47f0454` | **Sensitivity validation:** six matching scenarios, review of 225 time-reversed pairs, owner-surrender denominator correction (D-016, D-017) |
| 23-11-2026 | `5e61837` | **Edge-case validation:** primary dataset excludes 225 reversed pairs (D-018), Foster semantics (D-019), exact-timestamp overlap check and interval guard (D-020) |
| 23-11-2026 | `60028da` (candidate) | PR #1 merged `claude/magical-allen-uhauys` → `main` |
| 23-11-2026 | `09e0813` | **Power BI Stage 1:** M queries, relationship spec, DAX library 01–04, `validate_powerbi_model.py`, `docs/POWER_BI_DATA_MODEL.md` |
| 23-11-2026 | `1a0c345` | Conformed `DimIntakeType` (R8/R9) |
| 24-11-2026 | `c4d223b`, `00d9deb`, `900974f`, `ce9564a` (candidate) | Working PBIX created and iterated in Desktop |
| 24-11-2026 | `36d232c` | 416 vs 439 reconciliation: `Visits Under 24 Hours`, `05_Diagnostics.dax` |
| 24-11-2026 | `5eac600` | Six report YoY measures in `DAX_Measures`; `outputs/powerbi/yoy_reference.csv` |
| 24-11-2026 | `af6aca4` (candidate) | Executive Summary background image + updated dashboard |
| 24-11-2026 | `c9d1b3c` | README rewrite; image moved to `assets/images/executive-summary-background.png` |
| 24-11-2026 | `031ec5e` | Executive Summary figure corrected 12.07 → 12.08 days (image pixels for one digit) |
| 24-11-2026 | `682a568` (candidate) | "Final Changes": PBIX renamed `_Working.pbix` → `_Final.pbix` (32,607,642 bytes), embedded image replaced |
| 25-11-2026 | `a5a83ef` (candidate) | DOCX knowledge kit and action plan added |

**Debugging / correction episodes worth remembering** (each changed a number or a claim):

1. Preliminary "sequence" matching was a *derived rank*, not a source field (no sequence field exists).
2. The outcome `-05:00` offset turned out to be an export artefact on date-only rows, not a timezone.
3. 621 strict-timestamp misses were same-day visits with date-only outcomes → date-precision rule (D-011).
4. The owner-surrender 37.21% / 61.68% figures had the wrong denominator for director use (D-017).
5. The 225 time-reversed pairs were moved out of the primary dataset (D-018): matched 172,772 → 172,547.
6. "LOS includes foster time" was withdrawn; LOS is time to final recorded outcome (D-019).
7. 416 vs 439 "zero-day" confusion resolved (§5.4).
8. 12.07 vs 12.08 dog median: image mixed two bases; corrected (§5.2).

---

## 3. Source data

### 3.1 Files and coverage [Verified]

| | Intakes | Outcomes |
|---|---|---|
| File (`data/raw/`, read-only) | `Austin_Animal_Center_Intakes__10_01_2013_to_05_05_2025_.csv` | `Austin_Animal_Center_Outcomes__10_01_2013_to_05_05_2025_.csv` |
| Portal | `data.austintexas.gov/api/views/wter-evkm/rows.csv` | `data.austintexas.gov/api/views/9t4d-g238/rows.csv` |
| SHA-256 | `3473ac90…a4cabb` | `54c34ab8…f818499d` (full values in `data/reference/source_checksums.csv`) |
| Rows × columns | 173,812 × 12 | 173,775 × 12 |
| First / last timestamp | 01-10-2013 07:51 / 04-05-2025 23:44 | 01-10-2013 09:31 / 05-05-2025 07:22 |
| Unique Animal IDs | 156,287 | 156,237 |
| IDs with 2+ rows / rows in repeated IDs / excess rows | 13,487 / 31,012 / 17,525 | 13,507 / 31,045 / 17,538 |

**The extract ends 05-05-2025.** 2013 (from 01-10) and 2025 (to 05-05; 05-05 is a partial day with outcomes
only) are partial years. The last complete day common to both files is **04-05-2025**.

### 3.2 Schemas

* **Intakes:** Animal ID (`A`+6 digits), Name, DateTime (`MM/DD/YYYY hh:mm:ss AM/PM`, no offset), MonthYear
  (`Month YYYY`), Found Location (free text, 70,183 values), Intake Type (6), Intake Condition (20), Animal Type
  (5), Sex upon Intake, Age upon Intake (`N unit(s)`), Breed (3,006), Color (661).
* **Outcomes:** Animal ID, Date of Birth (`YYYY-MM-DD`), Name, DateTime (ISO-8601; `-05:00` suffix on 3,584
  rows), MonthYear (`MM-YYYY`), Outcome Type (11 + blank), Outcome Subtype (26 + blank), Animal Type, Sex upon
  Outcome, Age upon Outcome, Breed (3,010), Color (663).
* Category shares of **rows** (not rates): Stray 68.56%, Owner Surrender 20.46%, Public Assist 6.00%, Wildlife
  3.73%, Abandoned 1.10%, Euthanasia Request 0.15%; Adoption 48.68%, Transfer 28.02%, Return to Owner 14.78%,
  Euthanasia 6.23%, Died 0.96%, Rto-Adopt 0.71%, Disposal 0.50%. Dogs 54.43%, cats 39.88% of intake rows.

### 3.3 Data-quality issues (full register: `docs/DATA_QUALITY_ISSUES.md`, DQ-001…DQ-031) [Verified]

| Issue | Size | Treatment |
|---|---:|---|
| Exact duplicate rows (excess copies) | 36 intake / 26 outcome | flagged; excluded from analytic events |
| Same ID + timestamp, other fields differ | 12 intake rows (6 pairs) / 2 outcome rows (1 pair) | kept, flagged |
| Consecutive same-kind events < 24 h | 10 intake / 17 outcome | kept; resolved by matching |
| `-05:00` offset on outcomes | 3,584 rows, all exactly 00:00:00; 884 in Nov–Feb (true offset −06:00) | metadata only (D-008) |
| Midnight outcomes (date-only) | 3,788 raw / 3,787 analytic (3,583 offset + 204 non-offset) | date-precision rule (D-011) |
| Outcome Subtype blank | 94,115 (54.16%) — structural (RTO 98.9%, Adoption 78.2%, Transfer 0%) | kept blank |
| Outcome Type blank | 46 | "Not recorded" |
| Names missing | 49,991 / 49,784 (≈28.7%); ~43.3k start with `*` (assumed shelter-assigned) | flag |
| Negative ages | 10 / 10; 9 `NULL` outcome ages; 1 `NULL` sex each | flagged invalid |
| DOB after outcome date | 33 | flagged |
| Category changes | `Abandoned` first appears 2020; `Euthanasia Request` ≤ 4/year from 2018 | noted (affects type trends) |
| `MonthYear` consistency | 100% consistent with parsed timestamp in both files | confirms wall-clock reading |

### 3.4 Transformations (derived data only)

* `data/processed/intakes_clean.csv` (173,812 rows) and `outcomes_clean.csv` (173,775 rows): one row per source
  row, event IDs `IN000001…` / `OUT000001…` (source order), `source_row` (CSV line), typed fields, flags as 1/0,
  ISO dates. Exact duplicates are **flagged, not removed** here; Power Query removes them.
* Analytic events after duplicate exclusion: **173,776 intakes, 173,749 outcomes**.
* Age converted to approximate days (year 365.25, month 30.4375, week 7); age bands Under 1 month … 7+ years.
* Provisional outcome grouping (D-014): Rto-Adopt → Return to Owner; Missing/Lost/Stolen grouped; status
  Live (Adoption, RTO, Transfer, Relocate) / Non-live (Euthanasia, Died) / Indeterminate (Disposal, Missing…,
  blank). **Not the City's live-release rate.**

---

## 4. Analytical methodology

### 4.1 Duplicate handling (D-009)

Three classes kept distinct: exact duplicate rows (excluded from analysis), suspected duplicate events
(same ID+timestamp with differing fields, or same-kind events < 24 h apart — kept and flagged), and legitimate
repeat visits (17,489 second-or-later intakes).

### 4.2 Timestamp interpretation (D-008)

Both files are parsed as timezone-naive Austin wall-clock time. Intakes use a strict month-first format.
Outcomes keep the first 19 characters of the ISO string; the offset is stored in `outcome_tz_offset` and never
applied. Evidence: every offset row is midnight; the offset is wrong for winter dates; `MonthYear` agrees 100%.

### 4.3 Visit reconstruction

**Problem:** no visit or sequence key; an Animal ID can have 33 intakes. A naive ID join multiplies rows.

**Methods compared** (`outputs/matching/method_comparison.csv`, exact duplicates removed):

| Method | Matched | Unmatched I / O | Defect |
|---|---:|---:|---|
| `rank` (k-th intake ↔ k-th outcome) | 172,809 | 967 / 940 | 784 negative durations |
| `asof` (latest preceding intake, no 1:1) | 172,220 | 1,638 / 1,529 | 82 reused intakes |
| `fifo` (earliest open intake) | 172,170 | 1,606 / 1,579 | 54 visits span another intake (overlap) |
| `lifo` (latest open intake) | 172,170 | 1,606 / 1,579 | 31 nested visits |
| `adjacent` (state machine) | 172,138 | 1,638 / 1,611 | none structural |
| `*_dp` variants | 172,799 / 172,807 / 172,772 | — | add date-precision + same-day pass |

**Chosen rule — adjacent-event (D-010):** walk each animal's events in time order (intake before outcome on
ties); an intake opens a visit, closing any already-open intake as "no recorded outcome" (superseded); an outcome
closes the open visit or is left unmatched. One-to-one, never overlapping, unaffected by duplicate removal
(172,138 with or without duplicates).

**Why not FIFO:** with a missing outcome, FIFO links an old intake to a much later outcome. Among outcomes with
several open intakes, FIFO's median LOS was 27.0 days vs 3.9 for LIFO (stale intakes), and FIFO creates
physically impossible overlapping visits.

**Date-precision rule (D-011):** outcomes stamped exactly 00:00:00 are sequenced at the end of their day (for
ordering only; stored value unchanged). Motivation: 621 outcomes were unmatched under strict timestamps although
the same animal had an unmatched intake later that day (403 midnight-stamped) — typically same-day returns to
owner (example A554047: outcome 14-05-2016 00:00 RTO, intake 14-05-2016 11:26).

**Same-day time-reversed pass (D-012) and its exclusion (D-018):** a second pass pairs an unmatched outcome with
an unmatched intake of the same animal on the same date when the intake is *later* (no event between). It finds
**225 pairs**. Because no source field proves these are one visit (37 ambiguous on review), they are **excluded
from the primary dataset**, kept in `outputs/matching/same_day_reversed_candidates.csv` and flagged on 450
unmatched rows (`same_day_reversed_candidate`, `candidate_partner_event_id`).

**Primary dataset = `adjacent_dp` chronological pass only (`matching_method = adjacent_dp_primary`).**

### 4.4 Edge-case rules (primary dataset) [Verified]

| Situation | Rule | Count |
|---|---|---:|
| Same calendar date | matched; LOS from timestamps | 22,149 visits |
| Equal timestamps | eligible (intake first); LOS 0 | 23 |
| Date-only outcome on the intake date | raw duration negative → LOS floored to 0, flagged | 416 |
| Multiple open intakes | latest used; earlier "superseded" | 46 outcomes; 38 superseded intakes |
| Method-dependent pairing | kept, flagged | 45 animals; 76 matched visits |
| Long stays | retained, flagged | 577 > 365 days; 7,777 > 90 days |

**Unmatched reasons** (`unmatched_intakes.csv`, `unmatched_outcomes.csv`):

| Intakes (1,229) | | Outcomes (1,202) | |
|---|---:|---|---:|
| Animal ID has no outcome records (743 dated 2025, 106 in 2024) | 864 | Animal ID has no intake records (704 dated 2013) | 814 |
| Same-day reversed candidate | 225 | Same-day reversed candidate | 225 |
| No outcome after this intake | 102 | No intake before this outcome | 112 |
| Superseded by a later intake | 38 | Preceding intake already closed (extra outcome) | 51 |

"Open Intake Visits" (still in care or outcome unrecorded) = 864 + 102 = **966**.

### 4.5 Length of stay (D-013, D-019)

`los_days = (outcome timestamp − intake timestamp) / 24 h`, matched visits only, floored at 0 only for the 416
date-only same-date cases. **Meaning: intake to final recorded outcome — not kennel/shelter-only occupancy.**
Foster placement is not recorded in either file, so shelter vs foster time cannot be separated.

**Foster semantics (D-019)** — established from source fields because the City portal was unreachable from the
work environment (network policy, HTTP 403): `Foster` appears only as a subtype of Adoption (17,945) and RTO (2);
`In Foster` only with Died (377) and Missing (39); no Transfer subtype means foster; only **3 of 17,945**
Adoption/Foster outcomes are followed by another outcome without a new intake. Conclusion: the recorded date is
the final outcome, not a transfer into foster (`outputs/sensitivity/foster_subtype_evidence.csv`).

### 4.6 Partial-year treatment (D-015)

YoY uses complete comparison periods only (years 2015–2024); 2013 is compared via the 01-10→31-12 window and 2025
via 01-01→04-05. Example: 2025 vs 2024 intakes in 01-01→04-05 = 3,745 vs 3,991 (−6.16%).

### 4.7 Sensitivity analysis (`analysis/sensitivity_analysis.py`, `outputs/sensitivity/`) [Verified]

| Scenario | Matched | P50 | P90 | Dog pooled median 2014–19 → 2023–24 | OS after adoption | Stray-dog RTO 2014–19 avg → 2024 |
|---|---:|---:|---:|---|---:|---|
| **A excl. reversed (primary)** | 172,547 | 6.00 | 55.56 | 5.12 → 12.08 | 24.46% | 29.47% → 12.51% |
| A incl. reversed (pre-D-018) | 172,772 | 6.00 | 55.34 | 5.11 → 12.07 | 24.45% | 29.50% → 12.49% |
| B offset-only date-only + pass | 172,772 | 6.00 | 55.34 | 5.11 → 12.07 | 24.45% | 29.50% → 12.49% |
| C strict timestamps | 172,138 | 6.02 | 55.80 | 5.13 → 12.09 | 24.49% | 29.47% → 12.48% |

No scenario moves a finding by more than ~0.05 percentage points / 0.04 days; all scenarios have 0 reused
intakes and 0 overlaps at date level **and** at exact-timestamp level (D-020). A and B produce identical pair
sets: of the 204 non-offset midnight outcomes, 125 match chronologically in both and 79 are paired by the
reversed pass in B instead of the primary pass in A — same intake.

The 225 reversed pairs (`same_day_reversed_review.csv`): 188 "plausible recording-order lag (unconfirmed)",
37 "ambiguous" (30 with > 8 h reversal, 5 adoptions logged before intake, 1 other event within a day, 1 owner
surrender → RTO); median reversal 4.0 h (max 11.7 h); none midnight-stamped.

---

## 5. Analytical findings

### 5.1 The three director findings

All descriptive; **no causal claims**. Source: primary dataset (`outputs/sensitivity/scenario_comparison.csv`,
`A_excl_reversed`; `outputs/analysis/`).

**Finding 1 — Dog time to final recorded outcome more than doubled.**
* Pooled median `los_days`, Dog matched visits, by intake year: **5.12 days** (2014–2019; 61,626 visits; exact
  5.117361) → **12.08 days** (2023–2024; 10,134 visits; exact 12.078472).
* Unweighted average of annual medians: 5.12 → **12.38** (different statistic — always say which one).
* Dog visits without a foster subtype: pooled median 4.95 → 8.94 days; share > 30 days 8.67% → 22.58% (pooled;
  8.68% → 22.61% as averages of annual shares).
* Context: intake events −40% (19,726 in 2019 → 11,815 in 2024) while the estimated average daily in-care
  population (matched visits, not a kennel count) fell only −18% (1,120.1 → 916.4).
* Cohort completeness: 0.26% (2023) and 2.37% (2024) of dog intakes still open → 2024 median, if anything,
  understated.
* Caveat: custody time to final outcome, foster share unknown; cause not established.
* Action: review dogs at day 14 / day 30 with placement plans; track "% of dogs > 30 days".

**Finding 2 — About one in four owner surrenders had a prior shelter adoption.**
* Definition (D-017): matched owner-surrender visit whose immediately preceding matched visit for the same animal
  ended in Adoption; interval = adoption outcome → surrender intake (verified non-negative, 0 failures).
* 2016–2024: **24.46%** (6,668 of 27,256); within 30 days **14.89%** (4,058); within 7 days **8.96%** (2,441).
* Of the 2016–2024 adoption returns: 60.86% within 30 days, 36.61% within 7 days.
* **Do not quote** 37.21% / 61.69% as shares of owner surrenders — they are shares of all 8,065 adoption returns
  across 2013–2025 (`adoption_return_timing.csv`).
* Director headline: "In 2016–2024, 14.9% of owner surrenders were animals we had adopted out within the
  previous 30 days, and 24.5% had been adopted from us at some earlier point."
* Caveat: surrender reasons not recorded; adoptions before 01-10-2013 invisible.
* Action: post-adoption support in the first 30 days.

**Finding 3 — Recorded stray-dog return-to-owner share fell.**
* Share of matched stray-dog visits ending in Return to Owner (incl. Rto-Adopt): **29.46%** (2014–2019 average
  of annual intake-cohort shares, each rounded to 2 dp; unrounded 29.47%; pooled 29.43%) → **12.51%** (2024).
* Absolute stray-dog RTO visits 2,036 (2019) → 386 (2024). RTO is the fastest exit: dogs median 1.82 days, 63.5%
  within 3 days.
* Caveat: field returns without an intake are not in the data; the mix of dogs reaching the shelter may have
  changed.
* Action: microchip/ID checks, found-animal posting, owner-contact data quality, measure field returns.

### 5.2 The Executive Summary image figure (12.07 → 12.08)

The image originally read "5.12 → 12.07 days". 12.07 (12.067014) was the pooled 2023–2024 median **before**
D-018, when 10 dog reversed-candidate visits with LOS 0 were included (historical on that basis was 5.11). The
image therefore mixed bases. Corrected in `031ec5e` (one digit; 1,593 pixels; rest pixel-identical). The final
PBIX embeds the corrected image — **[Verified]** byte-identical to
`assets/images/executive-summary-background.png`.

### 5.3 Supporting findings and context [Verified]

* Intake volume: full-year intake events averaged 18,216 (2014–2019) vs 11,643 (2022–2024). 2020 vs 2019:
  intakes −51.41%, outcomes −50.56%. Monthly YoY −2.0% (01-2020), +1.2% (02-2020), −41.2% (03-2020), −80.8%
  (04-2020); largest 12-month level shift starts 03-2020. **Cause not inferable.**
* Seasonality (2014–2024): intake index peaks May (127.4), June (121.9); troughs February (77.7).
* Visit-level outcome shares (matched visits): Adoption 48.64%, Transfer 28.03%, RTO 15.55%, Euthanasia 6.22%;
  provisional live 92.24%.
* Wildlife intakes: 87.1% end in euthanasia (mostly Rabies Risk); 42.98% of euthanasia visits are animal type
  Other with subtype Rabies Risk.
* 27.42% of cat transfers are Snr/SCRP (community-cat return), not partner placement.
* Repeat intakes: 10.06% of intake events; Owner Surrender 25.94%, Stray 5.39%. Dog adoptions re-enter within
  365 days in 15.0% of cases.
* Long stays: of 577 visits > 365 days, 77.1% dogs, 41.8% owner surrenders, 75.2% end with a foster subtype.
* Foster-subtype visits (18,136): median LOS 54.05 days vs 5.03 for all others.

### 5.4 Short-stay definitions (the 416 vs 439 reconciliation)

| Measure | Definition (matched visits) | Count |
|---|---|---:|
| Same-Day Visits | same calendar date | 22,149 |
| Visits Under 24 Hours | LOS < 1 day | 32,417 |
| Zero-Duration Visits (Diagnostic) | LOS exactly 0 | 439 |
| LOS Floored to Zero (Diagnostic) | date-only outcome on intake date, raw negative → 0 | 416 |
| Identical Timestamp Visits (Diagnostic) | timestamps equal | 23 |

439 = 416 + 23. "Zero-day" must not appear in director visuals. **DAX trap:** `BLANK() = 0` is TRUE, so a
`los_days = 0` filter without the matched-visit filter returns 2,870 (adds 2,431 unmatched rows); the diagnostics
use `==`.

### 5.5 Opportunity register (`docs/BUSINESS_OPPORTUNITY_REGISTER.md`)

Six criteria scored 1–5 (relevance, availability, reliability, depth, actionability, interpretation safety):
1 Owner surrender 28 · 2 Intake volume/seasonality 26 · 3 Adoption 26 · 4 LOS 26 · 5 RTO 25 · 6 Throughput 24 ·
7 Stray intake 23 · 8 Age-based 23 · 9 Repeat visits 23 · 10 Long stays 22 · 11 Euthanasia 21 · 12 Intake
condition 21 · 13 Transfer dependency 20 · 14 Death/other non-live 18 · 15 Breed 14. Scores are analyst
judgement recorded in code; evidence text is generated. Status in the register: **candidate findings, approval
pending** — do not claim hiring-team approval.

---

## 6. Python implementation

**Environment:** Python 3.13 (works 3.11+), pandas 3.0.5, numpy 2.5.3, pytest 9.1 (`requirements.txt`).
Total ~2,860 lines in `analysis/`.

| Module | Role | Key functions / notes |
|---|---|---|
| `common.py` | paths, loading, parsing, cleaning | `read_raw` (all text, no NA inference), `parse_intake_datetime` (strict `%m/%d/%Y %I:%M:%S %p`), `parse_outcome_datetime` (regex, offset kept as text), `parse_age`, `age_band`, `flag_duplicates`, `build_intakes`, `build_outcomes`, `write_csv` (bools → 1/0, floats 6 dp, date-only columns `YYYY-MM-DD`), `metrics_frame`, `fmt_ddmmyyyy` (display only) |
| `matching_engine.py` | pure matching functions | `match_rank`, `_match_queue` (FIFO/LIFO via `bisect_right`), `_match_adjacent` (state machine), `match_asof` (`merge_asof`), `run_method`, `attach_times`, `sequencing_key` (midnight → 23:59:59 for ordering), `reconcile_same_day_reversed` (one-to-one, closest-first, no intervening events) |
| `audit_datasets.py` | source audit | verifies checksums (creates reference on first run); profiles; label variants; suspected duplicates; writes `data/processed/` and `outputs/audit/` (15 CSVs) |
| `match_visits.py` | method comparison + primary visits | raw vs dedup stages; 13 configurations; pairwise differences; dedup impact; ambiguity streams; builds `candidate_visits.csv` from the **chronological pass only** (`PRIMARY_LABEL = adjacent_dp_primary`); LOS percentiles; preliminary reconciliation |
| `explore_business_opportunities.py` | time series + findings evidence | monthly/annual/like-for-like, seasonality, structural-break screen, visit outcome mix, LOS by segment/cohort, census estimate (daily in-care via cumulative ±1), repeat visits, adoption returns, opportunity register |
| `sensitivity_analysis.py` | assumption testing | six scenarios; `exact_overlaps` (vectorised cummax); `owner_surrender` (interval guard); reversed-pair review; A-vs-B reconciliation; foster evidence |
| `validate_powerbi_model.py` | model foundation checks | mirrors Power Query in pandas; checks M column lists vs CSV headers, DAX column references, reference values per measure; writes `outputs/powerbi/` |
| `run_all.py` | orchestration | audit → matching → analysis → pytest (sensitivity and model validation run separately) |

**Workflow:** `python analysis/run_all.py` (~1.5 min) → `python analysis/sensitivity_analysis.py` →
`python analysis/validate_powerbi_model.py` → `python -m pytest analysis/tests -q`. Outputs are deterministic
(pipeline rerun produced byte-identical files).

**Implementation details that matter:**
* Event ordering: animal, timestamp, event ID (stable) → deterministic results.
* `match_rule` values: `chronological`; `same_day_time_reversed` (only in sensitivity / candidate file);
  `unmatched` on unmatched rows of `candidate_visits.csv`.
* `visit_id` = `V-` + intake event ID (or outcome event ID for outcome-only rows).
* Owner-surrender "previous visit" uses previous **matched** visits by intake time.
* The census estimate counts matched visits in care at end of day (`intake_date ≤ d < outcome_date`).

---

## 7. Power BI implementation

### 7.1 Files

| Item | Path | Notes |
|---|---|---|
| **Final report** | `powerbi/Austin_Animal_Center_Analytics_Final.pbix` | 32,607,642 bytes, commit `682a568` (renamed from `_Working.pbix`) |
| Original blank file | `powerbi/Austin_Animal_Center_Analytics.pbix` | 16,674 bytes, history only |
| Power Query | `powerbi/power_query/*.m` | `RepoRoot` (text parameter), FactIntakes, FactOutcomes, FactVisits, DimDate, DimAnimalType, DimIntakeType |
| Relationships | `powerbi/dax/00_Model_Relationships.md` | R1–R9 |
| Measures | `powerbi/dax/01_Core_Measures.dax` … `05_Diagnostics.dax` | DAX-query-view format (`DEFINE MEASURE … EVALUATE`) |
| Documentation | `docs/POWER_BI_DATA_MODEL.md` | full spec + Desktop steps |

### 7.2 Tables (repository spec) [Verified]

| Table | Source | Grain | Rows |
|---|---|---|---:|
| FactIntakes | `data/processed/intakes_clean.csv` minus `is_exact_duplicate` | intake event | 173,776 |
| FactOutcomes | `data/processed/outcomes_clean.csv` minus `is_exact_duplicate` | outcome event | 173,749 |
| FactVisits | `outputs/matching/candidate_visits.csv` + reasons from `unmatched_intakes.csv` / `unmatched_outcomes.csv` (`unmatched_reason`, `unmatched_reason_code`) | candidate visit, **no rows removed** | 174,978 |
| DimDate | generated: 01-10-2013 → 05-05-2025 | day | 4,235 |
| DimAnimalType | distinct values of the three facts | animal type | 5 |
| DimIntakeType | distinct non-null `intake_type` of FactIntakes + FactVisits | intake type | 6 |

M rules: UTF-8 (`Encoding = 65001`); `Table.SelectColumns(…, MissingField.Error)`; blank → null; explicit ISO
formats (`Date.FromText(t, [Format="yyyy-MM-dd", Culture="en-US"])`); flags 1/0 → logical (error otherwise); no
timezone conversion; `Table.AddKey`. DimDate flags: Is Full Calendar Year, Is Partial Extract Year, Is YoY
Comparable Year, Is Complete Extract Day (≤ 04-05-2025), Is Jan to 04-May Window, Is Oct to Dec Window.

### 7.3 Relationships (all 1:*, single direction)

R1 DimDate→FactIntakes[intake_date] (active) · R2 →FactOutcomes[outcome_date] (active) · R3 →FactVisits[intake_date]
(active) · R4 →FactVisits[outcome_date] (**inactive**, `USERELATIONSHIP`) · R5–R7 DimAnimalType → each fact ·
R8–R9 DimIntakeType → FactIntakes, FactVisits. **Not created:** Animal ID joins, fact-to-fact joins,
bidirectional or many-to-many relationships; DimIntakeType → FactOutcomes (no intake type on outcomes).

**Date roles:** a date filter = intake date for intake measures, outcome date for outcome measures, **intake
date (cohort)** for visit measures; outcome-only visit rows (blank intake date) are reachable only via R4. The
1,202 outcome-only rows fall under DimIntakeType's blank member.

### 7.4 Measures (repository DAX; expected unfiltered values) [Verified by Python equivalence]

| Measure | Value | | Measure | Value |
|---|---:|---|---|---:|
| Total Intakes | 173,776 | | Total Outcomes | 173,749 |
| Distinct Animals Intake | 156,287 | | Distinct Animals Outcome | 156,237 |
| Matched Visits | 172,547 | | Unmatched Intake / Outcome Events | 1,229 / 1,202 |
| Median / Average / P90 LOS (Days) | 6.00 / 21.03 / 55.56 | | Visits Over 30 / 90 / 365 Days | 33,304 / 7,777 / 577 |
| Same-Day Visits | 22,149 | | Visits Under 24 Hours | 32,417 |
| Share of Matched Visits Over 30 Days | 19.30% | | Open Intake Visits | 966 |
| Repeat Intake Visits | 17,489 | | Method-Dependent Visits | 76 |
| Same-Day Reversed Candidates (pairs) | 225 | | Long Stay Visits | 577 |
| Adoption / RTO / Transfer / Euthanasia / Died Outcomes (events) | 84,586 / 26,928 / 48,683 / 10,832 / 1,670 | | Provisional Live / Non-Live / Indeterminate (events) | 160,226 / 12,502 / 1,021 |

Every visit measure filters `visit_status = "Matched visit"` **inside** the measure. P90 uses `PERCENTILE.INC`
(= pandas linear interpolation).

**Report YoY measures (`DAX_Measures`, `02_Time_Intelligence.dax`):** Total Intakes / Total Outcomes Previous
Year, YoY Change, YoY Change %. Self-contained guard (prior-period start ≥ 01-10-2013 and current-period end ≤
04-05-2025), `REMOVEFILTERS ( DimDate )` + `SAMEPERIODLASTYEAR ( DimDate[Date] )`, `DIVIDE`. BLANK for 2013, 2014,
2025. Examples: intakes 2019 +16.2% (19,726 vs 16,975), 2020 −51.4%, 2024 +5.3%; outcomes 2020 −50.6%, 2024
+6.0%; Dog intakes 2020 −50.4%. Full table: `outputs/powerbi/yoy_reference.csv`. Older equivalents (`Intake Events
PY` family) also exist in the file; use one family per visual.

### 7.5 Report pages (final PBIX) [Metadata]

All pages 1920 × 1080; page order: Executive Summary, Shelter Overview, Operational Insights. No visual uses the
auto date/time hierarchy.

| Page | Visuals and titles | Fields / measures referenced |
|---|---|---|
| **Executive Summary** | background image (embedded `executive-summary-background….png`, identical to repo asset); 2 action buttons with **PageNavigation** to the two analysis pages | — |
| **Shelter Overview** | title "AUSTIN ANIMAL CENTER — Shelter Operations Overview \| 2013–2025"; 4 cards; "Intake Volume by Animal Type"; "Monthly Intake vs. Outcome Trends"; "Outcome Distribution by Category" (subtitles "October 2013 – May 2025"); slicers Animal Type, Date, Animal Intake Type | Total Intakes, Total Outcomes, Matched Visits, Median Intake-to-Outcome Days; DimDate[Date], DimDate[Month-Year Display], DimAnimalType[Animal Type], DimIntakeType[intake_type], FactOutcomes[outcome_group] |
| **Operational Insights** | title "OPERATIONAL INSIGHTS — Understanding animal outcomes, length of stay and operational patterns \| 2013–2025"; 4 cards; "Median Length of Stay by Animal Type"; "Annual Intake Volume & Year-over-Year Change" (column + line combo); note "LOS represents matched intake-to-outcome duration; shelter and foster periods cannot be separated"; slicers Date, Animal Type, Animal Intake Type | Matched Visits, Median / Average / P90 Intake-to-Outcome Days, Total Intakes, Total Intakes YoY Change %; DimDate[Date], DimDate[Year], DimAnimalType[Animal Type], DimIntakeType[intake_type] |

**[User-reported]:** slicers synced between the two analytical pages; DimDate marked as date table; Auto
date/time off; chronological year sorting; visuals and measures checked in Desktop.

**[Unresolved]:** the PBIX measures `Median / Average / P90 Intake-to-Outcome Days` are named differently from the
repository's `Median / Average / P90 LOS (Days)`; their DAX lives in the compressed model and was never read from
the repository. Expected values if equivalent: 6.00 / 21.03 / 55.56.

---

## 8. Validation and testing

### 8.1 Current results (re-run 25-11-2026 at `a5a83ef`) [Verified]

* `python analysis/validate_powerbi_model.py` → **151 PASS, 33 INFO, 0 FAIL** (previously 34 INFO; the INFO
  check reading the working-PBIX metadata is now skipped because it points to the old `_Working.pbix` filename).
* `python -m pytest analysis/tests -q` → **86 passed**: `test_matching.py` 24, `test_powerbi_model.py` 35,
  `test_pipeline_outputs.py` 8, `test_parsing.py` 7, `test_sensitivity_outputs.py` 6, `test_duplicates.py` 3,
  `test_docs_consistency.py` 3.
* Raw-file checksums unchanged.

### 8.2 What the checks cover

Raw checksums; strict parsing; duplicate classes; one-to-one and chronological matching on synthetic streams
(overlap, nesting, superseded intakes, same-day rules, determinism); output reconciliation (matched + unmatched =
events); no negative LOS; no overlapping visits; key metrics recomputed from raw files; docs quoting outputs; M
`ExpectedColumns` = CSV headers; every DAX column reference exists; reference values per measure cross-checked
against independent outputs (e.g. YoY vs `annual_event_counts.csv`, Dog/Cat vs `annual_intakes_by_animal_type.csv`,
Stray vs `annual_intakes_by_type.csv`).

### 8.3 Preliminary-figure reconciliation (`outputs/matching/preliminary_reconciliation.csv`)

All preliminary figures in `DECISION_LOG.md` §5–6 reproduced exactly except: "latest preceding intake 155,448"
(not reproducible; method rejected), FIFO/LIFO "81 changes / 47 IDs" (exact only when choices between
identical-timestamp intakes are excluded; 90 / 51 otherwise). 172,205 → 172,170 = FIFO/LIFO on raw vs
deduplicated rows (−38 pairs, +3 new); "17,525 / 17,538 rows in repeated IDs" were excess rows.

### 8.4 What was NOT independently verified

* **No DAX was executed in the Power BI engine by the assistant.** Measures were validated by equivalent pandas
  computations; Desktop checks are the candidate's.
* PBIX data-model contents (measure formulas, storage mode, Power Query source paths, date-table marking) — the
  DataModel part is compressed; a decoder could not be installed in the work environment.
* City of Austin data documentation (portal blocked by network policy) — Foster semantics inferred from data.
* Legal/policy context (DECISION_LOG §8) — research leads only.

---

## 9. Important decisions and rationale (D-001…D-020)

| ID | Decision | Why |
|---|---|---|
| D-001 | Investigate 15 opportunities; present 3 | breadth for credibility, focus for the director |
| D-002 | 3-page report | fits brief |
| D-005 | `DD-MM-YYYY` display, real date types | candidate's convention; avoids text dates |
| D-008 | Wall-clock timestamps; offset as metadata | offset only on midnight rows, wrong in winter; MonthYear agrees |
| D-009 | Exclude exact duplicates; keep conflicts; repeats are visits | distinguishes data error from real behaviour |
| D-010 | Adjacent-event matching | only one-to-one rule without overlaps; robust to duplicates; explainable |
| D-011 | Midnight outcomes = date-only | recovers genuine same-day visits (621 misses) |
| D-012 / D-018 | Reversed pass kept only as flagged candidates | no source proof; 37 ambiguous; confirmed matches must not rest on inference |
| D-013 / D-019 | LOS = intake to final recorded outcome | foster start never recorded |
| D-014 | Provisional outcome grouping | official live-release formula unverified |
| D-015 | YoY only on complete comparison periods | 2013 / 2025 partial |
| D-016 | Retain method after sensitivity | no material effect on findings |
| D-017 | Owner-surrender definitions and wording | earlier shares had the wrong denominator |
| D-020 | Exact-timestamp overlap validation; interval guard | closes date-level blind spots (0 overlaps, 0 negative intervals) |

**Model-design choices (documented in `docs/POWER_BI_DATA_MODEL.md`, not D-numbered):** role-specific DAX with one
inactive relationship instead of duplicate date tables; visits default to intake cohort; no fact-to-fact keys
(ambiguous paths); conformed DimIntakeType added for the mandatory intake-type slicer; diagnostics separated from
KPIs; YoY guard instead of showing misleading partial-year comparisons.

**Approval status:** D-008…D-020 are marked "pending candidate review" in `DECISION_LOG.md`; the candidate built
and submitted the report on this basis, but no explicit approval is recorded in the log **[Unresolved]**.

---

## 10. Limitations and unresolved questions

### 10.1 Analytical

LOS ≠ kennel time (foster unrecorded) · partial years and right-censoring of 2024–2025 cohorts · 225 reversed
candidates and 45 method-dependent animals cannot be resolved · field reunifications invisible · surrender reasons
not recorded · adoptions before 01-10-2013 invisible · "Transfer" mixes partner placement and community-cat
return · provisional live grouping ≠ official live-release rate · breed labels unreliable · cause of the 03-2020
level shift unknown · census is an estimate from matched visits.

### 10.2 Technical

PBIX formulas / storage mode unread from the repository · refresh depends on `RepoRoot` and local CSV paths
(viewing does not) · DAX not engine-executed by the assistant · validator's PBIX path is stale (§10.4).

### 10.3 Business / process

Official live-release definition and wildlife treatment (DECISION_LOG §12 Q4) · interview time allocation (does
10 minutes include the Power BI demo?) · CRM platform for the role unknown · Austin/Texas policy research not done.

### 10.4 Repository items to fix (found while preparing this kit; not changed here)

1. `README.md` §7/§11 and `docs/POWER_BI_DATA_MODEL.md` §9.1/§11.1 still name
   `powerbi/Austin_Animal_Center_Analytics_Working.pbix` and commit `af6aca4`; the file is now
   `…_Final.pbix` (`682a568`).
2. `analysis/validate_powerbi_model.py` constant `PBIX_WORKING` points to the old filename (check silently skipped).
3. `CLAUDE.md` layout section does not list `sensitivity_analysis.py`, `validate_powerbi_model.py`, `powerbi/`
   or `assets/`.

---

## 11. Current project status

| Item | Status |
|---|---|
| Audit, matching, analysis, sensitivity, model foundation | Complete; validated (§8) |
| Final PBIX | In repo (`682a568`); **submitted by email to Mr. Kuber Gupta without a repository link [User-reported]** |
| Executive Summary image | Corrected to 12.08; embedded in final PBIX [Verified] |
| Presentation website (10 slides, KPI cards/tables, no duplicate charts) | Not started |
| Policy / environmental-health research | Not started |
| 10-minute speaking script; Power BI + CRM interview kit; rehearsal | Not started |
| Stale filename references (§10.4) | Pending |

Next steps as planned by the candidate: see the DOCX (Part A and §12 slide architecture).

---

## 12. Interview defence notes

Answers are grounded in repository evidence; numbers in Appendix A.

**Data and preparation**

* *Did you use the supplied datasets?* — Yes. The raw CSVs are unchanged (checksums verified). Power Query reads
  typed derivatives produced from them by the Python pipeline (`data/processed/`, `outputs/matching/`), so cleaning
  and matching are reproducible and testable outside Power BI.
* *How did you handle duplicates?* — 36 and 26 exact duplicate excess rows excluded; near-duplicates flagged, not
  deleted; repeat intakes treated as real visits.
* *Why not convert the `-05:00` timestamps?* — The offset appears only on midnight, date-only rows and is wrong in
  winter (Austin is −06:00); MonthYear agrees with wall-clock time on every row. Converting would shift dates.

**Visit matching**

* *Why not join on Animal ID?* — Not a visit key (up to 33 visits per animal); a join multiplies rows and creates
  nonsense durations.
* *Why adjacent-event, not FIFO?* — FIFO and LIFO are one-to-one but produce overlapping or nested visits for the
  same animal; adjacent-event never does, is unaffected by duplicate removal, and is explainable in one sentence.
  It matches 35 fewer visits than LIFO (0.02%).
* *What about unmatched records?* — Kept: 1,229 intake-only (mostly still in care at extract end) and 1,202
  outcome-only (mostly intakes before 01-10-2013). They are rows in FactVisits with a status and reason, excluded
  from LOS.
* *What are the 225 pairs?* — Outcomes logged a few hours *before* a same-day intake. Plausibly one visit, but not
  provable; excluded from confirmed matches, flagged, and shown to make no material difference.

**Length of stay**

* *What exactly is LOS?* — Intake to final recorded outcome for matched visits. Not shelter occupancy: foster
  placement isn't recorded, so shelter and foster time can't be split.
* *Why 6.00 days median but 21 days average?* — Strong right skew; P90 55.56, 577 stays over a year.
* *Same-day vs zero-day?* — Same-day = same calendar date (22,149). Exact zero (439) is mostly a timestamp-precision
  artefact and is only a diagnostic.
* *Pooled vs averaged median?* — 5.12 → 12.08 is the pooled median of all visits in each period; 5.12 → 12.38 is
  the average of yearly medians. Both show the same direction; quote the statistic by name.

**Model and DAX**

* *Why three fact tables?* — Different grains: intake events, outcome events, visits. Event trends use event
  facts; LOS and visit-level shares use the visit fact.
* *Why an inactive relationship?* — Visits have two dates; intake date is the default (cohort view);
  `USERELATIONSHIP` activates outcome date when needed.
* *How does YoY handle 2013 and 2025?* — It returns BLANK when the prior period isn't fully inside the extract or
  the current period is incomplete; like-for-like windows compare 2025 (01-01→04-05) and 2013 (Oct–Dec).
* *Why filter `visit_status` inside measures?* — So KPIs can't silently include unmatched rows if a report filter
  is removed; also prevents the `BLANK() = 0` trap.
* *Does the intake-type slicer filter outcomes?* — No; outcome events carry no intake type, so DimIntakeType
  relates only to intakes and visits.

**Findings**

* *Is the dog LOS increase caused by X?* — The data shows timing, not causes. It is robust to every matching
  scenario and holds for visits without a foster subtype (4.95 → 8.94 days).
* *Does 24.46% mean owners return adopted animals?* — It means the animal's previous visit here ended in adoption.
  The reason for surrender isn't recorded; 14.89% within 30 days points to early post-adoption support.
* *Why might stray-dog RTO fall?* — Not determinable here; field returns without intake are invisible and the mix
  of dogs reaching the shelter may differ. Recommend measuring field returns alongside.
* *Why not the live-release rate?* — The official numerator, denominator and wildlife treatment weren't verified;
  the provisional grouping is labelled as such.

**Process and integrity**

* *What did AI do vs you?* — Be explicit: the assistant implemented scripts, tests and documentation under the
  candidate's direction; the candidate built and verified the PBIX in Desktop, made the design and reviewed the
  decisions. Only claim what you can explain.
* *What would you do next?* — Verify the official live-release definition; obtain foster placement dates; add
  field-return data; publish with scheduled refresh (repoint sources from local CSVs).

---

## Appendix A — Number sheet

| Quantity | Value | Source |
|---|---:|---|
| Raw rows intakes / outcomes | 173,812 / 173,775 | `outputs/audit/source_file_profile.csv` |
| Exact duplicate excess | 36 / 26 | same |
| Analytic events | 173,776 / 173,749 | same |
| Unique Animal IDs | 156,287 / 156,237 | same |
| Candidate visit rows | 174,978 | `outputs/matching/candidate_visits.csv` |
| Matched / intake-only / outcome-only | 172,547 / 1,229 / 1,202 | `matching_key_metrics.csv` |
| Reversed candidate pairs | 225 (37 ambiguous) | `same_day_reversed_candidates.csv`, sensitivity review |
| LOS P25 / P50 / P75 / P90 / P95 / P99 | 2.01 / 6.00 / 19.93 / 55.56 / 84.81 / 214.46 | `los_percentiles.csv` |
| LOS mean / max | 21.03 / 1,912.94 | same |
| Floored to zero / same-day / under 24 h | 416 / 22,149 / 32,417 | `matching_key_metrics.csv`, `los_distribution.csv` |
| Dog pooled median 2014–19 → 2023–24 | 5.12 → 12.08 | `scenario_comparison.csv` (A_excl_reversed) |
| Dog averaged annual medians | 5.12 → 12.38 | `analysis_key_metrics.csv` |
| Owner surrender after adoption / ≤30 d / ≤7 d (2016–24) | 24.46% / 14.89% / 8.96% (6,668 / 4,058 / 2,441 of 27,256) | `owner_surrender_verification.csv` |
| Stray-dog RTO 2014–19 avg → 2024 | 29.46% → 12.51% | `analysis_key_metrics.csv` |
| Intakes 2014–19 avg / 2022–24 avg | 18,216 / 11,643 | `analysis_key_metrics.csv` |
| 2020 YoY intakes / outcomes | −51.41% / −50.56% | `annual_event_counts.csv` |
| 2025 vs 2024 (01-01→04-05) intakes | 3,745 vs 3,991 (−6.16%) | `like_for_like_periods.csv` |
| DimDate days | 4,235 | `model_validation_summary.csv` |
| Model checks / tests | 151 PASS (33 INFO) / 86 passed | re-run 25-11-2026 |

## Appendix B — File index

* Root: `README.md`, `DECISION_LOG.md` (decisions D-001…D-020; §12 open questions), `CHANGELOG.md`, `CLAUDE.md`
  (assistant rules), `requirements.txt`, this file, the DOCX handover.
* `analysis/` — pipeline modules (§6) and `tests/`.
* `data/raw/` (read-only), `data/processed/`, `data/reference/source_checksums.csv`.
* `docs/` — `DATA_AUDIT_REPORT.md`, `DATA_DICTIONARY.md`, `DATA_QUALITY_ISSUES.md`,
  `VISIT_MATCHING_METHODOLOGY.md` (§11 sensitivity), `BUSINESS_OPPORTUNITY_REGISTER.md`, `POWER_BI_DATA_MODEL.md`.
* `outputs/audit/` (15), `outputs/matching/` (12), `outputs/analysis/` (35), `outputs/sensitivity/` (9),
  `outputs/powerbi/` (2).
* `powerbi/` — final and blank PBIX, `power_query/`, `dax/`, `screenshots/` (empty).
* `assets/images/executive-summary-background.png` (1672 × 941).
* `references/design/Vetology_Week6_Presentation.html` — design inspiration only (different subject matter).
* `website/`, `presentation/` — empty placeholders.

## Appendix C — Instructions for the next assistant

1. Read `CLAUDE.md`, this file, `DECISION_LOG.md` and the DOCX before acting. `CLAUDE.md` rules are binding:
   raw data read-only; no silent definition changes (new D-entry + CHANGELOG); only quote numbers present in
   `outputs/`; run tests before committing.
2. Quote findings with their definitions and statistic names (pooled vs averaged; shares of owner surrenders vs
   shares of returns; matched visits as denominator).
3. Do not modify the submitted PBIX. Distinguish repository-verified facts from Desktop-only facts.
4. Never present the provisional live grouping as the official live-release rate; never claim causes.
5. For the website: exactly 10 slides, KPI cards/tables/diagrams (no duplicate Power BI charts), keyboard
   navigation, full-screen friendly; inspect the design reference first (D-004).
6. For policy research: primary sources, exact sections, effective dates, binding vs guidance (D-006).
7. Resolve §10.4 when convenient, with a changelog entry.
