# Austin Animal Center Analytics

A data analytics and Power BI case study using the public Austin Animal Center intake and outcome datasets. The goal is to help shelter leadership understand incoming animal demand, outcomes, length of stay, and potential operational actions.

## Project status

**Current stage:** Audit and visit-matching validation complete (merged). Power BI Stage 1 — data model,
Power Query and DAX foundation — is written and validated as source files in `powerbi/power_query/` and
`powerbi/dax/` (see `docs/POWER_BI_DATA_MODEL.md`). These must be loaded into Power BI Desktop manually;
the PBIX has not been modified and no visuals have been built yet.

Key documents: `docs/DATA_AUDIT_REPORT.md`, `docs/VISIT_MATCHING_METHODOLOGY.md`,
`docs/DATA_QUALITY_ISSUES.md`, `docs/BUSINESS_OPPORTUNITY_REGISTER.md`, `docs/DATA_DICTIONARY.md`,
`docs/POWER_BI_DATA_MODEL.md`.

Do not treat preliminary figures or hypotheses from planning discussions as final findings. Final metrics must be reproduced from the source files and documented methodology.

## Project structure

```text
Austin_Animal_Center_Analytics/
├── DECISION_LOG.md
├── README.md
├── CHANGELOG.md
├── .gitignore
├── analysis/
│   └── tests/
├── data/
│   ├── raw/          # Original source CSV files; preserve unchanged
│   ├── processed/    # Validated and transformed datasets
│   └── reference/   # Supporting reference data
├── docs/             # Audit reports, data dictionary, methodology, findings
├── outputs/
│   ├── analysis/
│   ├── audit/
│   └── matching/
├── powerbi/
│   ├── Austin_Animal_Center_Analytics.pbix
│   ├── dax/
│   └── screenshots/
├── presentation/     # Presentation assets and supporting material
├── references/
│   └── design/       # Visual/design references
└── website/
    ├── assets/
    ├── css/
    └── js/
```

## Source datasets

The project uses the Austin Animal Center public datasets:

- **Intakes:** https://data.austintexas.gov/api/views/wter-evkm/rows.csv?accessType=DOWNLOAD
- **Outcomes:** https://data.austintexas.gov/api/views/9t4d-g238/rows.csv?accessType=DOWNLOAD

Keep the original downloaded files in `data/raw/` unchanged. Perform cleaning and transformation on copies, and document every material transformation.

## Analytical scope

The planned work includes:

1. Audit source structure, data types, missing values, duplicates, and date fields.
2. Develop and validate a visit-level relationship between intake and outcome events.
3. Document matching assumptions, ambiguous records, unmatched records, and limitations.
4. Explore operational questions such as intake demand, outcome mix, length of stay, long-stay cases, and repeat visits.
5. Select a small number of evidence-backed findings and actionable recommendations for shelter leadership.
6. Build a concise Power BI report and a supporting presentation website.

## Analytical integrity rules

- Distinguish event-level counts from visit-level counts.
- Do not treat `Animal ID` alone as a unique visit key.
- Do not describe intake/outcome event shares as conversion rates.
- Do not silently discard unmatched records, long stays, or ambiguous matches.
- Keep source facts, analytical interpretations, and recommendations clearly distinguished.
- Document assumptions, exclusions, and known limitations.
- Apply `DD-MM-YYYY` as the display format for dates while retaining genuine date/date-time data types.
- Reproduce all reported metrics from the documented scripts and source data before presenting them as final.

## Reproducing the audit

Requires Python 3.11+ with the packages in `requirements.txt`.

```bash
pip install -r requirements.txt
python analysis/run_all.py
```

`run_all.py` verifies the raw-file checksums, runs `audit_datasets.py` → `match_visits.py` →
`explore_business_opportunities.py` (about 1.5 minutes) and then the pytest suite. Each script can also be
run on its own, in that order. Outputs are deterministic.

| Output | Contents |
|---|---|
| `data/processed/` | Cleaned intake and outcome event tables (one row per source row, flags, event IDs) |
| `outputs/audit/` | Profiles, distributions and exception records |
| `outputs/matching/` | Candidate visit table, unmatched/ambiguous records, method comparison, LOS |
| `outputs/analysis/` | Time series, visit-level evidence, opportunity register |
| `outputs/powerbi/` | Power BI model validation summary (`python analysis/validate_powerbi_model.py`) |

## Tools

The project is expected to use Python for audit and analysis, Power BI for the dashboard, Git/GitHub for version control, and a web-based presentation experience for communicating the findings.

## Getting started

1. Review `DECISION_LOG.md` for project decisions, constraints, and outstanding questions.
2. Keep the original CSVs in `data/raw/`.
3. Complete the source-data audit before building analytical conclusions.
4. Store audit documentation in `docs/` and reproducible scripts/tests in `analysis/`.
5. Keep generated outputs in the relevant `outputs/` subfolders.
6. Record meaningful project changes in `CHANGELOG.md`.

## Data and repository handling

This repository should initially be **private** while file sizes, dataset terms, and the intended sharing scope are checked. Do not add credentials, API keys, personal access tokens, local environment files, or unrelated private material.

Check the size of each CSV and the PBIX before the first commit. GitHub blocks ordinary Git files larger than 100 MB. If a required artifact exceeds that limit, decide whether to use Git LFS or keep the large artifact outside the repository and document how to obtain it.

## References

- Austin Animal Center data portal: https://data.austintexas.gov/
- Austin Animal Services: https://www.austintexas.gov/department/animal-services
