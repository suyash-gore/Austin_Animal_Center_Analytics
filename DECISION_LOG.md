# Project Decision Log & Analytical Discovery Record

**Project:** Austin Animal Center --- Power BI & CRM Interview Exercise\
**Candidate:** Suyash Gore\
**Prepared:** 23-11-2026\
**Status:** Living project record --- update as decisions are validated\
**Purpose:** Preserve assignment requirements, project decisions,
preliminary audit observations, contextual research, assumptions, and
unresolved questions so they can be carried into later development and
interview preparation.

------------------------------------------------------------------------

## 1. Project objective

Build a defensible, executive-oriented Power BI report using Austin
Animal Center intake and outcome data, supported by a single interactive
presentation website.

The project should demonstrate more than visualisation skills. It should
show the ability to: - Understand an operational/business context. -
Profile and validate real-world data. - Identify meaningful business
opportunities. - Build a sound analytical data model and measures. -
Translate findings into management actions. - Explain technical
decisions and limitations confidently.

**Guiding principle:** analytical correctness, traceability, and
business usefulness take priority over decorative complexity or
impressive-looking but unsupported numbers.

------------------------------------------------------------------------

## 2. Hiring-team assignment --- source requirements

The hiring-team email describes the scenario as:

> You are the analyst for an animal shelter. The director wants to know
> how animals come in, what happens to them, and where to act.

### Required deliverable

-   One Power BI report (`.pbix`).
-   2--3 report pages.
-   Both supplied CSV datasets must be used.

### Mandatory requirements

1.  A data model linking intakes to outcomes, with a date table.
2.  Length of stay per visit, implemented as a measure.
3.  A trend over time, including a year-over-year comparison.
4.  Slicers for animal type, intake type, and date.
5.  Three findings the director should act on.

### Submission and interview dates stated in the email

-   PBIX due: Wednesday, 25-11-2026.
-   Interview availability requested: Thursday, 26-11-2026, between 5:00
    and 7:00 pm IST.
-   Interview duration: 45--50 minutes.

**Scope guardrail:** the three actionable findings and 2--3 page report
are explicit requirements. Additional analysis must support these
requirements rather than turn the report into an oversized presentation.

------------------------------------------------------------------------

## 3. Strategic decisions

### D-001 --- Investigate broadly, present selectively

**Decision:** Investigate approximately 12--15 potential analytical
opportunities. Rank them, identify the strongest eight internally, and
select the three most compelling, evidence-backed findings for the
director.

**Why:** Broad discovery demonstrates initiative; selective presentation
respects the short-report brief and gives the director a focused story.

**Presentation rule:** impress the director with the first three
findings. Do not create 8--15 dashboard pages.

### D-002 --- Three-page Power BI report

**Decision:** Use a concise three-page report, subject to the data
supporting the proposed structure.

1.  **Executive Overview:** key KPIs, high-level intake/outcome trends,
    and the three headline insights.
2.  **Intake & Outcome Analysis:** intake sources/types, outcomes, time
    trends, year-over-year comparison, length of stay, and required
    slicers.
3.  **Director's Action Centre:** three findings, supporting evidence,
    operational implications, and recommended actions.

**Why:** Fits the hiring brief while demonstrating analytical depth.

### D-003 --- One unified website experience

**Decision:** The website itself will function as the presentation and
interactive experience around the Power BI report. It is not a separate
slide deck with a dashboard attached.

Planned capabilities, subject to technical feasibility: - Executive
landing/opening screen. - Navigation between the three report/story
sections. - Embedded Power BI report or an appropriate report-viewing
approach. - Contextual pop-ups explaining what a visual says and why it
matters. - Recommendation/implication pop-ups. - Presenter Mode with
discreet speaker notes for the candidate. - Audience-facing exploration
mode. - Link to the GitHub repository.

**Important limitation:** website interactions must complement, not
falsely claim to reproduce, native Power BI interactions. Embedding,
permissions, and hosting options must be verified before implementation.

### D-004 --- Visual design reference

**Decision:** Use `Vetology_Week6_Presentation.html` only as a
visual/design reference. Do not reuse its radiology presentation content
or slide narrative.

