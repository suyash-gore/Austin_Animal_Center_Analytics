# Interview Preparation Kit — Austin Animal Center Analytics

Backup material for questions after the presentation. Keep these details **out** of the main talk unless asked.
Numbers are from the validated outputs (see `CLAUDE_PROJECT_KNOWLEDGE_KIT.md`, Appendix A). Answers are written to
be spoken in 20–40 seconds.

**Golden rules:** name the statistic and its denominator · say "pattern", not "cause" · LOS is time to the final
recorded outcome, not kennel time · the provisional outcome grouping is not the official live-release rate · the
findings are my recommendations, not approved by the director · be honest about what AI helped implement and what
you verified yourself.

### Interview format (Thursday 26-11-2026, 19:00 IST, 45–50 minutes)

| Segment | Time | Material |
|---|---|---|
| Report and findings | 10 min | `website/index.html` + `presentation/PRESENTATION_SCRIPT.md` |
| Data model and DAX | 5 min | `presentation/DATA_MODEL_AND_DAX_WALKTHROUGH.md` |
| Data problems discovered | 5 min | `presentation/DATA_QUALITY_WALKTHROUGH.md` |
| Power BI and SQL questions | remaining | this kit — sections 1–10 (project, Power BI, CRM) and **section 11 (SQL)** |
| Live report changes (screen-share) | during questions | `presentation/POWER_BI_DEMO_PLAN.md` — *Live Power BI Practice Exercises* |

Have Power BI Desktop open with the submitted PBIX (a practice copy for any edits — see the demo plan).

---

## 1. Business problem and prioritisation

**Q: How did you decide what to analyse?**
I started from the director's three questions and listed fifteen candidate opportunities. Each was scored one to
five on business relevance, data availability, data reliability, analytical depth, actionability and
interpretation safety. The top eight were owner surrender (28/30), intake volume and seasonality, adoption, length
of stay (26 each), return to owner (25), throughput (24), stray intake and age-based outcomes (23).

**Q: Why these three findings and not, say, seasonality?**
Each combines robust evidence, a lever the shelter controls and a one-sentence definition. Seasonality is useful
for staffing context and is in the report, but it describes demand rather than something the shelter can change.

**Q: What did you reject and why?**
Breed patterns (visual labels, stigma risk), the official live-release rate (formula not verified), and the cause
of the 2020 drop (the data shows timing, not causes). Transfer dependency scored low because "Transfer" mixes partner
placements with community-cat return programmes.

**Q: Who approved the findings?**
No one yet — they are my candidate findings for the director, with evidence and caveats.

## 2. Data cleaning and duplicate handling

**Q: What did you find in the raw data?**
173,812 intake and 173,775 outcome records, 12 columns each, 01-10-2013 to 05-05-2025. Structurally clean
(every timestamp parses), but: 36 and 26 exact duplicate rows; a "-05:00" suffix on 3,584 outcome timestamps;
54% of outcome subtypes blank (mostly by design); a few negative ages and birth dates after the outcome; category
changes over time (e.g. "Abandoned" from 2020).

**Q: How did you treat duplicates?**
Three classes: exact duplicate rows were excluded (leaving 173,776 intake and 173,749 outcome events); records
with the same animal and timestamp but different details were kept and flagged; repeat intakes for the same animal
are real repeat visits.

**Q: The outcome timestamps had a timezone offset — did you convert them?**
No. Every offset row is exactly midnight, and the offset is −05:00 even in winter when Austin is −06:00, so it's an
export artefact marking date-only records. The month-year column matches the wall-clock time on every row.
Converting would have shifted dates.

**Q: Did you change the source data?**
No. The raw files are read-only and checksum-verified; all cleaning happens on derived copies in Python, and Power
Query reads those derived files.

## 3. Visit matching

**Q: Why can't you just join intakes and outcomes on Animal ID?**
Animal ID identifies the animal, not the visit. One animal can come in many times — one has 33 intakes — so a direct
join creates every intake-outcome combination for that animal and produces wrong and even negative durations.

**Q: How did you reconstruct visits?**
Chronologically, per animal: an intake is paired with the animal's next outcome, unless the animal was taken in again
first; in that case the earlier intake is treated as having no recorded outcome. Each record is used at most once and
an animal can never be in two visits at the same time.

