# Changelog

All notable project changes should be recorded here in reverse chronological order. Keep entries concise and describe what changed, why it changed, and any material impact on results.

This project has not yet completed its formal source-data audit. No preliminary planning figures should be recorded as validated results.

## [Unreleased]

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
