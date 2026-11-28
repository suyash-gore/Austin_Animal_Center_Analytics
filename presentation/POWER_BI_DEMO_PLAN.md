# Power BI — Live Report Plan and Practice Exercises

**Interview format (confirmed):** Thursday 26-11-2026, 19:00 IST, 45–50 minutes. First 20 minutes: report and
findings (10) · data model and DAX (5) · data problems (5). Then Power BI and SQL questions with **live changes to
the report while screen-sharing**. There is **no separate mandatory demo segment** — use the report when a question
calls for it, and use the exercises below to practise the live changes.

**Report:** `powerbi/Austin_Animal_Center_Analytics_Final.pbix` (submitted). Three pages: **Executive Summary**,
**Shelter Overview**, **Operational Insights**.

**What is verified and what isn't.** Page names, visual titles, slicers and the fields/measures used come from the
PBIX report metadata in the repository. Click paths and on-screen behaviour below follow standard Power BI Desktop
behaviour but have **not** been executed from the repository — rehearse each exercise once in Desktop. Menu labels
can differ slightly between Desktop versions.

---

## 1. Safeguards (read first)

1. **Never practise on, or save over, the submitted PBIX.**
2. Tonight, in File Explorer, copy the submitted file twice:
   * `Austin_Animal_Center_Analytics_PRACTICE.pbix` — for rehearsing the exercises (break it freely).
   * `Austin_Animal_Center_Analytics_INTERVIEW.pbix` — an untouched copy to open and edit during the interview.
3. In the interview, open the **INTERVIEW** copy. If asked, say: "This is a copy of the submitted file, so I can make
   changes without touching the version I sent you."