**Q: Did you consider alternatives?**
Yes — a sequence-number join (k-th intake to k-th outcome: 784 negative durations), FIFO and LIFO (one-to-one, but
they create overlapping or nested visits for the same animal), and "latest preceding intake" (re-uses intakes). The
chronological adjacent-event rule was the only one with no overlaps and no sensitivity to duplicate removal.

**Q: Does every intake have an outcome?**
No. Of 174,978 candidate visits, 172,547 are matched; 1,229 intakes have no matched outcome (mostly still in care at
the end of the extract) and 1,202 outcomes have no matched intake (mostly intakes before October 2013). They're kept in
the visit table with a reason, and excluded from length of stay.

**Q: What are the 225 same-day pairs?**
Outcomes logged a few hours before a same-day intake for the same animal. Probably recording order, but the data
can't prove it, so they're excluded from confirmed matches and flagged. Including them moves the 90th-percentile
LOS from 55.56 to 55.34 days and no finding materially.

**Q: How do you know the matching is right?**
Unit tests on synthetic cases, reconciliation (matched + unmatched = events on both sides), zero negative durations,
zero overlapping visits (checked at date and exact-timestamp level), and six sensitivity scenarios in which no
finding moved by more than about 0.05 percentage points.

## 4. Data model and dates

**Q: Describe the model.**
A star schema: three fact tables — intake events, outcome events and visits — and three dimensions: a date table,
animal type and intake type. All relationships are one-to-many and single-direction; nothing joins on Animal ID and
the facts aren't joined to each other.

**Q: Why three fact tables?**
They have different grains. Volumes and trends use events; length of stay and visit outcomes use visits.

**Q: How do dates work?**
The date table relates to intake date for intakes, outcome date for outcomes, and intake date for visits — so visit
measures are by intake cohort. Visits also have an inactive relationship on outcome date, activated in specific
measures with USERELATIONSHIP.

**Q: Does the intake-type slicer filter outcomes?**
It filters intake events and visits. Outcome events carry no intake type, so there is no relationship to them.

**Q: Why is there a blank intake type?**
The 1,202 outcome-only visit rows have no intake, so they sit under the blank member.

## 5. Length of stay

**Q: How is LOS calculated?**
Outcome timestamp minus intake timestamp, in days, for matched visits only — implemented as measures with the
matched-visit filter inside the measure. Median 6.00 days, average 21.03, 90th percentile 55.56.

**Q: Is LOS the time animals spend in the kennel?**
No. It's time to the final recorded outcome. Foster placement isn't recorded in either file, so shelter and foster
time can't be separated. That's why Finding 1 is also shown for dogs with no foster subtype: 4.95 → 8.94 days.

**Q: What are same-day and zero-duration visits?**
Same-day = intake and outcome on the same calendar date (22,149). Under 24 hours = 32,417. Exactly zero = 439, of
which 416 are date-only outcomes on the intake date set to zero, and 23 have identical timestamps — a diagnostic, not
a business KPI.

**Q: Pooled median versus average of annual medians?**
5.12 → 12.08 days is the median of all dog visits in each period (pooled). The average of the yearly medians is
5.12 → 12.38. Same direction; always name which one.

## 6. Year-over-year and partial years

**Q: How do you handle 2013 and 2025?**
The extract runs from 01-10-2013 to 05-05-2025. YoY measures return blank unless the prior period is fully inside the
data and the current period is complete — so 2013, 2014 (its prior year is partial) and 2025 are blank. For 2025 I use
a like-for-like window, 1 January to 4 May: 3,745 intakes vs 3,991 in 2024 (−6.2%).

**Q: Give an example.**
2020 intakes were 9,585 vs 19,726 in 2019 (−51.4%); the drop starts in March 2020. I don't attribute a cause.

## 7. Power BI, Power Query and DAX concepts

* **Power Query / M:** the ETL layer. My queries read the processed CSVs through a `RepoRoot` parameter, set explicit
  types, parse ISO dates with a fixed format (no locale guessing), convert 1/0 flags to true/false, and fail on schema
  changes. Query folding doesn't apply to CSV sources.
* **Star schema and grain:** one fact row = one event or one visit; dimensions describe them; one-to-many,
  single-direction filters avoid ambiguity.
* **Measure vs calculated column:** measures are evaluated in the filter context of the visual (all KPIs here);
  calculated columns are computed per row at refresh and stored.
* **Row vs filter context; CALCULATE:** CALCULATE changes the filter context — e.g. `CALCULATE(COUNTROWS(FactVisits),
  FactVisits[visit_status] = "Matched visit")`.
