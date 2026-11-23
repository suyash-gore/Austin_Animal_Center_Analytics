# Changelog

All notable project changes should be recorded here in reverse chronological order. Keep entries concise and describe what changed, why it changed, and any material impact on results.

This project has not yet completed its formal source-data audit. No preliminary planning figures should be recorded as validated results.

## [Unreleased]

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