Design traits to consider retaining: - Light "Mist" blue/white
palette. - Optional Warm and Slate themes if useful. - Glass-like
translucent panels. - Soft gradients and subtle depth. - Rounded cards,
restrained shadows, clean typography. - Smooth transitions and clear
navigation. - Supporting text at least 14 px where practical.

**Why:** The candidate liked the visual language of the prior
presentation. The new site must be redesigned for animal-shelter
analytics and executive storytelling.

### D-005 --- Number and date conventions

**Decision:** - Director-facing and US-facing outputs use US number
conventions: `1,000,000`, `$1.2M`, USD. - All displayed dates use
`DD-MM-YYYY`, as explicitly requested by the candidate. - Personal study
notes should include Indian-numbering equivalents in brackets when
useful. Example: `1M (10,00,000; 10 lakh)`.

**Important:** keep dates as actual date values in the data model; apply
`DD-MM-YYYY` as the display format. Do not convert date fields to text
merely for display.

### D-006 --- Separate evidence, policy context, and interpretation

**Decision:** Maintain three distinct layers in the analysis and
presentation: 1. Dataset evidence --- what the supplied records show. 2.
Local policy/operating context --- what official Austin/ Texas sources
establish. 3. Analytical interpretation --- what the shelter director
could consider doing.

**Why:** Avoid presenting an external policy requirement as if it were a
dataset finding, or claiming causation from a simple trend.

### D-007 --- No premature dashboard build

**Decision:** Complete and review the analytical audit, matching
methodology, and opportunity ranking before finalising DAX and dashboard
design.

**Why:** Length-of-stay and intake-to-outcome analysis depend on
defensible visit matching.

------------------------------------------------------------------------

## 4. Source files received

### Data

1.  `Austin_Animal_Center_Intakes__10_01_2013_to_05_05_2025_.csv`
2.  `Austin_Animal_Center_Outcomes__10_01_2013_to_05_05_2025_.csv`

### Power BI

-   `untitled.pbix` --- supplied blank Power BI file.

### Website design reference

-   `Vetology_Week6_Presentation.html` --- inspiration only; content
    belongs to a different presentation.

### Public source URLs from hiring email

-   Intakes:
    https://data.austintexas.gov/api/views/wter-evkm/rows.csv?accessType=DOWNLOAD
-   Outcomes:
    https://data.austintexas.gov/api/views/9t4d-g238/rows.csv?accessType=DOWNLOAD

------------------------------------------------------------------------

## 5. Preliminary data inventory

The following figures were reported during the initial inspection of the
uploaded files. Claude Code must independently reproduce them and
investigate any discrepancy.

  Attribute                           Intakes           Outcomes
  ------------------------- ----------------- ------------------
  Rows initially observed             173,812            173,775
  Columns                                  12                 12
  Animal ID                           Present            Present
  Event timestamp                  `DateTime`         `DateTime`
  Animal type                         Present            Present
  Age field                   Age upon Intake   Age upon Outcome
  Breed                               Present            Present
  Main classification             Intake Type       Outcome Type

Initial unique/repeated-ID profile: - Unique Animal IDs in intakes:
156,287. - Unique Animal IDs in outcomes: 156,237. - Intake rows
reported as belonging to repeated Animal IDs: 17,525. - Outcome rows
reported as belonging to repeated Animal IDs: 17,538. - Animal IDs
appearing multiple times: 13,487 in intakes and 13,507 in outcomes.

These counts are profile observations, not visit counts. Confirm
definitions and reproduce from raw data.

------------------------------------------------------------------------

## 6. Preliminary audit observations --- preserve, then independently verify

**Critical status:** These are preliminary findings from an initial
audit, not final approved business metrics. Different matching runs and
duplicate-handling stages produced slightly different totals. Do not
silently combine them or select whichever looks best. Reproduce every
stage and reconcile the differences.

### 6.1 Initial visit-matching experiments