* **Time intelligence:** a marked, continuous date table; `SAMEPERIODLASTYEAR(DimDate[Date])` for prior year;
  `DIVIDE` to avoid division by zero; a guard that blanks partial comparison periods.
* **USERELATIONSHIP / REMOVEFILTERS:** activate an inactive relationship inside a measure; clear filters on a table.
* **BLANK handling:** in DAX `BLANK() = 0` is true, so diagnostics use `==` and an explicit matched-visit filter.
* **PERCENTILE.INC:** used for P90; matches the Python calculation.
* **Slicers and interactions:** synced slicers across the analytical pages; cross-filtering between visuals; page
  navigation buttons on the Executive Summary.
* **Auto date/time:** turned off; visuals use the model's own date table.
* **Service topics (if asked):** publishing to a workspace, scheduled refresh needs a gateway for local files (or
  repointing sources to SharePoint or a database), row-level security via roles, apps for distribution, Performance
  Analyzer for slow visuals.
* **Viewing vs refreshing the PBIX:** CSV sources can only be imported in Power BI, so the data is stored in the file
  and can be viewed anywhere; refreshing requires the processed CSVs at the `RepoRoot` path.

## 8. Findings, limitations, recommendations

**Finding 1 — Dog LOS.** Pooled median 5.12 days (2014–2019, 61,626 visits) → 12.08 (2023–2024, 10,134 visits).
Holds without foster-subtype outcomes. Intake −40% (2019→2024), estimated in-care −18%. *Action:* day-14/day-30
long-stay reviews; track the share of dogs over 30 days (22.58% baseline, non-foster).

**Finding 2 — Owner surrender.** 2016–2024, of 27,256 owner-surrender visits: 24.46% had a prior adoption here;
14.89% within 30 days; 8.96% within 7 days. *Don't say* "61.69% within 30 days" as a share of surrenders — that's a
share of returns across all years. *Action:* first-30-days adopter support.

**Finding 3 — Stray-dog RTO.** 29.46% (2014–2019 average) → 12.51% (2024); 2,036 → 386 dogs. *Caveat:* field returns
without intake aren't in the data. *Action:* microchip scan at intake, same-day posting, contact-data quality, free
microchip/ID promotion.

**Limitations to volunteer if asked:** LOS isn't kennel time; surrender reasons and field returns not recorded;
partial years; 225 unconfirmed same-day pairs and 45 animals with method-dependent matches; provisional outcome
grouping; no causal claims.

**Q: What would you do with more time or data?**
Get foster start/end dates, surrender reasons and field-return records; verify the official live-release formula;
break long stays down by intake type, age and outcome; set the three KPIs up as a monthly scorecard.

## 9. CRM concepts (platform not specified — answer in transferable terms)

The job's CRM platform isn't stated in the project material; don't assume Salesforce or Dynamics 365. Use the shelter
as a worked analogy.

| CRM concept | Meaning | Shelter analogy |
|---|---|---|
| Contact / account | person / organisation record | adopter, owner, rescue partner |
| Lead → opportunity | prospect moving through qualification | adoption enquiry → application → adoption |
| Pipeline and stages | ordered steps with conversion between them | intake → available → adopted |
| Activities / tasks | calls, emails, follow-ups logged against a record | day-3 and day-14 adopter check-ins |
| Cases / tickets | service issues with status and SLA | behaviour-support request after adoption |
| Campaigns | targeted outreach measured by response | microchip clinics, adoption events |
| Segmentation | groups for tailored treatment | first-time adopters, returning owners |
| Retention / churn | keeping customers; losing them | an adoption return is "churn" |
| Customer 360 | one view of all interactions | an animal's and adopter's full history across visits |

**Data quality in CRM** maps directly to this project: deduplication (exact vs near duplicates), matching records to
the right entity (Animal ID ≠ visit, like contact ≠ deal), standardised fields, validation rules, and audit trails.

**Q: How would a CRM help the shelter?**
Finding 2 is essentially a retention problem: a CRM could trigger check-in tasks after each adoption, log behaviour
cases, and report 30-day return rates by segment. Finding 3 is a matching problem: linking microchip and owner records
quickly at intake.

**Q: How do CRM and Power BI fit together?**
The CRM is the operational system of record; Power BI connects to it (connector, API or warehouse) for cross-system
reporting — pipeline conversion, case backlog, response times, retention — with the same modelling principles used
here: clear grain, conformed dimensions, measures with explicit definitions.

