# Changelog

All notable project changes should be recorded here in reverse chronological order. Keep entries concise and describe what changed, why it changed, and any material impact on results.

This project has not yet completed its formal source-data audit. No preliminary planning figures should be recorded as validated results.

## [Unreleased]

### 24-11-2026 — Executive Summary dog LOS figure reconciled (12.07 → 12.08)
#### Fixed
- `assets/images/executive-summary-background.png`: "5.12 → 12.07 days" corrected to "5.12 → 12.08 days". Only the
  final digit was replaced (33 × 50 px region; 1,593 pixels; all other pixels identical; 1672 × 941 RGB, lossless
  PNG). Evidence: primary dataset (D-018), Dog matched visits, pooled median of `los_days` by intake year —
  2014–2019: 61,626 visits, 5.117361 → 5.12; 2023–2024: 10,134 visits, 12.078472 → 12.08
  (`outputs/sensitivity/scenario_comparison.csv`, `A_excl_reversed`). 12.07 (12.067014) included 10 dog
  time-reversed candidate visits with LOS 0, i.e. different cohort membership, not a calculation or rounding change.
- `README.md` note updated; `DECISION_LOG.md` D-017 annotated with the primary-basis values (history preserved).
#### Known limitations
- The PBIX still embeds the previous image; replace the Executive Summary background in Power BI Desktop.

### 24-11-2026 — Repository finalisation: README, assets and documentation review
#### Changed
- Moved `Austin Animal Center Executive Findings.png` (repository root, added in `af6aca4`) to
  `assets/images/executive-summary-background.png` with `git mv` (byte-identical; 1672 × 941 PNG, identical to the
  background embedded in the working PBIX).
- `README.md` rewritten from the repository's contents: objective, sources and period (extract ends 05-05-2025;
  2013 and 2025 partial), cleaning, visit matching, model, the three report pages, KPIs, findings with
  definitions and caveats, structure, reproduction and validation.
- `docs/POWER_BI_DATA_MODEL.md` §9.1 and §11.1 updated to the report as of `af6aca4` (pages, measures referenced,
  auto date hierarchy no longer used; date-table marking still to verify in Desktop).
- `docs/BUSINESS_OPPORTUNITY_REGISTER.md`: Finding 1 cohort-completeness figures corrected to the primary dataset
  (0.26% / 2.37%; previously 0.20% / 2.24% from the pre-D-018 basis).
- `outputs/powerbi/model_validation_summary.csv` regenerated (151 checks pass; auto-date-hierarchy check now False).
#### Validated
- `python analysis/validate_powerbi_model.py`: 151 PASS, 34 INFO; `python -m pytest analysis/tests -q`: 86 passed.
#### Known limitations
- Executive Summary image shows the dog pooled median as 12.07 days; the primary dataset gives 12.08 (pre-D-018
  value; 0.01 day). PBIX and image not modified.

### 24-11-2026 — Report YoY measures
#### Added
- `powerbi/dax/02_Time_Intelligence.dax`: `DAX_Measures[Total Intakes Previous Year]`, `[Total Intakes YoY Change]`,
  `[Total Intakes YoY Change %]` and the three `Total Outcomes …` equivalents. Use `[Total Intakes]` /
  `[Total Outcomes]`, `SAMEPERIODLASTYEAR ( DimDate[Date] )` with `REMOVEFILTERS ( DimDate )`, the partial-year guard
  (BLANK for 2013, 2014, 2025) and `DIVIDE`.
- `outputs/powerbi/yoy_reference.csv` (annual expected values: All, Dog, Cat, Stray scopes) and 14
  time-intelligence checks in `analysis/validate_powerbi_model.py` (151 pass), cross-checked against
  `outputs/analysis/annual_event_counts.csv`, `annual_intakes_by_animal_type.csv`, `annual_intakes_by_type.csv`.
- Tests for the YoY measures and reference values.
#### Changed
- `docs/POWER_BI_DATA_MODEL.md` §9.1 (behaviour, expected annual output, visual configuration), §10.
  Existing base measures, `Intake/Outcome Events PY` measures, relationships and the PBIX are unchanged.
#### Known limitations
- DAX not executed in Power BI. The working PBIX visuals use the auto date/time hierarchy on `DimDate[Date]`,
  indicating DimDate is not marked as a date table; mark it and use `DimDate[Year]` before relying on YoY values.

### 24-11-2026 — Short-stay measure cleanup (416 vs 439 reconciliation)
#### Added
- `Visits Under 24 Hours` (32,417) in `powerbi/dax/01_Core_Measures.dax`; `Same-Day Visits` (22,149, same calendar
  date) confirmed and documented as the business short-stay KPI.
- `powerbi/dax/05_Diagnostics.dax`: `Zero-Duration Visits (Diagnostic)` (439), `LOS Floored to Zero (Diagnostic)`
  (416), `Identical Timestamp Visits (Diagnostic)` (23); matched visits only, strict `==` so blanks never match.