The first audit reported these exploratory results:

  ------------------------------------------------------------------------
  Method / run                     Candidate matches Observation
  --------------------- ---------------------------- ---------------------
  Same Animal ID +                           172,850 781 candidate pairs
  chronological                                      had outcome
  sequence                                           timestamps earlier
                                                     than intake
                                                     timestamps

  Latest preceding                           155,448 Can assign multiple
  intake, without                                    outcomes to one
  one-to-one                                         intake; unsuitable as
  restriction                                        a final visit mapping

  Chronological                              172,205 No negative durations
  one-to-one matching                                in that run; 1,570
                                                     unmatched outcomes
                                                     and 1,607 unmatched
                                                     intakes were reported
  ------------------------------------------------------------------------

Further observations from that run: - 96 instances were flagged where
multiple unmatched intakes existed before an outcome and needed
review. - Preliminary median length of stay was approximately 6.02
days. - The source outcome timestamps may include timezone offsets.
Initial handling preserved the source-local wall-clock date/time rather
than converting and potentially shifting dates.

### 6.2 Matching after exact-duplicate removal

A subsequent audit, after removing exact duplicate rows from analytical
copies, reported:

  -----------------------------------------------------------------------
  Metric                                               Preliminary result
  ------------------------------ ----------------------------------------
  Candidate matched visits                                        172,170

  Unmatched outcomes                                                1,579

  Unmatched intakes                                                 1,606

  Median length of stay                                         6.02 days

  Multiple-open-intake instances                                       60

  FIFO/LIFO assignment                81 assignments across 47 Animal IDs
  differences                    
  -----------------------------------------------------------------------

Additional observations: - Zero negative-duration records in the
candidate matched set. - Zero animal-type mismatches in the candidate
matched set. - FIFO versus LIFO changed 81 visit assignments across 47
Animal IDs.

**Reconciliation required:** The earlier 172,205 matches and later
172,170 matches are not interchangeable. The later run reportedly
followed exact-duplicate removal. Claude Code must reproduce the raw and
deduplicated stages and explain the 35-record difference, as well as the
changes in unmatched counts and multiple-open-intake counts.

### 6.3 Preliminary length-of-stay distribution

Reported from the later candidate matched set:

  Percentile          Days
  --------------- --------
  50th (median)       6.02
  75th               19.99
  90th               55.81
  95th               84.90
  99th              215.63

-   578 candidate visits reportedly exceeded 365 days.
-   These long-duration cases require validation; do not automatically
    exclude them as outliers.
-   Length of stay must be defined at the visit level and implemented as
    a Power BI measure for the required report.
-   Decide explicitly how same-day intake/outcome visits, unmatched
    visits, and open stays are treated.

### 6.4 Preliminary data-quality observations

  Issue                           Intakes   Outcomes
  ----------------------------- --------- ----------
  Missing animal names             49,991     49,784
  Missing outcome type                ---         46
  Missing outcome subtype             ---     94,115
  Missing sex                           1          1
  Missing age upon outcome            ---          9
  Exact duplicate excess rows          36         26

Other reported observations: - 33 outcome records had dates of birth
later than their recorded outcome dates. - Both age fields reportedly
contained 10 negative-age entries. - An initial note recorded that
`MonthYear` reconciled with the local timestamps after preserving
source-local time. This must be retested and documented. - Outcome
subtype missingness was reported at approximately 54.16%; avoid
conclusions based on subtype without assessing missingness and category
definitions.

### 6.5 Preliminary categorical profile

Initial reported counts: - Stray intakes: 119,160 of 173,812 intake rows
(approximately 68.6%). - Adoption outcomes: 84,598 of 173,775 outcome
rows (approximately 48.7%). - Dogs: approximately 54.4% of intake
rows. - Cats: approximately 39.9% of intake rows. - Owner surrenders:
35,563 intake rows. - Transfers: 48,689 outcome rows.

**Interpretation warning:** These are separate dataset row shares, not
conversion rates. An intake-row percentage and an outcome-row percentage
do not establish the proportion of intake animals that adopted. Use
matched visits and clearly defined denominators for conversion or
outcome rates.

### 6.6 Preliminary annual trend