## 10. Process and integrity

**Q: Did you use AI?**
Answer honestly: an AI coding assistant implemented much of the Python pipeline, tests and documentation under my
direction; I defined the questions, reviewed the decisions and evidence, built and checked the Power BI report in
Desktop, and can explain each method and number. Every figure is reproducible from scripts and tested.

**Q: How would someone reproduce your numbers?**
`pip install -r requirements.txt`, `python analysis/run_all.py`, then `python -m pytest analysis/tests -q` (86 tests
pass); the model validator checks the Power BI inputs (151 checks pass).

---

## 11. SQL interview preparation

### 11.0 Read this first

* **The project did not use a SQL database.** Cleaning and visit matching were done in Python (pandas); Power BI
  reads the resulting CSV files. Everything below is an **illustrative SQL exercise** using the project's real
  table structure and verified column names — useful because the interviewer may ask "how would you do this in
  SQL?".
* **Dialect: Microsoft SQL Server (T-SQL)** — the most common partner to Power BI. PostgreSQL differences are noted
  where they matter.
* **Checked against the data:** the *logic* of every query in 11.3 was run in SQLite against the project CSVs on
  25-11-2026 and reproduced the validated figures shown under each query. The T-SQL text itself was not executed on
  a SQL Server instance.
* **If asked "did you use SQL in this project?"** — "No, the pipeline is Python, but the same logic translates
  directly to SQL; for example, I'd find duplicates with GROUP BY … HAVING and rebuild visits with a window
  function."

### 11.1 Assumed tables (loaded from the project files)

| SQL table | Source file | Key columns used below |
|---|---|---|
| `dbo.raw_intakes` | `data/raw/Austin_Animal_Center_Intakes__10_01_2013_to_05_05_2025_.csv` | `[Animal ID]`, `[Name]`, `[DateTime]`, `[MonthYear]`, `[Found Location]`, `[Intake Type]`, `[Intake Condition]`, `[Animal Type]`, `[Sex upon Intake]`, `[Age upon Intake]`, `[Breed]`, `[Color]` (all text, as in the source) |
| `dbo.intakes_clean` | `data/processed/intakes_clean.csv` | `intake_event_id`, `animal_id`, `intake_datetime` (datetime2), `intake_date` (date), `intake_type`, `animal_type`, `is_exact_duplicate` (bit) |
| `dbo.outcomes_clean` | `data/processed/outcomes_clean.csv` | `outcome_event_id`, `animal_id`, `outcome_datetime`, `outcome_date`, `outcome_type`, `outcome_subtype`, `outcome_group`, `outcome_is_midnight` (bit), `is_exact_duplicate` (bit) |
| `dbo.candidate_visits` | `outputs/matching/candidate_visits.csv` | `visit_id`, `visit_status`, `animal_id`, `intake_event_id`, `outcome_event_id`, `intake_datetime`, `outcome_datetime`, `intake_date`, `los_days`, `animal_type`, `intake_type`, `outcome_group`, `same_day_visit` |

`visit_status` values: `'Matched visit'`, `'Intake without matched outcome'`, `'Outcome without matched intake'`.
Space-containing source column names need square brackets in T-SQL (`[Animal ID]`; PostgreSQL uses `"Animal ID"`).

### 11.2 Core concepts in one breath each

| Topic | What to say | Project example |
|---|---|---|
| `SELECT … WHERE … ORDER BY` | choose columns, filter rows, sort the result | stray intakes in 2024, newest first |
| `INNER JOIN` | only rows that match on both sides | visits joined to intakes on `intake_event_id` |
| `LEFT JOIN` | all rows from the left, matches from the right, NULLs where none | all intakes, with their visit if one exists → find unmatched |
| `RIGHT JOIN` | mirror of LEFT; usually rewritten as LEFT for readability | — |
| `FULL OUTER JOIN` | all rows from both sides | compare two lists of event IDs and see what's missing on each side |
| `GROUP BY` / aggregates | one row per group with `COUNT`, `SUM`, `AVG`, `MIN`, `MAX` | intakes per month |
| `HAVING` | filter **after** grouping (WHERE filters before) | groups with `COUNT(*) > 1` = duplicates |
| CTE (`WITH … AS`) | a named, readable sub-step | build the event stream, then match it |
| Subquery | a query inside another query | `WHERE NOT EXISTS (SELECT 1 …)` |
| `CASE WHEN` | if-then logic inside a query | label stays as same-day / short / long |
| `NULL`, `IS NULL`, `COALESCE` | NULL means unknown; `= NULL` never works; `COALESCE` gives a fallback | `COALESCE(outcome_subtype, '(not recorded)')` |
| `ROW_NUMBER` / `RANK` / `DENSE_RANK` | number rows within a group; RANK leaves gaps after ties, DENSE_RANK doesn't | visit number per animal |
| `LAG` / `LEAD` | value from the previous / next row in a window | previous visit's outcome; next event for the animal |
| Date filtering | use ranges on the raw column so indexes work | `intake_date >= '2024-01-01' AND intake_date < '2025-01-01'` |
| Indexing | speeds up lookups and joins on the indexed columns | index on `(animal_id, intake_datetime)` |
| Reconciliation | prove totals agree between steps | matched + intake-only = cleaned intakes |

