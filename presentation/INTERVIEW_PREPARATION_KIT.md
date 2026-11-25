# Interview Preparation Kit — Austin Animal Center Analytics

Backup material for questions after the presentation. Keep these details **out** of the main talk unless asked.
Numbers are from the validated outputs (see `CLAUDE_PROJECT_KNOWLEDGE_KIT.md`, Appendix A). Answers are written to
be spoken in 20–40 seconds.

**Golden rules:** name the statistic and its denominator · say "pattern", not "cause" · LOS is time to the final
recorded outcome, not kennel time · the provisional outcome grouping is not the official live-release rate · the
findings are my recommendations, not approved by the director · be honest about what AI helped implement and what
you verified yourself.

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