- Validator cross-checks of all five against matching/sensitivity outputs (137 checks pass) and tests.
#### Changed
- `docs/POWER_BI_DATA_MODEL.md` §7.1 (definitions, blank-handling trap = 2,870), §10, §11.1 (PBIX measures to
  rename/retire). No change to source CSVs, matching outputs, methodology or the PBIX.
#### Known limitations
- The working PBIX measure expressions (`Zero-Day Visits`, `Same-Day Visit Flag Count`) could not be read; the
  rename/retire steps must be done in Power BI Desktop.

### 23-11-2026 — Conformed intake type dimension
#### Added
- `powerbi/power_query/DimIntakeType.m`: distinct non-null `intake_type` of FactIntakes and FactVisits (6 members),
  with sort order and notes; relationships R8 `DimIntakeType[intake_type]` → `FactIntakes[intake_type]` and R9 →
  `FactVisits[intake_type]` (one-to-many, single direction). Not related to FactOutcomes.
- Validation: identical domain in both facts; no FactIntakes blanks; FactVisits blank only on the 1,202
  outcome-only rows (retained under the blank member); no rows excluded; per-type counts equal (130 checks pass;
  71 tests).
#### Changed
- `powerbi/dax/00_Model_Relationships.md`, `docs/POWER_BI_DATA_MODEL.md` (diagram, tables, filter propagation,
  implementation steps). No change to facts, DAX measures, audit outputs or the PBIX.

### 23-11-2026 — Power BI Stage 1: data model, Power Query and DAX foundation
#### Added
- `powerbi/power_query/`: `RepoRoot.m` (path parameter), `FactIntakes.m`, `FactOutcomes.m` (exact duplicates
  excluded), `FactVisits.m` (all 174,978 rows retained; unmatched reasons and reason codes joined), `DimDate.m`
  (01-10-2013 to 05-05-2025 with partial-year and like-for-like flags), `DimAnimalType.m`.
- `powerbi/dax/00_Model_Relationships.md` (7 single-direction relationships; inactive visit outcome-date role)
  and measure files `01_Core_Measures.dax` … `04_Outcome_Analysis.dax` (core, LOS, guarded time intelligence,
  like-for-like windows, visit operations, provisional outcome grouping).
- `analysis/validate_powerbi_model.py` → `outputs/powerbi/model_validation_summary.csv` (121 checks pass,
  32 reference values); `analysis/tests/test_powerbi_model.py` (70 tests total).
- `docs/POWER_BI_DATA_MODEL.md` (grains, relationships, date roles, LOS and provisional-outcome caveats,
  partial-year rules, validation targets, Desktop implementation steps).
#### Changed
- README project status. No change to raw data, audit outputs, matching methodology or audit metrics.
#### Known limitations
- The PBIX is not modified: queries, relationships and measures must be loaded manually in Power BI Desktop.
- Measures were validated by an equivalent pandas computation, not executed in the Power BI engine.

### 23-11-2026 — Matching edge-case validation
#### Changed
- **Primary dataset (D-018):** 225 same-day time-reversed pairs excluded from matched visits and kept as
  flagged candidates (`outputs/matching/same_day_reversed_candidates.csv`; `same_day_reversed_candidate`,
  `candidate_partner_event_id` in `candidate_visits.csv`). Matched 172,772 → 172,547; unmatched intakes
  1,004 → 1,229; outcomes 977 → 1,202; LOS P90 55.34 → 55.56. Regenerated `outputs/matching/` and
  `outputs/analysis/` files that depend on matched visits; method comparison, reconciliation and audit
  outputs are byte-identical.
- **Foster semantics (D-019):** LOS described as intake to final recorded outcome; "LOS includes foster
  time" withdrawn; Finding 1 reworded.
- `owner_surrender()` requires non-negative adoption-to-surrender intervals (0 records affected).
- `exact_overlaps()` added: timestamp-level intervals with date-only handling (0 overlaps; none missed).
#### Added
- `outputs/sensitivity/`: `scenario_a_vs_b_differences.csv`, `nonoffset_midnight_outcomes_a_vs_b.csv`,
  `exact_overlap_check.csv`, `foster_subtype_evidence.csv`.
- Tests for the primary-dataset exclusion, exact overlaps, interval guard and A/B equivalence (51 total).

### 23-11-2026 — Visit-matching and business-finding sensitivities
#### Added
- `analysis/sensitivity_analysis.py` → `outputs/sensitivity/`: record-level review of the 225
  same-day time-reversed matches; midnight-outcome split (3,583 offset / 204 non-offset analytic events);
  six-scenario comparison (date-only rule × reversed pass); owner-surrender and dog-LOS verification.
- `analysis/tests/test_sensitivity_outputs.py` (48 tests total).
#### Changed
- Owner-surrender finding reworded with explicit windows and denominators (D-017); "recent adoption"
  removed. Dog-LOS and stray-RTO baselines documented as averages of annual values, pooled values added.
