# Data Model and DAX — Five-Minute Walkthrough

For the **5-minute "Data model and DAX"** slot (minutes 10–15 of the interview). Spoken script ≈ 700 words
(about 5 minutes at a calm pace). Share **Model view** in Power BI Desktop while speaking, if possible.

* DAX below is copied exactly from `powerbi/dax/01_Core_Measures.dax` and `02_Time_Intelligence.dax`.
* In the submitted report, the LOS measures are named **Median / Average / P90 Intake-to-Outcome Days** in the
  `DAX_Measures` table; in the repository files they are **Median / Average / P90 LOS (Days)**. Same idea — check
  the formula in Desktop before quoting it as identical (the PBIX formulas were not readable from the repository).
* Expected values come from `outputs/powerbi/model_validation_summary.csv`.

---

## 1. The model in one picture (draw or describe it)

```text
                     DimDate (one row per day, 01-10-2013 → 05-05-2025)
                   /         |                    \              \ (inactive)
      intake_date /          | outcome_date        \ intake_date  \ outcome_date
                 v           v                      v              v
         FactIntakes     FactOutcomes            FactVisits ───────┘
      (1 row = 1 intake) (1 row = 1 outcome)   (1 row = 1 visit: intake + outcome,
                 ^           ^                    or intake-only / outcome-only)
                 |           |                      ^      ^
    DimAnimalType ───────────┴──────────────────────┘      |
    DimIntakeType ───────────────────────────────────── (intakes and visits only)
```

* Three **fact** tables (the things that happen), three **dimension** tables (how we slice them).
* Every arrow is **one-to-many**, **single direction**: the dimension filters the fact, never the reverse.
* No arrow between the fact tables, and nothing joins on `animal_id`.

| Table | Grain (what one row means) | Rows |
|---|---|---:|
| FactIntakes | one intake event, exact duplicates removed | 173,776 |
| FactOutcomes | one outcome event, exact duplicates removed | 173,749 |
| FactVisits | one candidate visit (matched, intake-only or outcome-only) | 174,978 |
| DimDate | one calendar day | 4,235 |
| DimAnimalType | one animal type | 5 |
| DimIntakeType | one intake type | 6 |

---

## 2. Five-minute speaking script

**[0:00 — Why a star schema]**
"The model is a star schema. In the middle I have fact tables — the events that happen — and around them,
dimension tables that describe them: date, animal type and intake type. I chose a star schema because it keeps
filters simple and predictable: each slicer sits on a dimension and flows in one direction into the facts.

**[0:30 — Three fact tables, three grains]**
I have three fact tables because the questions need three different levels of detail. FactIntakes has one row per
intake event — that's for volume questions, like how many animals came in each month. FactOutcomes has one row per
outcome event — how many adoptions or transfers happened. And FactVisits has one row per visit — an intake paired
with its outcome — and that's where length of stay lives. FactVisits also keeps the unmatched rows: about twelve
hundred intakes with no outcome and twelve hundred outcomes with no intake, each with a status.

**[1:15 — Why not Animal ID]**
I deliberately didn't relate the intake and outcome tables on Animal ID. Animal ID identifies the animal, not the
visit — one animal came in thirty-three times. A relationship on Animal ID would be many-to-many and would pair the
wrong intakes with the wrong outcomes. So the pairing is done once, during data preparation, and the model only
uses the result.

**[1:45 — Relationships and dates]**
All relationships are one-to-many and single-direction, from dimension to fact. The date table is the interesting
one. It has an active relationship to the intake date in FactIntakes, the outcome date in FactOutcomes, and the
intake date in FactVisits. A visit has two dates, but Power BI only allows one active relationship between two
tables, so the outcome-date relationship to FactVisits is inactive. When a measure needs it, I switch it on with
USERELATIONSHIP — for example, for unmatched outcomes, which have no intake date at all.

**[2:30 — Measures, not calculated columns]**
All my calculations are measures. A calculated column is worked out once per row when the data loads and stored
in the table. A measure is calculated at query time, inside whatever filters the visual has — so the same measure
gives the right answer for dogs, for 2019, or for strays. Row-level values like the length of stay in days were
prepared upstream in the data preparation, so I didn't need calculated columns in the model.