4. Make only **report-level** changes live: titles, filters, slicers, new cards, new temporary measures, interactions.
   **Do not** change relationships, Power Query steps, data types or existing measures during the interview, and do
   **not** press *Refresh* (the queries read local CSVs through the `RepoRoot` parameter; viewing doesn't need them).
5. Undo is **Ctrl + Z**. If anything goes wrong: close **without saving** and reopen the INTERVIEW copy.

---

## 2. Pre-interview checklist (15 minutes before)

- [ ] Power BI Desktop updated and opened; the INTERVIEW copy open; visuals fully rendered.
- [ ] Notifications off; other windows closed; screen resolution and zoom comfortable for sharing.
- [ ] On **Shelter Overview** and **Operational Insights**: clear every slicer (eraser icon on each slicer header) —
      Date = full range, Animal Type = All, Animal Intake Type = All.
- [ ] Unfiltered card values match the validated outputs:

  | Measure | Expected |
  |---|---:|
  | Total Intakes | 173,776 |
  | Total Outcomes | 173,749 |
  | Matched Visits | 172,547 |
  | Median Intake-to-Outcome Days | 6.00 |
  | Average Intake-to-Outcome Days | 21.03 |
  | P90 Intake-to-Outcome Days | 55.56 |

- [ ] *Annual Intake Volume & Year-over-Year Change* shows blank YoY for 2013, 2014 and 2025; 2019 ≈ +16.2%,
      2020 ≈ −51.4%.
- [ ] Filters pane and Data pane visible (View ribbon) — you will need them for live changes.
- [ ] Start on the **Executive Summary** page. Website open in a browser tab for the first 10 minutes.

---

## 3. If asked to show the report (optional, ≈ 2 minutes)

1. **Executive Summary** — "The director's landing page: three findings, actions and caveats." Ctrl + click the
   *Shelter Overview* button.
2. **Shelter Overview** — cards (event counts and matched visits); *Monthly Intake vs. Outcome Trends* (drop from
   March 2020); *Intake Volume by Animal Type*; *Outcome Distribution by Category*; slicers Date, Animal Type, Animal
   Intake Type. Set Animal Type = Dog: "every visual responds; the slicer is synced to the next page."
3. **Operational Insights** — Median / Average / P90 Intake-to-Outcome Days; *Median Length of Stay by Animal Type*;
   *Annual Intake Volume & Year-over-Year Change* — "blank YoY for partial comparison years by design." Note on the
   page: LOS is matched intake-to-outcome duration; shelter and foster periods can't be separated.
4. Clear the slicers again.

---


## **3. If asked to show the report (optional, ≈ 3–4 minutes)**

1. **Executive Summary** — Start with the director's landing page, highlighting the three key findings, recommended actions and interpretation caveats.

   - **Dog Length of Stay:** The median intake-to-final-recorded-outcome duration increased from 5.12 days (historical period) to 12.08 days (recent period), indicating that dogs are spending longer between intake and their final recorded outcome.
   - **Owner Surrender:** 24.46% of owner-surrender visits had a previous shelter adoption record. Of these, 14.89% occurred within 30 days and 8.96% within 7 days, highlighting an opportunity to explore post-adoption support.
   - **Stray Dog Return-to-Owner:** The recorded return-to-owner share declined from 29.46% (2014–2019 average) to 12.51% in 2024, indicating a need to review identification, microchip scanning and owner-contact processes.

   Ctrl + click the **Shelter Overview** button.

2. **Shelter Overview** — Explain the four KPI cards and three charts.

   - **Total Intakes (173,776):** Total recorded intake events during the analysis period.
   - **Total Outcomes (173,749):** Total recorded outcome events. These are separate events and do not necessarily represent the same visits.
   - **Matched Visits (172,547):** Intake events successfully paired with their corresponding subsequent outcome events.
   - **Median Intake-to-Outcome Days (6.00):** Half of the matched visits had a recorded duration of six days or less.
   - **Monthly Intake vs. Outcome Trends:** Compares monthly intake and outcome volumes. The chart shows a significant disruption around March 2020, followed by changes in shelter activity.
   - **Intake Volume by Animal Type:** Dogs and cats account for the majority of intake events, with dogs contributing the largest share.
   - **Outcome Distribution by Category:** Adoption is the largest recorded outcome category, followed by transfer and return to owner.

   Briefly demonstrate the Date, Animal Type and Animal Intake Type slicers. Select Dog under Animal Type to show how the report responds. Explain that slicers allow users to explore patterns across different categories.

3. **Operational Insights** — Explain the duration measures and operational trends.

   - **Matched Visits (172,547):** The matched population used for the intake-to-outcome duration analysis.
   - **Median LOS (6.00 days):** Represents the typical matched intake-to-outcome duration and is less affected by unusually long stays.
   - **Average LOS (21.03 days):** The higher average compared with the median indicates a right-skewed distribution, with some visits having considerably longer durations.
   - **90th Percentile LOS (55.56 days):** 90% of matched visits had an intake-to-outcome duration of approximately 55.56 days or less. This helps identify the longer-stay tail.
   - **Annual Intake Volume & Year-over-Year Change:** Shows annual intake volumes and percentage changes from the previous year. The sharp decline in 2020 and subsequent increase in 2021 highlight major changes in shelter activity. 2025 is a partial year, so it should not be directly compared with complete years.
   - **Median Length of Stay by Animal Type:** Livestock has the highest median duration (19.9 days), followed by cats (7.2 days), dogs (6.0 days), birds (4.1 days) and other animals (0.7 days). This suggests that operational requirements may differ across animal categories.

   Highlight the interpretation note: LOS represents matched intake-to-final-recorded-outcome duration; shelter and foster periods cannot be separated using the available data.

4. **Clear all slicers and cross-filter selections** before finishing, so the report returns to its original unfiltered state.


---

## 4. Live Power BI Practice Exercises

Practise each on the **PRACTICE** copy, then undo. For each: *where to click → what to change → expected result →
what to say → how to undo.*

### Exercise 1 — Change a visual title

* **Where:** Shelter Overview → click *Monthly Intake vs. Outcome Trends* → **Format visual** (paintbrush icon in the
  Visualizations pane) → **General** → **Title** → **Text**.
* **Change:** type `Monthly Intake vs Outcome Events (Oct 2013 – May 2025)`.
* **Expect:** the chart title updates immediately.
* **Say:** "Titles are formatting only — the data and measures don't change. I'd make the title say exactly what the
  chart counts, here events rather than visits."
* **Undo:** Ctrl + Z, or retype the original title *Monthly Intake vs. Outcome Trends*.

### Exercise 2 — Apply and remove a visual-level filter

* **Where:** click *Outcome Distribution by Category* → **Filters** pane → **Filters on this visual** → drag
  **DimAnimalType → Animal Type** into the well (or expand it if already listed).
* **Change:** Basic filtering → tick **Cat**.
* **Expect:** only that visual changes to cats; the other visuals and the cards stay unchanged.
* **Say:** "There are three filter levels: visual, page and report. A visual-level filter affects just this chart,
  unlike the slicer, which filters the whole page."
* **Undo:** click the eraser on that filter card (clear) or the **×** (remove it from the visual).

### Exercise 3 — Change slicer selections and explain the effect

* **Where:** Shelter Overview → **Animal Type** slicer → choose **Dog**; then **Animal Intake Type** → **Stray**.
* **Expect:** all visuals on the page update; the selection is synced to Operational Insights (check by switching
  page).
* **Say:** "The slicer filters the Animal Type dimension, which filters all three fact tables through one-to-many,
  single-direction relationships. Intake type filters intakes and visits; outcome events don't have an intake type,
  so outcome-event visuals don't respond to that slicer."
  *(Rehearse: note which visuals change with Intake Type and adjust the sentence to what you see.)*
* **Undo:** eraser icon on each slicer header (Clear selections).

### Exercise 4 — Add a Card visual using an existing measure

* **Where:** click an empty area of the canvas (so nothing is selected) → **Visualizations** pane → **Card** →
  from the **Data** pane, expand **DAX_Measures** → tick **Total Outcomes**.
* **Expect:** a new card showing **173,749** when no slicers are applied (fewer if slicers are active).
* **Say:** "A card shows a single measure. It respects the page's slicers because the measure is evaluated in the
  current filter context."
* **Undo:** select the new card → **Delete**.

### Exercise 5 — Create a simple temporary measure

* **Where:** **Data** pane → right-click **DAX_Measures** → **New measure** → type in the formula bar:

```dax
Practice Dog Intakes =
CALCULATE ( [Total Intakes], DimAnimalType[Animal Type] = "Dog" )
```

* Press **Enter**, then add it to a new Card (as in Exercise 4).
* **Expect:** **94,588** with no slicers (dog intake events after duplicate removal).
* **Then demonstrate filter context:** set the Animal Type slicer to **Cat** — the card **still shows 94,588**.
  "CALCULATE replaced the Animal Type filter from the slicer with Dog. If I wanted the slicer to still apply, I'd
  wrap the condition in KEEPFILTERS — then selecting Cat would give blank."
* **Undo:** Data pane → right-click **Practice Dog Intakes** → **Delete from model**; delete the card.

### Exercise 6 — A basic measure modification

Don't edit production measures live. Modify the **practice** measure instead (or duplicate a measure first).

* **Where:** right-click **Practice Dog Intakes** → **New measure** (or select it and edit in the formula bar).
* **Change (a share):**

```dax
Practice Dog Share of Intakes =
DIVIDE ( [Practice Dog Intakes], [Total Intakes] )
```

* Then **Measure tools** ribbon → **Format** → **Percentage**, **1** decimal place.
* **Expect:** **54.4%** with no slicers (94,588 ÷ 173,776).
* **Say:** "DIVIDE is safer than the slash operator — it returns blank instead of an error if the denominator is zero.
  Measures can reference other measures, so the definition stays in one place."
* **Variation if asked:** change `"Dog"` to `"Cat"` in Practice Dog Intakes and watch every dependent measure update.
* **Undo:** delete both practice measures (dependent measure first) and any cards using them.

### Exercise 7 — Visual interactions and filter context

* **Cross-filtering:** on Shelter Overview, click the **Dog** bar in *Intake Volume by Animal Type*.
  **Expect:** the other visuals filter or highlight to dogs. **Say:** "Clicking a data point adds it to the filter
  context of the other visuals — like a temporary slicer." Click the bar again (or empty space) to clear.
* **Edit interactions:** select *Intake Volume by Animal Type* → **Format** ribbon → **Edit interactions** → on
  *Monthly Intake vs. Outcome Trends* click the **None** icon (circle with a line).
  **Expect:** clicking a bar no longer affects the trend chart. **Say:** "Interactions control how visuals filter each
  other — filter, highlight or none."
* **Undo:** in Edit interactions, set the trend chart back to its original icon (filter or highlight, whichever it was
  — note it before changing), then click **Edit interactions** again to turn the mode off.

---

## 5. Quick answers while editing

* **"What's the filter context of this card?"** — "Every active slicer, visual filter, page and report filter, plus
  any cross-filter selection. The measure is calculated inside that."
* **"Measure or calculated column?"** — "Measure — it has to respond to slicers. A calculated column is fixed per row
  at refresh."
* **"Why did the card not change when I changed the slicer?"** — "Because CALCULATE overrides that column's filter
  (Exercise 5), or the visual isn't related to the sliced table, or interactions are set to None."
* **"How would you add a new slicer?"** — "Select an empty area, choose the Slicer visual, drag a dimension column —
  e.g. DimDate Year — then sync it to other pages with View → Sync slicers if needed."

## 6. If something goes wrong

* **A visual shows an error after an accidental refresh** — close without saving and reopen the INTERVIEW copy.
* **A card shows an unexpected value** — check slicers, the Filters pane and any cross-filter selection first.
* **YoY is blank for a year** — expected for 2013, 2014 and 2025 (partial comparison periods).
* **You can't find a field** — use the search box at the top of the Data pane.
