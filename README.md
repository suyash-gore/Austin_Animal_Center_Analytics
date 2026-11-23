# Austin Animal Center Analytics

A data analytics and Power BI case study using the public Austin Animal Center intake and outcome datasets. The goal is to help shelter leadership understand incoming animal demand, outcomes, length of stay, and potential operational actions.

## Project status

**Current stage:** Repository setup and data-audit preparation.

The source datasets and initial Power BI file have been placed in the project structure. Data validation, visit-level intake/outcome matching, business analysis, dashboard development, and the final director-facing recommendations are still subject to audit and verification.

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