### 11.3 Ten project queries

#### Q1 — Find duplicate intake records

```sql
-- Exact duplicates: rows identical in all 12 source columns
SELECT [Animal ID], [DateTime], [Intake Type], COUNT(*) AS copies
FROM dbo.raw_intakes
GROUP BY [Animal ID], [Name], [DateTime], [MonthYear], [Found Location], [Intake Type],
         [Intake Condition], [Animal Type], [Sex upon Intake], [Age upon Intake], [Breed], [Color]
HAVING COUNT(*) > 1;

-- Number the copies; rn > 1 are the excess rows
WITH numbered AS (
    SELECT *,
           ROW_NUMBER() OVER (
               PARTITION BY [Animal ID], [Name], [DateTime], [MonthYear], [Found Location], [Intake Type],
                            [Intake Condition], [Animal Type], [Sex upon Intake], [Age upon Intake], [Breed], [Color]
               ORDER BY (SELECT NULL)) AS rn
    FROM dbo.raw_intakes
)
SELECT COUNT(*) AS excess_copies FROM numbered WHERE rn > 1;   -- 36
```

* **Returns:** each duplicated record with its number of copies; then the count of extra copies — **36** (26 for
  outcomes).
* **Why useful:** duplicates inflate counts and can create duplicate visits.
* **Say:** "GROUP BY every column and HAVING COUNT greater than one finds exact duplicates; ROW_NUMBER lets me keep
  the first copy and flag the rest. In the project I flagged rather than deleted, so nothing is lost."
* *Deleting (if asked):* `DELETE FROM numbered WHERE rn > 1;` works in T-SQL through the CTE.

#### Q2 — Monthly intake volume

```sql
SELECT DATEFROMPARTS(YEAR(intake_date), MONTH(intake_date), 1) AS month_start,
       COUNT(*)                                                AS intake_events
FROM dbo.intakes_clean
WHERE is_exact_duplicate = 0
GROUP BY DATEFROMPARTS(YEAR(intake_date), MONTH(intake_date), 1)
ORDER BY month_start;
```

* **Returns:** one row per month with intake count — e.g. **March 2020 = 883, April 2020 = 312**.
* **Why useful:** trend and seasonality; this is what the monthly line chart shows.
* *PostgreSQL:* `date_trunc('month', intake_date)`; SQL Server 2022+ also has `DATETRUNC(month, intake_date)`.

#### Q3 — Outcome distribution

```sql
SELECT outcome_group,
       COUNT(*)                                            AS outcome_events,
       CAST(100.0 * COUNT(*) / SUM(COUNT(*)) OVER () AS decimal(5,2)) AS pct_of_outcome_events
FROM dbo.outcomes_clean
WHERE is_exact_duplicate = 0
GROUP BY outcome_group
ORDER BY outcome_events DESC;
```

* **Returns:** Adoption **84,586**, Transfer 48,683, Return to Owner 26,928, Euthanasia 10,832, …
* **Why useful:** the outcome mix. `SUM(COUNT(*)) OVER ()` is a window over the grouped result — the grand total on
  every row.
* **Careful:** these are shares of outcome **events**, not conversion rates from intakes.

#### Q4 — Match intakes to outcomes chronologically