**[3:00 — CALCULATE and the matched-visit filter]**
The key function is CALCULATE. It evaluates an expression with a changed filter context. My median length of stay
is the MEDIAN of the length-of-stay column, wrapped in CALCULATE with a filter that keeps only matched visits. I
put that filter inside the measure, not just on the page, so the KPI can never accidentally include unmatched
rows. The average and the ninetieth percentile work the same way — median six days, average twenty-one, P90 about
fifty-five and a half — and the gap between them shows how skewed stays are.

**[3:45 — Year over year]**
For year-over-year, the previous-year measure uses SAMEPERIODLASTYEAR on the date table: whatever dates are
selected, it shifts them back a year and recounts intakes. Because 2013 and 2025 are partial years, the measure
first checks that both periods are complete inside the data; if not, it returns blank rather than a misleading
comparison. The percentage change uses DIVIDE, which returns blank instead of an error if the previous year is
zero.

**[4:20 — Slicers]**
Finally, slicers. A slicer on animal type filters the animal-type dimension, which filters all three fact tables,
so every visual updates together. The intake-type slicer filters intakes and visits — outcome events have no
intake type, so that relationship doesn't exist. And the date slicer means intake date for intake measures,
outcome date for outcome measures, and intake date for visit measures.

**[4:50 — Close]**
So: three grains, one-directional filters, no shortcut joins on Animal ID, and measures that carry their own
definitions."

---

# Data Model & DAX — Simplified Interview Script

## **[0:00 — Why I used a star schema]**

"I organised my data using something called a star schema.

In simple terms, I have three main tables that store the actual events, and supporting tables that describe things like dates, animal types and intake types.

I used this structure because it makes the data easier to organise and allows filters to work consistently across the report."

## **[0:30 — Three fact tables]**

"I created three main tables because each one serves a different purpose.

- FactIntakes stores one record for every intake event. I use it to analyse how many animals entered the shelter.
- FactOutcomes stores one record for every outcome event, such as adoption, transfer or return to owner.
- FactVisits connects an intake with its corresponding outcome. This is particularly important for calculating Length of Stay.

I also retained records that couldn't be matched, so we don't lose those records during the analysis."

## **[1:15 — Why I didn't join using Animal ID]**

"One important decision was not to directly connect intake and outcome records using Animal ID.

The reason is that the same animal can enter the shelter multiple times. In our data, one animal appeared in as many as 33 intake records.

So, simply joining on Animal ID could connect the wrong intake with the wrong outcome.

Instead, I matched the records chronologically during data preparation and used the resulting visit-level table in Power BI."

## **[1:45 — Relationships and dates]**

"I connected the supporting tables to the fact tables using one-to-many relationships.

For dates, there is one small detail. Each visit can have both an intake date and an outcome date.

Power BI allows one active relationship between these tables for this date dimension, so I kept the intake-date relationship active and the outcome-date relationship inactive.

When I need to analyse outcomes using the outcome date, I can activate that relationship inside a DAX calculation using a function called USERELATIONSHIP."

## **[2:30 — Measures vs. calculated columns]**

"For my calculations, I mainly used measures.

The difference is quite simple. A calculated column stores a value for each row when the data is loaded.

A measure calculates the result when the report is viewed, based on the filters selected.

For example, if I select Dogs or choose a particular year, the same measure recalculates based on that selection.

This is why measures were useful for my interactive dashboard."

## **[3:00 — CALCULATE and Length of Stay]**

"One of the important DAX functions I used is CALCULATE.

It allows me to calculate something under a particular condition or filter.

For example, when calculating median Length of Stay, I specifically tell Power BI to consider only matched visits. This ensures that unmatched records are not included in the calculation.

I applied the same approach to the average and 90th percentile.

The results were a median of 6 days, an average of 21.03 days and a 90th percentile of 55.56 days.

The difference between these values tells us that some visits have much longer durations than others."

## **[3:45 — Year-over-year calculation]**

"I also created a year-over-year calculation to understand how intake volumes changed compared with the previous year.

I used SAMEPERIODLASTYEAR to compare the selected period with the corresponding period in the previous year.