- Methodology §11, audit report §7, opportunity register, DECISION_LOG D-016/D-017.
#### Validated
- No scenario changes any candidate finding by more than 0.05 pp / 0.04 days; recommended method
  unchanged. Existing outputs in `outputs/audit|matching|analysis` not regenerated or modified.

### 23-11-2026 — Audit reports and business opportunity assessment
#### Added
- `docs/DATA_AUDIT_REPORT.md`, `docs/DATA_DICTIONARY.md`, `docs/VISIT_MATCHING_METHODOLOGY.md`,
  `docs/DATA_QUALITY_ISSUES.md` (31 issues), `docs/BUSINESS_OPPORTUNITY_REGISTER.md` (15 opportunities
  scored; top eight; three candidate director findings).
- `outputs/analysis/los_by_foster_subtype.csv` so the foster LOS caveat is reproducible.
- `analysis/tests/test_docs_consistency.py`: headline figures in docs must match outputs (44 tests total).
#### Changed
- `README.md`: project status and reproduction instructions.
#### Known limitations
- Live-release definition unverified (§12 Q4); LOS includes foster time; ambiguous/superseded records
  cannot be resolved from the extract; cause of the 03-2020 break unknown. See `docs/DATA_QUALITY_ISSUES.md`.

### 23-11-2026 — Validated data audit and matching outputs
#### Added
- `data/processed/intakes_clean.csv`, `data/processed/outcomes_clean.csv` (one row per source row,
  typed fields, event IDs, quality flags; booleans 1/0).
- `outputs/audit/` (15 files): file/column profiles, categorical distributions, label variants,
  duplicates, same-ID/timestamp conflicts, suspected duplicate events, date and age exceptions.
- `outputs/matching/` (11 files): candidate visit table (method `adjacent_dp`), unmatched intakes and
  outcomes with reasons, ambiguous event streams, method comparison, pairwise differences,
  deduplication impact, LOS percentiles/distribution, preliminary reconciliation, key metrics.
- `outputs/analysis/` (34 files): monthly/annual/like-for-like time series, seasonality, structural-break
  screen, visit-level outcome mix, LOS by segment and cohort, long stays, census estimate, repeat visits,
  adoption returns, breed and condition profiles, scored opportunity register.
#### Validated
- Outputs regenerated twice from the raw files with byte-identical results; 41/41 tests pass;
  raw checksums unchanged. Matched visits 172,772; unmatched intakes 1,004; unmatched outcomes 977;
  0 reused intakes, 0 negative LOS, 0 overlapping visits, 0 animal-type mismatches.

### 23-11-2026 — Reproducible source audit and visit-matching framework
#### Added
- `analysis/common.py` (loading, parsing, cleaning, duplicate flags), `analysis/matching_engine.py`
  (rank, FIFO, LIFO, adjacent-event and as-of matching; date-precision and same-day rules),
  `analysis/audit_datasets.py`, `analysis/match_visits.py`, `analysis/explore_business_opportunities.py`,
  `analysis/run_all.py`.
- pytest suite under `analysis/tests/` (parsing, duplicates, one-to-one/chronological matching,
  unmatched handling, same-day visits, multiple intakes, raw-data checksums, reproducibility).
- `CLAUDE.md` project instructions; `requirements.txt`; `data/reference/source_checksums.csv`.
#### Changed
- `DECISION_LOG.md` §14: decisions D-008 to D-015 (timestamp interpretation, duplicates, visit rule,
  date-precision rule, same-day rule, LOS definition, provisional outcome grouping, partial years).
  Affects matching, LOS and denominators; supersedes preliminary §6.3 LOS figures.
#### Validated
- Source row counts, unique IDs, duplicate counts and preliminary matching runs reproduced from the raw
  files (see `outputs/matching/preliminary_reconciliation.csv` once generated).

### Initial setup
#### Added
- Established the initial project directory structure for analysis, data, documentation, outputs, Power BI, references, and the presentation website.
- Added the project decision log to the repository root.
- Added repository setup documentation and ignore rules.
- Added placeholders to preserve planned empty directories in Git.

### Planned
- Source-data audit and data dictionary.
- Intake/outcome visit-matching methodology and validation tests.
- Business opportunity register and evidence-backed findings.
- Reproducible analysis outputs.
- Power BI report and supporting presentation website.

---

## Changelog conventions

Use these categories where applicable:

- **Added** — new files, features, analyses, or documentation.
- **Changed** — changes to existing logic, definitions, visuals, or methodology.
- **Fixed** — corrections to errors or data-quality issues.
- **Removed** — deleted files, fields, analyses, or features.
- **Validated** — results independently reproduced or checked.
- **Known limitations** — unresolved issues that affect interpretation.

For analytical changes, state whether the change affects row counts, matching, denominators, KPI definitions, or previously reported results. Link to the relevant methodology or decision-log entry where possible.