```sql
WITH events AS (
    SELECT animal_id, intake_event_id AS event_id, 'I' AS kind,
           intake_datetime AS sort_dt, 0 AS kind_order
    FROM dbo.intakes_clean
    WHERE is_exact_duplicate = 0
    UNION ALL
    SELECT animal_id, outcome_event_id, 'O',
           -- date-only (midnight) outcomes count as happening later that day
           CASE WHEN outcome_is_midnight = 1
                THEN DATEADD(SECOND, 86399, CAST(outcome_date AS datetime2))
                ELSE outcome_datetime END,
           1
    FROM dbo.outcomes_clean
    WHERE is_exact_duplicate = 0
),
ordered AS (
    SELECT *,
           LEAD(kind)     OVER (PARTITION BY animal_id ORDER BY sort_dt, kind_order, event_id) AS next_kind,
           LEAD(event_id) OVER (PARTITION BY animal_id ORDER BY sort_dt, kind_order, event_id) AS next_event_id
    FROM events
)
SELECT animal_id, event_id AS intake_event_id, next_event_id AS outcome_event_id
FROM ordered
WHERE kind = 'I' AND next_kind = 'O';
```

* **Returns:** one row per matched visit — **172,547** pairs, identical to the project's primary matched visits.
* **How it works:** stack intakes and outcomes into one timeline per animal, sort it, and pair each intake with the
  **next** event if that event is an outcome. If the next event is another intake, the first intake has no
  recorded outcome; an outcome with no intake just before it stays unmatched.
* **Say:** "That's the adjacent-event rule in one window function: an intake pairs with the next outcome unless the
  animal came in again first."

#### Q5 — Unmatched intake and outcome records

```sql
-- Intakes with no matched visit
SELECT i.intake_event_id, i.animal_id, i.intake_datetime
FROM dbo.intakes_clean AS i
LEFT JOIN dbo.candidate_visits AS v
       ON v.intake_event_id = i.intake_event_id
      AND v.visit_status = 'Matched visit'
WHERE i.is_exact_duplicate = 0
  AND v.visit_id IS NULL;                       -- 1,229

-- Same idea with NOT EXISTS, for outcomes
SELECT o.outcome_event_id, o.animal_id, o.outcome_datetime
FROM dbo.outcomes_clean AS o
WHERE o.is_exact_duplicate = 0
  AND NOT EXISTS (SELECT 1 FROM dbo.candidate_visits AS v
                  WHERE v.outcome_event_id = o.outcome_event_id
                    AND v.visit_status = 'Matched visit');   -- 1,202
```

* **Why useful:** shows what didn't pair — mostly still in care (intakes) or arrived before October 2013 (outcomes).
* **Trap:** put the `visit_status` condition in the **ON** clause. In the WHERE clause it would turn the LEFT JOIN
  into an INNER JOIN and return nothing.

#### Q6 — Length of stay

```sql
WITH los AS (
    SELECT visit_id, animal_type,
           CASE WHEN DATEDIFF(SECOND, intake_datetime, outcome_datetime) < 0 THEN 0.0
                ELSE DATEDIFF(SECOND, intake_datetime, outcome_datetime) / 86400.0
           END AS los_days                       -- negative only for date-only same-day outcomes → 0
    FROM dbo.candidate_visits
    WHERE visit_status = 'Matched visit'
)
SELECT DISTINCT
       PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY los_days) OVER () AS median_los,   -- 6.00
       PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY los_days) OVER () AS p90_los,      -- 55.56
       AVG(los_days) OVER ()                                         AS avg_los       -- 21.03
FROM los;
```

* **Returns:** median **6.00**, P90 **55.56**, average **21.03** days — the same as the Power BI measures.
* **Why useful:** LOS is the core visit metric; `PERCENTILE_CONT` uses the same interpolation as DAX
  `PERCENTILE.INC`.
* *T-SQL note:* `PERCENTILE_CONT` is a window function in SQL Server (hence `OVER ()` and `DISTINCT`); in PostgreSQL
  it is an ordered-set aggregate: `SELECT percentile_cont(0.5) WITHIN GROUP (ORDER BY los_days) FROM los;`
* **Say:** "Time from intake to final recorded outcome, matched visits only — not kennel time."

#### Q7 — Owner surrenders following a recent adoption