I also added checks to avoid misleading comparisons for incomplete years, such as 2013 and 2025.

For percentage calculations, I used DIVIDE because it handles cases where the previous year's value is zero without producing a division error."

## **[4:20 — How slicers work]**

"Finally, I connected the slicers to the data model.

For example, when I select Dogs, the animal type filter flows through the relationships and updates the relevant visuals.

The intake-type slicer works on intake and visit records. Outcome records don't have an intake type, so that filter doesn't directly apply to them.

Similarly, date filters work according to the date relevant to each table."

## **[4:50 — Closing]**

"So overall, I focused on keeping the model organised, avoiding incorrect record matching, and creating measures that respond correctly to the user's selections.

That is how I built the foundation for the interactive Power BI report."

---

## 3. The key DAX, line by line

### Total Intakes — counting rows

```dax
MEASURE FactIntakes[Total Intakes] =
    COUNTROWS ( FactIntakes )
```

* `COUNTROWS ( FactIntakes )` — counts the intake rows **that survive the current filters** (slicers, visual
  axis). Unfiltered: **173,776**.

### Matched Visits — CALCULATE with an explicit filter

```dax
MEASURE FactVisits[Matched Visits] =
    CALCULATE (
        COUNTROWS ( FactVisits ),
        KEEPFILTERS ( FactVisits[visit_status] = "Matched visit" )
    )
```

* `CALCULATE (` — evaluate the first argument under modified filters.
* `COUNTROWS ( FactVisits )` — count visit rows.
* `KEEPFILTERS ( FactVisits[visit_status] = "Matched visit" )` — add the condition "matched visits only" **on top
  of** existing filters (KEEPFILTERS intersects instead of overwriting a filter on the same column).
* Unfiltered: **172,547**.

### Median / Average / P90 LOS — aggregation inside CALCULATE

```dax
MEASURE FactVisits[Median LOS (Days)] =
    CALCULATE (
        MEDIAN ( FactVisits[los_days] ),
        KEEPFILTERS ( FactVisits[visit_status] = "Matched visit" )
    )

MEASURE FactVisits[Average LOS (Days)] =
    CALCULATE (
        AVERAGE ( FactVisits[los_days] ),
        KEEPFILTERS ( FactVisits[visit_status] = "Matched visit" )
    )

MEASURE FactVisits[P90 LOS (Days)] =
    CALCULATE (
        PERCENTILE.INC ( FactVisits[los_days], 0.9 ),
        KEEPFILTERS ( FactVisits[visit_status] = "Matched visit" )
    )
```

* `los_days` = intake to final recorded outcome, in days (prepared upstream; not kennel time).
* `MEDIAN` — middle value; robust to very long stays. **6.00** days.
* `AVERAGE` — pulled up by long stays. **21.03** days.
* `PERCENTILE.INC ( …, 0.9 )` — 90% of matched visits are at or below this value. **55.56** days.
* Same matched-visit filter in all three, so they always describe the same population.

### Unmatched Outcome Events — activating the inactive date relationship

```dax
MEASURE FactVisits[Unmatched Outcome Events] =
    CALCULATE (
        COUNTROWS ( FactVisits ),
        KEEPFILTERS ( FactVisits[visit_status] = "Outcome without matched intake" ),
        USERELATIONSHIP ( DimDate[Date], FactVisits[outcome_date] )
    )
```

* Outcome-only visit rows have **no intake date**, so the default (intake-date) relationship can't date them.
* `USERELATIONSHIP ( DimDate[Date], FactVisits[outcome_date] )` — for this measure only, filter visits by outcome
  date. Unfiltered: **1,202**.

### Share of Matched Visits Over 30 Days — DIVIDE

```dax
MEASURE FactVisits[Share of Matched Visits Over 30 Days] =
    DIVIDE ( [Visits Over 30 Days], [Matched Visits] )
```

* `DIVIDE ( a, b )` — `a / b`, but returns BLANK instead of an error when `b` is 0 or blank. **19.30%**.
* Builds on other measures: measures can reference measures.

### Year over year — SAMEPERIODLASTYEAR with a partial-year guard