The initial audit reported these annual event counts:

  Year     Intakes   Outcomes Note
  ------ --------- ---------- ---------------------------------
  2013       4,182      4,505 Partial year
  2014      18,656     18,709 Full year
  2015      18,712     18,506 Full year
  2016      17,675     17,670 Full year
  2017      17,563     17,657 Full year
  2018      16,979     16,741 Full year
  2019      19,727     19,775 Full year
  2020       9,587      9,778 Full year
  2021      12,043     11,967 Full year
  2022      11,896     11,885 Full year
  2023      11,227     11,151 Full year
  2024      11,817     11,822 Full year
  2025       3,748      3,609 Partial year through 05-05-2025

Initial interpretation: - 2020 intake records were reported to be 51.4%
lower than 2019. - 2020 outcome records were reported to be 50.6% lower
than 2019. - This is an investigation lead only. Do not attribute the
decline to COVID-19 or any specific policy without evidence. - Partial
years 2013 and 2025 must not be compared directly with full calendar
years without normalisation or equivalent-period comparison.

------------------------------------------------------------------------

## 7. Initial business opportunity register --- hypotheses only

Investigate approximately 12--15 opportunities. The following 15 were
proposed:

1.  Intake volume and seasonality --- staffing and capacity planning.
2.  Stray animal intake patterns --- resource allocation and field
    response.
3.  Owner surrender analysis --- prevention and community support.
4.  Adoption performance --- improve adoption pathways.
5.  Return-to-owner performance --- improve reunification.
6.  Transfer dependency --- understand external placement reliance.
7.  Length-of-stay analysis --- reduce shelter occupancy duration.
8.  Long-stay animal identification --- prioritise difficult-to-place
    animals.
9.  Euthanasia analysis --- identify intervention opportunities.
10. Animal mortality analysis --- improve welfare and care.
11. Intake condition analysis --- identify medical resource
    requirements.
12. Animal age segmentation --- understand vulnerable populations.
13. Breed-level outcome patterns --- explore placement differences.
14. Intake-to-outcome flow analysis --- understand operational
    throughput.
15. Repeat animal visits --- identify recurring shelter demand.

These are not approved findings. Score each on: - Business relevance and
potential impact. - Data availability and reliability. - Analytical
depth. - Actionability. - Clarity for an executive audience. - Risk of
misleading interpretation.

Identify the strongest eight internally; select only three validated,
compelling findings for the director.

------------------------------------------------------------------------

## 8. Austin / Texas operating context --- research leads, not legal advice

The candidate requested local context because the interview is with a
US-based hiring team and the exercise concerns Austin, Texas.

The purpose is to understand the operating environment and use relevant
context naturally in the presentation. Do not overstate legal knowledge,
offer legal advice, or imply the dataset proves compliance.

### Research leads captured during initial web research

1.  **Organisation and mission:** Austin Animal Services provides
    sheltering, animal protection, pet resources, and placement
    services. Its work spans animal welfare, public safety, community
    service, and shelter capacity.
    -   Official overview:
        https://www.austintexas.gov/animal-services/about
2.  **Stray holds and reclaim:** Initial research noted public guidance
    describing a 72-hour stray hold and Austin City Code §3-1-25
    language describing three business days for owner reclamation,
    excluding the initial impound date. These formulations must be
    checked against the current official text and explained carefully;
    do not casually equate business days with 72 calendar hours.
    -   Reclaim guidance:
        https://www.austintexas.gov/animal-services/reclaim-your-pet
    -   Austin City Code:
        https://library.municode.com/tx/austin/codes/code_of_ordinances/340792
3.  **Owner surrender and ownership:** Initial research noted that
    voluntary surrender by a legal owner may transfer ownership to the
    City immediately under the relevant Austin code provision, while
    stray animals follow an impound/reclamation process. Verify current
    code wording before using this in the interview.
    -   Ordinance FAQ:
        https://www.austintexas.gov/animal-services/ordinance-change-faqs
