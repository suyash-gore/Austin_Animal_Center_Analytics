# CLAUDE.md — Austin Animal Center Analytics

Project instructions for Claude Code. Read `DECISION_LOG.md` before changing data preparation,
visit matching, KPI definitions, dashboard scope or presentation claims.

## Non-negotiable rules
- **Preserve source data.** `data/raw/*.csv` are read-only. Their SHA-256 values are recorded in
  `data/reference/source_checksums.csv`; `analysis/audit_datasets.py` and the test suite fail if they change.
  All cleaning, deduplication and matching happen on derived data (`data/processed/`, `outputs/`).
- **Never silently change analytical definitions** (visit rule, LOS, outcome grouping, denominators,
  exclusions). A change needs a new `DECISION_LOG.md` entry (D-0xx) with rationale and impact, and a
  `CHANGELOG.md` entry. Mark superseded decisions as superseded; do not delete them.
- **Preliminary figures are not results.** Numbers in `DECISION_LOG.md` §5–§6 are leads. Only figures
  produced by the scripts and present in `outputs/` may be reported, and docs must agree with outputs.
- **Document assumptions and limitations** next to every metric (docs/DATA_QUALITY_ISSUES.md,
  docs/VISIT_MATCHING_METHODOLOGY.md).
- **Reproducible Python only.** No notebook-only or hand-edited numbers. Regenerate everything with
  `python analysis/run_all.py`.
- **Run tests before committing:** `python -m pytest analysis/tests -q` (integration tests need the
  pipeline outputs). Review the diff, confirm raw data unchanged, no credentials or unrelated files.
- **Update `CHANGELOG.md`** with every implementation change and `DECISION_LOG.md` whenever a material
  analytical decision is made or changed.

## Analytical conventions (see DECISION_LOG.md D-008 onward)
- `Animal ID` is not a visit key. Visits come from `outputs/matching/candidate_visits.csv`
  (primary dataset: `adjacent_dp` chronological pass, D-010/D-011/D-018; the 225 same-day time-reversed
  pairs are flagged candidates, not matched visits).
- LOS = intake to final recorded outcome; not kennel time (foster placement is unrecorded, D-019).
- Event counts (intake rows / outcome rows) and visit-level rates are separate; never divide one by the other
  or call event shares "conversion rates".
- Timestamps are source-local wall-clock, timezone-naive. Do not convert using the outcome `-05:00` offset.
- Keep dates as date/datetime types; display as `DD-MM-YYYY` only in reports.
- 2013 (from 01-10) and 2025 (to 05-05) are partial years: use like-for-like windows.
- "Live outcome" in the derived data is a provisional grouping, not the City of Austin live-release rate.
- No causal claims from descriptive trends. Do not discard long stays or unmatched records.
- Do not modify `powerbi/*.pbix`; do not build the dashboard/website until the audit is approved.

## Layout
- `analysis/common.py` loading/parsing/cleaning · `analysis/matching_engine.py` pure matching functions
- `analysis/audit_datasets.py` → `outputs/audit/`, `data/processed/`
- `analysis/match_visits.py` → `outputs/matching/`
- `analysis/explore_business_opportunities.py` → `outputs/analysis/`
- `analysis/tests/` pytest suite · `docs/` human-readable reports
