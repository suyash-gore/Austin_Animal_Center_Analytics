# Power BI Live Demonstration Plan

**File:** `powerbi/Austin_Animal_Center_Analytics_Final.pbix` (submitted version; do not save changes during the
demo). **Length:** 4–5 minutes. **Order:** Executive Summary → Shelter Overview → Operational Insights.

Page contents below come from the PBIX report metadata in the repository (page names, visual titles, slicers and
fields). Click behaviour (cross-filtering, synced slicers) follows Power BI defaults and the candidate's own
Desktop checks; it has **not** been executed from the repository.

## Before the interview (5 minutes)

1. Open the PBIX in Power BI Desktop; wait for visuals to render. Do **not** press Refresh — the queries read local
   CSV files through the `RepoRoot` parameter; viewing does not need them.
2. Clear all slicers on both analytical pages (Date full range, Animal Type and Animal Intake Type = All).
3. Check the unfiltered card values against the validated outputs:

   | Measure on the cards | Expected |
   |---|---:|
   | Total Intakes | 173,776 |
   | Total Outcomes | 173,749 |
   | Matched Visits | 172,547 |
   | Median Intake-to-Outcome Days | 6.00 |
   | P90 Intake-to-Outcome Days | 55.56 |
   | Average Intake-to-Outcome Days | 21.03 |

4. Open the Executive Summary page. Close the Filters pane and the Fields pane for a cleaner view (View ribbon).
5. Decide which year to use for the YoY example: **2020** (intakes −51.4% vs 2019) and **2019** (+16.2%) are good;
   2013, 2014 and 2025 deliberately show blank YoY.

## 1. Executive Summary (≈ 45 s)

* **Show:** the three findings with recommended actions and the interpretation notes at the bottom.
* **Say:** "This is the director's landing page: the three findings from my presentation, each with an action, and
  the caveats underneath."
* **Click:** the *Shelter Overview* navigation button (Ctrl + click in Desktop editing mode).

## 2. Shelter Overview (≈ 1 min 45 s)

Visuals: four KPI cards; *Monthly Intake vs. Outcome Trends* (October 2013 – May 2025); *Intake Volume by Animal
Type*; *Outcome Distribution by Category*; slicers *Date*, *Animal Type*, *Animal Intake Type*.

1. **Cards** — "Intakes and outcomes are event counts after removing exact duplicates; matched visits are the
   reconstructed visits; the median is time from intake to final recorded outcome."
2. **Monthly trend** — point to the drop from March 2020 and the lower level afterwards. "The data shows when it
   happened, not why."
3. **Animal Type slicer → Dog.** All visuals update. "Every visual responds to the same slicers." (Slicers are synced
   with Operational Insights — the selection carries over.)
4. **Animal Intake Type slicer → Stray.** "Intake type comes from a shared intake-type dimension, so it filters intake
   events and visits together. Outcome events have no intake type, so the outcome visual is not filtered by it."
   *(Check this in rehearsal; if the outcome visual changes, say it is filtered through visits.)*
5. **Optional cross-filter:** click the *Dog* bar in *Intake Volume by Animal Type*; the other visuals highlight.
   Click again to clear.
6. Reset Intake Type to All; keep Dog selected for the next page.

## 3. Operational Insights (≈ 1 min 45 s)

Visuals: four KPI cards (Median, Average, P90 Intake-to-Outcome Days, Matched Visits); *Median Length of Stay by
Animal Type*; *Annual Intake Volume & Year-over-Year Change* (columns = intake volume, line = YoY %); note "LOS
represents matched intake-to-outcome duration; shelter and foster periods cannot be separated"; slicers *Date*,
*Animal Type*, *Animal Intake Type*.

1. **Cards** — "Median, average and ninetieth percentile: the gap between them shows how skewed stays are."
2. **Median Length of Stay by Animal Type** — "Length of stay is calculated per matched visit, as a measure, so it
   responds to every filter."
3. **Annual combo chart** — "Columns are intake volume; the line is year-over-year change. 2013, 2014 and 2025
   intentionally have no YoY value: 2013 and 2025 are partial years, and 2014's prior year is partial." Hover over
   2020 (≈ −51.4%).
4. **Date slicer** → restrict to 2023–2024 with Animal Type = Dog; the median card rises compared with the full
   range. "This is the recent dog cohort behind Finding 1." (The headline 5.12 → 12.08 days is a pooled median by
   intake-year cohort from the audit outputs; the card shows the median for whatever is filtered.)
5. Clear all slicers.

## Close (≈ 15 s)

"The report gives the director the overview, the operational detail and the three findings in one place, and every
number traces back to a documented, tested preparation pipeline. Happy to take questions."

## If something goes wrong

* **A visual shows an error after an accidental refresh** — close without saving and reopen the PBIX (data is stored
  in the file).
* **A card shows a different unfiltered value** — check for an active slicer or a visual-level filter first.
* **YoY shows blank for a year** — expected for 2013, 2014 and 2025 (partial comparison periods).