4.  **Texas shelter standards:** Texas Health and Safety Code Chapter
    823 includes requirements related to animal separation, veterinary
    inspection, and microchip scanning. Check current statutory wording
    and applicability before making a specific claim.
    -   Statute:
        https://statutes.capitol.texas.gov/Docs/HS/pdf/HS.823.pdf
5.  **Live-release policy:** Initial research identified an Austin 95%
    live-release mandate and a 90% national No Kill benchmark referenced
    by the City. The 2024 ordinance reportedly clarified treatment of
    certain wildlife in the domestic-animal live-release calculation.
    Confirm current definitions, numerator, denominator, exclusions, and
    reporting period before calculating or quoting a live-release rate.
    -   Ordinance FAQ:
        https://www.austintexas.gov/animal-services/ordinance-change-faqs
    -   Animal Services: https://www.austintexas.gov/animal-services/
6.  **Dangerous dog assessments:** Initial research noted Austin's use
    of the Dunbar Bite Scale for certain assessments involving dogs
    legally owned by the City, with serious bite cases requiring
    case-specific review. Do not imply an automatic euthanasia outcome.
    -   Ordinance FAQ:
        https://www.austintexas.gov/animal-services/ordinance-change-faqs
7.  **Shelter capacity memorandum:** Initial research identified a City
    memorandum dated 01-07-2024 reporting capacity pressure:
    -   149 animals impounded during 24--26 June 2024.
    -   124 adopted, rescued, or fostered during the same period.
    -   An average weekly intake surplus of 14 animals.
    -   24 dogs in private boarding facilities.
    -   Weekly boarding expenditure reported at \$5,000--\$6,000.
    -   Temporary public intake restrictions reportedly began
        02-07-2024, with emergency exceptions.

    This is historical context, not a statement of current shelter
    operations. Locate and retain the original official memorandum
    before quoting figures in the final presentation.

### How to use local context

Use it selectively to frame a business question. Example:

"Given Austin's live-release objectives and the capacity pressures
documented by the City in 2024, I looked beyond intake volume and
examined how incoming demand relates to placement outcomes and length of
stay."

This is only an illustrative speaking line. Use it only if the relevant
data analysis supports the associated point, and verify policy context
before the interview.

------------------------------------------------------------------------

## 9. Technical and analytical rules to preserve

1.  Never join intake and outcome tables only on `Animal ID` and assume
    a one-to-one visit relationship.
2.  Compare sequence, FIFO, and LIFO approaches and document the chosen
    business rule.
3.  Do not force ambiguous records into matches.
4.  Preserve raw source files unchanged.
5.  Keep cleaned analytical copies separate from raw files.
6.  Preserve source-local timestamp meaning; investigate timezone
    semantics rather than applying arbitrary conversion.
7.  Keep dates as date/datetime types; display as `DD-MM-YYYY`.
8.  Do not treat missing outcome subtype as a meaningful category
    without explaining missingness.
9.  Distinguish event counts from unique animals and from matched
    visits.
10. Distinguish intake-row percentages from outcome rates or conversion
    rates.
11. Mark partial years clearly.
12. Do not infer causation from time-series correlation.
13. Do not treat long stays as errors without record-level review.
14. Explain all exclusions, deduplication, and denominator choices.
15. Every headline metric must be reproducible and traceable to a
    documented definition.

------------------------------------------------------------------------

## 10. Recommended project folder structure

Create a local project folder first. Do not create a GitHub repository
until the local structure and initial audit outputs are ready.

``` text
austin-animal-center-analytics/
│
├── README.md
├── DECISION_LOG.md
├── CHANGELOG.md
├── .gitignore
│
├── data/
│   ├── raw/
│   │   ├── Austin_Animal_Center_Intakes.csv
│   │   └── Austin_Animal_Center_Outcomes.csv
│   ├── processed/
│   └── reference/
│
├── powerbi/
│   ├── Austin_Animal_Center_Analytics.pbix
│   ├── screenshots/
│   └── dax/
│
├── analysis/
│   ├── audit_datasets.py
│   ├── match_visits.py
│   ├── explore_business_opportunities.py
│   └── tests/
│
├── outputs/
│   ├── audit/
│   ├── matching/
│   └── analysis/
│
├── docs/
│   ├── DATA_AUDIT_REPORT.md
│   ├── DATA_DICTIONARY.md
│   ├── VISIT_MATCHING_METHODOLOGY.md
│   ├── BUSINESS_OPPORTUNITY_REGISTER.md
│   ├── DATA_QUALITY_ISSUES.md
│   ├── AUSTIN_POLICY_CONTEXT.md
│   ├── TECHNICAL_IMPLEMENTATION_GUIDE.md
│   └── INTERVIEW_PREPARATION.md
│
├── website/
│   ├── index.html
│   ├── css/
│   ├── js/
│   └── assets/
│
└── presentation/
    ├── PRESENTATION_SCRIPT.md
    └── SPEAKER_NOTES.md
```