```sql
WITH mv AS (
    SELECT *,
           LAG(outcome_group)    OVER (PARTITION BY animal_id ORDER BY intake_datetime, intake_event_id) AS prev_outcome_group,
           LAG(outcome_datetime) OVER (PARTITION BY animal_id ORDER BY intake_datetime, intake_event_id) AS prev_outcome_datetime
    FROM dbo.candidate_visits
    WHERE visit_status = 'Matched visit'
),
os AS (
    SELECT *, DATEDIFF(SECOND, prev_outcome_datetime, intake_datetime) / 86400.0 AS days_since_prev_outcome
    FROM mv
    WHERE intake_type = 'Owner Surrender'
      AND intake_date >= '2016-01-01' AND intake_date < '2025-01-01'
)
SELECT COUNT(*) AS owner_surrenders,                                                        -- 27,256
       SUM(CASE WHEN prev_outcome_group = 'Adoption' THEN 1 ELSE 0 END) AS after_any_adoption,  -- 6,668 (24.46%)
       SUM(CASE WHEN prev_outcome_group = 'Adoption' AND days_since_prev_outcome <= 30
                THEN 1 ELSE 0 END) AS within_30_days,                                        -- 4,058 (14.89%)
       SUM(CASE WHEN prev_outcome_group = 'Adoption' AND days_since_prev_outcome <= 7
                THEN 1 ELSE 0 END) AS within_7_days                                         -- 2,441 (8.96%)
FROM os;
```

* **Returns:** the Finding 2 numbers exactly.
* **How it works:** `LAG` looks back to the animal's previous matched visit; `CASE WHEN` counts those that ended in
  adoption, overall and within 30 / 7 days.
* **Why the LAG is computed before filtering:** if you filter to owner surrenders first, the "previous visit" would
  be the previous *owner surrender*, not the previous visit.

#### Q8 — Return-to-owner percentage for stray dogs

```sql
SELECT YEAR(intake_date) AS intake_year,
       COUNT(*) AS stray_dog_visits,
       SUM(CASE WHEN outcome_group = 'Return to Owner' THEN 1 ELSE 0 END) AS rto_visits,
       CAST(100.0 * SUM(CASE WHEN outcome_group = 'Return to Owner' THEN 1 ELSE 0 END) / COUNT(*)
            AS decimal(5,2)) AS rto_pct
FROM dbo.candidate_visits
WHERE visit_status = 'Matched visit'
  AND animal_type = 'Dog'
  AND intake_type = 'Stray'
GROUP BY YEAR(intake_date)
ORDER BY intake_year;
```

* **Returns:** e.g. 2019 = 7,556 visits, **2,036** RTO, 26.95%; 2024 = 3,086 visits, **386** RTO, **12.51%**. The
  average of the 2014–2019 yearly percentages is **29.46%**.
* **Why `100.0`:** integer division would return 0; multiplying by a decimal first forces decimal arithmetic.
* **Say:** "Denominator is matched stray-dog visits; Return to Owner includes Rto-Adopt."

#### Q9 — Window functions for previous visits

```sql
SELECT animal_id, visit_id, intake_datetime, intake_type, outcome_group,
       ROW_NUMBER() OVER (PARTITION BY animal_id ORDER BY intake_datetime) AS visit_number,
       LAG(outcome_group) OVER (PARTITION BY animal_id ORDER BY intake_datetime) AS previous_outcome,
       DATEDIFF(DAY,
                LAG(outcome_datetime) OVER (PARTITION BY animal_id ORDER BY intake_datetime),
                intake_datetime) AS days_since_previous_outcome,
       LEAD(intake_datetime) OVER (PARTITION BY animal_id ORDER BY intake_datetime) AS next_intake
FROM dbo.candidate_visits
WHERE visit_status = 'Matched visit';
```

* **Returns:** every visit with its number for that animal, the previous outcome, days since it, and the next intake.
* **ROW_NUMBER vs RANK vs DENSE_RANK:** with a tie on the ordering value, ROW_NUMBER still gives 1, 2; RANK gives 1, 1,
  then 3; DENSE_RANK gives 1, 1, then 2. For visit numbers I want ROW_NUMBER, with a tie-breaker (e.g. `visit_id`) in
  the ORDER BY so the result is deterministic.

#### Q10 — Validate record counts and data quality