```dax
MEASURE DAX_Measures[Total Intakes Previous Year] =
    VAR _first = MIN ( DimDate[Date] )
    VAR _last = MAX ( DimDate[Date] )
    VAR _extractStart = CALCULATE ( MIN ( DimDate[Date] ), REMOVEFILTERS ( DimDate ) )
    VAR _lastComplete =
        CALCULATE (
            MAX ( DimDate[Date] ),
            REMOVEFILTERS ( DimDate ),
            DimDate[Is Complete Extract Day] = TRUE ()
        )
    VAR _isComparable =
        NOT ISBLANK ( _first )
            && EDATE ( _first, -12 ) >= _extractStart
            && _last <= _lastComplete
    RETURN
        IF (
            _isComparable,
            CALCULATE ( [Total Intakes], REMOVEFILTERS ( DimDate ), SAMEPERIODLASTYEAR ( DimDate[Date] ) )
        )

MEASURE DAX_Measures[Total Intakes YoY Change] =
    VAR _py = [Total Intakes Previous Year]
    RETURN IF ( NOT ISBLANK ( _py ), [Total Intakes] - _py )

MEASURE DAX_Measures[Total Intakes YoY Change %] =
    DIVIDE ( [Total Intakes YoY Change], [Total Intakes Previous Year] )
```

* `VAR _first / _last` — first and last selected date (e.g. 01-01-2019 and 31-12-2019 for the year 2019).
* `_extractStart` — first date in the whole date table (01-10-2013); `REMOVEFILTERS ( DimDate )` ignores the
  current selection.
* `_lastComplete` — last complete day of data (04-05-2025).
* `_isComparable` — TRUE only if the same period a year earlier starts inside the data **and** the current period
  is complete. Years 2015–2024 pass; 2013, 2014 and 2025 do not.
* `SAMEPERIODLASTYEAR ( DimDate[Date] )` — shifts the selected dates back one year;
  `REMOVEFILTERS ( DimDate )` clears other date-table filters (such as Year = 2019) so the shifted dates apply.
* `YoY Change` — only calculated when a previous-year value exists.
* `YoY Change %` — `DIVIDE` avoids division-by-zero errors.
* Examples: 2019 = 19,726 vs 16,975 → **+16.2%**; 2020 = 9,585 vs 19,726 → **−51.4%**; 2013, 2014, 2025 → blank.

---

## 4. Row context vs filter context — the 20-second version

* **Filter context** — the set of filters a visual applies (slicer = Dog, axis = 2019). Measures are evaluated in
  it. *"Median LOS shows 5.99 for dogs because the slicer put Animal Type = Dog into the filter context."*
* **Row context** — "the current row", used by calculated columns and iterators such as `SUMX` that go row by row.
  *"My model doesn't need calculated columns: row-level values like `los_days` were prepared before loading."*
* **CALCULATE** — the function that changes filter context, and turns row context into filter context when used
  inside an iterator.

---

## 5. Five likely follow-up questions

1. **"Why three fact tables instead of one?"**
   "Because they answer different questions at different grains. Volume questions need one row per event; length of
   stay needs one row per visit. Keeping them separate means each measure counts exactly one kind of thing, with
   no risk of double-counting."

2. **"What's the difference between a measure and a calculated column?"**
   "A calculated column is computed per row at refresh and stored, so it uses memory and doesn't react to slicers. A
   measure is computed at query time in the current filter context. KPIs should be measures."

3. **"Why is one date relationship inactive?"**
   "A table can have only one active relationship to another. Visits have intake and outcome dates; intake date is the
   default so visits are analysed by intake cohort, and USERELATIONSHIP turns on the outcome date inside specific
   measures."

4. **"Why do you put the matched-visit filter inside the measure?"**
   "So the definition travels with the measure. If someone removes a page filter, the KPI still excludes unmatched
   rows. It also avoids the DAX trap where a blank value compares equal to zero."

5. **"Why does the YoY show blank for 2014 and 2025?"**
   "2025 only runs to early May, and 2014's previous year only starts in October 2013. Comparing them with full years
   would be misleading, so the measure returns blank; for 2025 I use a like-for-like window, January to 4 May,
   which shows intakes down 6.2% on 2024."