**Repository privacy and size:** inspect the public datasets' terms and
the hiring team's expectations before publishing source data. Avoid
committing unnecessary large or sensitive files. Use Git LFS only if
justified and supported. The PBIX may be large; consider Git LFS or a
documented release/download approach. Never commit credentials, tokens,
private email content, or confidential information.

------------------------------------------------------------------------

## 11. Immediate next-step plan

### Stage 0 --- Local setup (before Claude Code audit)

-   Create the local project folder.
-   Create the folder structure.
-   Copy the two original CSV files into `data/raw/`.
-   Copy the blank PBIX into `powerbi/`.
-   Keep the HTML reference in a clearly labelled inspiration/reference
    location; do not treat it as project content.
-   Save this decision log as `DECISION_LOG.md`.
-   Create a `.gitignore`.
-   Do not initialise or publish GitHub until the initial structure and
    data-handling plan are checked.

### Stage 1 --- Claude Code analytical audit

Give Claude Code a consolidated audit instruction to independently
reproduce all preliminary results, investigate discrepancies, compare
visit-matching approaches, produce scripts, reports, exception files,
and automated validation.

### Stage 2 --- Human review and approval

Review Claude Code's audit against this decision log. Resolve the
matching rule and metric definitions before dashboard development.

### Stage 3 --- Opportunity ranking

Evaluate 12--15 opportunities, select eight internally, and approve
three director-facing findings.

### Stage 4 --- Power BI build

Build the 2--3 page PBIX with the required model, date table,
length-of-stay measure, year-over-year comparison, slicers, and three
actionable findings.

### Stage 5 --- Website integration

Build the single interactive presentation/dashboard website, using the
supplied HTML only as a design reference.

### Stage 6 --- Final validation and interview preparation

Verify all calculations, prepare the presentation script, technical
explanation, likely director questions, fallback answers, and CRM
discussion preparation.

------------------------------------------------------------------------

## 12. Open decisions / questions --- do not assume answers

1.  What exact event-matching rule best represents one shelter visit
    when multiple intakes/outcomes exist for the same Animal ID?
2.  How should same-day intake/outcome records be represented in
    length-of-stay calculations?
3.  Should open stays be shown separately from completed stays?
4.  What is the precise official live-release formula, including
    wildlife exclusions and other policy definitions?
5.  Which historical periods are comparable, given partial 2013 and 2025
    data and policy/operational changes?
6.  Which eight opportunities score highest after data validation?
7.  Which three findings have the strongest evidence and clearest
    director actions?
8.  What Power BI embedding/hosting method is feasible for the final
    website and interview environment?
9.  What is the safest and most appropriate way to publish the PBIX and
    supporting artifacts on GitHub?

------------------------------------------------------------------------

## 13. Change-log convention

Update this file whenever a material decision changes. Add a dated entry
to `CHANGELOG.md` for implementation changes.

Suggested entry format:

``` text
Date:
Decision / change:
Previous approach:
New approach:
Reason:
Evidence:
Impact on data model / DAX / report / website:
Approved by:
```

Do not erase superseded findings. Mark them as superseded and preserve
why the decision changed.

------------------------------------------------------------------------

**End of current project record.**\
This file is the continuity document for future project stages. Re-read
it before making material changes to data preparation, visit matching,
KPI definitions, dashboard scope, website behaviour, or presentation
claims.