```sql
-- 1. Reconciliation: every cleaned event appears exactly once in the visit table
SELECT
  (SELECT COUNT(*) FROM dbo.intakes_clean  WHERE is_exact_duplicate = 0) AS intake_events,     -- 173,776
  (SELECT COUNT(*) FROM dbo.outcomes_clean WHERE is_exact_duplicate = 0) AS outcome_events,    -- 173,749
  (SELECT COUNT(*) FROM dbo.candidate_visits WHERE intake_event_id  IS NOT NULL) AS visit_rows_with_intake,   -- 173,776
  (SELECT COUNT(*) FROM dbo.candidate_visits WHERE outcome_event_id IS NOT NULL) AS visit_rows_with_outcome,  -- 173,749
  (SELECT COUNT(*) FROM dbo.candidate_visits) AS all_visit_rows;                                -- 174,978

-- 2. One-to-one: no intake or outcome used twice; no negative LOS
SELECT COUNT(*) - COUNT(DISTINCT intake_event_id)  AS reused_intakes,     -- 0
       COUNT(*) - COUNT(DISTINCT outcome_event_id) AS reused_outcomes,    -- 0
       SUM(CASE WHEN los_days < 0 THEN 1 ELSE 0 END) AS negative_los       -- 0
FROM dbo.candidate_visits
WHERE visit_status = 'Matched visit';

-- 3. Missing values (NULL handling)
SELECT COUNT(*) AS outcome_rows,
       SUM(CASE WHEN outcome_subtype IS NULL THEN 1 ELSE 0 END) AS subtype_missing   -- 94,115
FROM dbo.outcomes_clean;
```

* **Why useful:** proves nothing was lost or double-counted between steps — the same checks the Python tests run.
* `COUNT(column)` ignores NULLs, `COUNT(*)` doesn't — a common interview point.

### 11.4 Date filtering and performance

* **Prefer ranges** — `WHERE intake_date >= '2024-01-01' AND intake_date < '2025-01-01'` — over
  `WHERE YEAR(intake_date) = 2024`. Wrapping a column in a function stops the database using an index on it
  ("non-sargable").
* **Half-open ranges** (`<` the next day) are safe for datetime columns; `BETWEEN '2024-01-01' AND '2024-12-31'`
  misses times after midnight on 31 December.
* **Indexes:** for the matching and window queries, an index on `(animal_id, intake_datetime)` matches the
  `PARTITION BY … ORDER BY`. For Q5, indexes on `candidate_visits(intake_event_id)` and `(outcome_event_id)` make the
  lookups fast. In the SQLite check, the Q5 anti-join ran in 0.16 s with those indexes; without them it was still
  running after several minutes.
* **Other tips:** select only needed columns (not `SELECT *`); filter early; check the execution plan; avoid
  functions on join keys; pre-aggregate large tables before joining.

### 11.5 Likely SQL questions — short spoken answers

1. **"WHERE vs HAVING?"** — "WHERE filters rows before grouping; HAVING filters groups after aggregation — like keeping
   only groups with more than one row to find duplicates."
2. **"INNER vs LEFT JOIN?"** — "INNER keeps only matches; LEFT keeps everything on the left and fills NULLs where
   there's no match — that's how I'd find intakes without an outcome."
3. **"How do you remove duplicates?"** — "ROW_NUMBER partitioned by the columns that define a duplicate, then keep
   row number one. For exact duplicates, partition by every column."
4. **"What's a CTE and why use one?"** — "A named step inside a query, defined with WITH. It makes multi-step logic —
   like building an event timeline, then matching it — readable and testable."
5. **"LAG vs LEAD?"** — "LAG looks at the previous row in the window, LEAD at the next. I'd use LAG to find an animal's
   previous outcome and LEAD to find its next event."
6. **"ROW_NUMBER vs RANK vs DENSE_RANK?"** — "ROW_NUMBER always numbers uniquely; RANK gives ties the same number and
   skips; DENSE_RANK gives ties the same number without skipping."
7. **"How do you handle NULLs?"** — "Test with IS NULL, never equals NULL; COALESCE to supply a default for display;
   and remember COUNT(column) ignores NULLs and AVG ignores them too."
8. **"How would you calculate the median in SQL?"** — "PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY …). It's the same
   interpolation as PERCENTILE.INC in DAX."
9. **"How would you check your SQL output is right?"** — "Reconcile totals with the source, check keys are unique,
   check no impossible values like negative durations, and spot-check a few records by hand."
10. **"A query is slow — what do you do?"** — "Look at the execution plan, make sure filters and joins can use an
    index, avoid functions on indexed columns, select fewer columns, and pre-aggregate where possible."
11. **"Why not join intakes to outcomes on animal ID in SQL?"** — "Same reason as in Power BI: one animal has many
    intakes and outcomes, so the join multiplies rows. I'd build an ordered event timeline per animal and pair each
    intake with the next outcome using LEAD."
12. **"SQL vs DAX — when would you use each?"** — "SQL or Power Query for shaping and cleaning data before it loads;
    DAX for calculations that must respond to slicers and filters in the report."
