# Business Opportunity Register

**Status:** Evidence assessed; ranking and director findings proposed for candidate approval
(DECISION_LOG D-001, Stage 3). **Code:** `analysis/explore_business_opportunities.py`.
**Scored register (machine-readable):** `outputs/analysis/business_opportunity_assessment.csv`.

## Ground rules applied

* Event counts (intake rows, outcome rows) and visit-level rates are reported separately. Visit-level
  shares use **primary matched visits** (172,547; D-018 excludes the 225 same-day time-reversed
  candidates) as the denominator; no intake-event percentage is compared with
  an outcome-event percentage.
* "Live outcome" is a provisional grouping (D-014), not the City of Austin live-release rate.
* Trends are descriptive. No cause is attributed to the 2020 break or any other change.
* Full calendar years 2014–2024 are compared; 2013 and 2025 only on like-for-like windows (D-015).
* Scores (1–5, higher = better) are analyst judgements recorded in code; the evidence text is generated
  from the outputs. *Interpretation safety* is the inverse of misinterpretation risk.

## Register

| Rank | Opportunity | Relevance | Availability | Reliability | Depth | Actionability | Interp. safety | Total /30 | Defensible KPI |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | Owner surrender patterns | 5 | 5 | 4 | 5 | 5 | 4 | **28** | Yes |
| 2 | Intake volume and seasonality | 4 | 5 | 5 | 4 | 4 | 4 | **26** | Yes |
| 3 | Adoption outcomes | 5 | 5 | 4 | 4 | 4 | 4 | **26** | Yes |
| 4 | Length of stay | 5 | 4 | 4 | 5 | 4 | 4 | **26** | Yes |
| 5 | Return-to-owner outcomes | 5 | 5 | 4 | 4 | 4 | 3 | **25** | Yes |
| 6 | Intake-to-outcome throughput | 5 | 4 | 4 | 4 | 4 | 3 | **24** | Yes |
| 7 | Stray animal intake patterns | 4 | 5 | 4 | 3 | 3 | 4 | **23** | Yes |
| 8 | Age-based outcome patterns | 4 | 5 | 4 | 3 | 3 | 4 | **23** | Yes |
| 9 | Repeat animal visits | 4 | 4 | 4 | 4 | 4 | 3 | 23 | Yes |
| 10 | Long-stay animals | 4 | 4 | 3 | 4 | 4 | 3 | 22 | Yes |
| 11 | Euthanasia patterns | 4 | 5 | 4 | 3 | 3 | 2 | 21 | Partial |
| 12 | Intake condition and welfare | 4 | 5 | 3 | 3 | 3 | 3 | 21 | Partial |
| 13 | Transfer dependency | 4 | 5 | 3 | 3 | 3 | 2 | 20 | Partial |
| 14 | Death and other non-live outcomes | 3 | 5 | 3 | 2 | 2 | 3 | 18 | Partial |
| 15 | Breed-level outcome patterns | 3 | 4 | 2 | 2 | 2 | 1 | 14 | No |

Ties at 23 are broken by register order; *Repeat animal visits* (rank 9) is largely captured by the
adoption-return evidence in rank 1.

## Evidence and limitations by opportunity

1. **Owner surrender patterns.** Verified in `outputs/sensitivity/owner_surrender_verification.csv`.
   *Definition:* an owner-surrender matched visit is an "adoption return" when the animal's immediately
   preceding matched visit at this shelter ended in Adoption; days are measured from that adoption's
   outcome timestamp to the surrender intake. Denominator = matched owner-surrender visits by intake year.
   * Any prior adoption (no time limit): 6,668 of 27,256 owner-surrender visits in 2016–2024 = **24.46%**.
   * Within 30 days of adoption: 4,058 = **14.89%** of owner surrenders (60.86% of the 2016–2024 returns).
   * Within 7 days of adoption: 2,441 = **8.96%** of owner surrenders (36.61% of the 2016–2024 returns).
   * Elapsed adoption-to-surrender time is checked to be ≥ 0 before the 7/30-day counts; 0 records fail.
   * The figures 37.21% (7 d) and 61.69% (30 d) in `adoption_return_timing.csv` are shares of *all* 8,065
     adoption returns, 2013–2025 (6,111 dogs, 1,921 cats), not of the 2016–2024 window; they are shares of
     returns, not of owner surrenders. Of all 9,157 return intakes classed as Owner Surrender, 8,065
     followed an adoption (`return_intake_previous_outcome.csv`).
   *Limitations:* adoptions before 01-10-2013 are invisible (2013–2015 biased low); surrender reasons
   are not recorded. *KPI:* % of adoptions returned as owner surrender within 30 days.
2. **Intake volume and seasonality.** Full-year intake events averaged 18,216 (2014–2019) and 11,643
   (2022–2024). Monthly year-over-year change was −2.0% (01-2020), +1.2% (02-2020), −41.2% (03-2020),
   −80.8% (04-2020); the largest 12-month level shift starts 03-2020. Seasonal index peaks in May
   (127.4) and troughs in February (77.7). *Limitations:* event counts; the break's cause is not in the
   data; category changes in 2020 (DQ-018). *KPI:* monthly intake events vs same month prior year.
3. **Adoption outcomes.** Adoption ends 48.64% of matched visits; owner-surrendered visits 66.5%,
   strays 48.4% (`visit_outcome_mix.csv`). Median LOS to adoption is 14.07 days. 15.0% of dog adoptions
   with a full year of follow-up re-enter within 365 days (`reentry_within_365d_by_outcome.csv`).
   *Limitation:* the Adoption/Foster subtype (21% of adoptions) indicates adoption by or via a foster;
   the date the animal entered foster is not recorded (methodology §7.1).
4. **Length of stay** (intake to final recorded outcome). Median 6.00 days (primary matched visits). Dog
   intake cohorts: median 5.12 days (2014–2019 average) vs 12.38 days (2023–2024); excluding
   foster-subtype outcomes, the share of dog visits over 30 days rose from 8.68% to 22.61%
   (`los_trend_by_intake_year.csv`). Both baselines are the
   unweighted average of annual cohort values; pooled equivalents are in
   `outputs/sensitivity/scenario_comparison.csv` (see Finding 1). Cats: median 6.14 vs
   10.20 days, non-foster > 30 days 15.31% vs 17.61%. *Limitations:* time in foster is not recorded, so
   LOS is custody time of unknown composition, not kennel time; recent
   cohorts mildly right-censored (which would understate the rise). *KPI:* median LOS and % > 30 days
   per intake cohort.
5. **Return-to-owner outcomes.** Stray-dog visits ending in RTO: 29.46% (2014–2019 average) vs 12.51%
   (2024); absolute stray-dog RTO visits 2,036 (2019) vs 386 (2024) (`stray_rto_by_year.csv`). RTO is the
   fastest outcome — dogs median 1.82 days, 63.5% within 3 days (`rto_timing.csv`).
   *Limitations:* reunifications made in the field without an intake are not in the data, so a falling
   share can reflect a different mix of animals reaching the shelter. *KPI:* RTO % of stray visits.
6. **Intake-to-outcome throughput.** Estimated average daily in-care population from matched visits:
   1,120 (2019) vs 916 (2024) (−18%), while intake events fell from 19,726 to 11,815 (−40%)
   (`annual_census_estimate.csv`). The population fell far less than intake because animals stay longer.
   *Limitation:* estimate of animals between intake and final outcome (location — shelter or foster — not
   recorded); open stays excluded — not a kennel count.
7. **Stray animal intake patterns.** Stray is 68.56% of intake rows; 15.64% of stray visits end in RTO.
   *Limitation:* Found Location is free text (70,183 values); geographic targeting needs geocoding.
8. **Age-based outcome patterns.** Adoption share is 70.7% for animals aged 1–5 months vs 32.2% for 7+
   years; RTO 38.7% for 7+ years; 7+ year visits have P90 LOS 63.0 days vs 44.2 for 1–5 months
   (`visit_outcome_mix.csv`, `los_by_segment.csv`). *Limitation:* ages are estimates.
9. **Repeat animal visits.** 10.06% of intake events are a repeat intake; Owner Surrender 25.94%, Stray
   5.39% (`repeat_intakes_by_type.csv`).
10. **Long-stay animals.** 7,777 visits > 90 days, 577 > 365 days; of 365+ day visits 77.1% are dogs,
    41.8% owner surrenders and 75.2% end with a foster subtype (`long_stay_profile.csv`,
    `long_stay_visits_365plus.csv`). Whether those animals spent the stay in foster is not recorded, so
    "long-stay kennel animals" cannot be identified reliably from this extract.
11. **Euthanasia patterns.** 6.22% of matched visits; 42.98% of euthanasia visits are wildlife (Other)
    with subtype Rabies Risk; dog/cat euthanasia share 5.94% (2014 intake cohort) vs 2.36% (2024).
    Dog euthanasia subtypes: Suffering 47.04%, Aggressive 27.19% (`euthanasia_subtype_by_animal.csv`).
    *Risk:* sensitive; must follow official definitions before any rate is quoted.
12. **Intake condition and welfare.** 15.25% of matched visits had a non-Normal condition; Sick visits end
    in euthanasia 32.0% and Injured 25.5% (vs 3.6% Normal). *Limitation:* overlapping labels (DQ-019).
13. **Transfer dependency.** Transfer ends 28.03% of matched visits, but 27.42% of cat transfers are
    Snr/SCRP community-cat return, not partner placements (`transfer_subtype_by_animal.csv`). Partner
    identity is absent. *Risk:* "dependency" easily overstated.
14. **Death and other non-live outcomes.** Died 1,645 and Disposal 868 matched visits; Disposal is
    undefined, and 582 of 876 Disposal outcome events (66%) are animal type Other. Small counts limit analysis.
15. **Breed-level patterns.** 3,006 labels, 69.31% mixes/slash; 41 labels with ≥ 500 visits
    (`breed_outcomes_min500.csv`). Not recommended: unreliable visual identification and stigma risk.

## Top eight (internal)

Owner surrender / adoption returns · Intake volume and seasonality · Adoption outcomes · Length of stay ·
Return-to-owner · Throughput / in-care population · Stray intake patterns · Age-based outcomes.

## Three strongest candidate findings for the director

Each finding is descriptive, reproducible from the outputs named, and paired with an action the
director controls. Approval pending (Stage 3).

### Finding 1 — Dogs now take more than twice as long to reach a final outcome, which keeps capacity tied up despite fewer intakes

* Median time from intake to final recorded outcome for dogs rose from 5.12 days (2014–2019 intake
  cohorts) to 12.38 days (2023–2024). For dog visits whose outcome has no foster subtype, the median rose
  from 4.95 to 8.94 days (pooled) and the share lasting more than 30 days from 8.68% to 22.61%.
* *What LOS means here:* elapsed time to the final outcome. Foster placement dates are not recorded, so
  the data cannot say how much of this time was spent in the shelter versus in foster care (methodology
  §7.1). The non-foster-subtype figures are the closest available proxy for on-site stays, not a measure of it.
* *Calculation (verified, `outputs/sensitivity/dog_los_verification.csv`):* cohorts are by **intake year**;
  5.12 / 12.38 are the **unweighted average of annual medians** (pooled medians: 5.12 → 12.08). The 30-day
  shares are averages of annual shares rounded per year (unrounded 8.69 → 22.61; pooled 8.67 → 22.58).
  Foster-subtype outcomes are 13–16% of 2023–2024 dog visits. Cohort completeness: 0.26% (2023) and
  2.37% (2024) of dog intakes have no accepted outcome; they are open stays, so the 2024 median is, if
  anything, understated.
* *Sensitivity:* including the 225 time-reversed candidates gives 5.12 → 12.35 days and 8.66% → 22.55%
  (pooled); strict timestamps give 5.13 → 12.39. The finding does not depend on these assumptions.
* Intake events are ~36% below the 2014–2019 level, yet the estimated in-care population fell only 18%
  (1,120 → 916 average per day, 2019 → 2024).
* **Action:** manage dog length of stay actively — review every dog at day 14 and day 30 with a
  placement plan (adoption promotion, foster, partner transfer); track "% of dogs > 30 days" monthly.
* **Caveats:** custody time to final outcome, of unknown shelter/foster composition; the cause of the
  increase is not established.

### Finding 2 — One in seven owner surrenders is an animal adopted from this shelter in the previous 30 days

**Director headline:** "In 2016–2024, 14.9% of owner surrenders were animals we had adopted out within the
previous 30 days, and 24.5% had been adopted from us at some earlier point."

* Any prior adoption at this shelter: 24.46% of owner-surrender visits (6,668 of 27,256, 2016–2024).
* Within 30 days of the adoption: 14.89% of owner surrenders (4,058); within 7 days: 8.96% (2,441).
* Of the 2016–2024 adoption returns, 60.86% came back within 30 days and 36.61% within 7 days.
* Elapsed times verified non-negative (0 records excluded).
* *Sensitivity:* 24.45–24.49% and 14.87–14.90% across all matching scenarios.
* **Action:** post-adoption support concentrated in the first 30 days (day-3 and day-14 check-ins,
  behaviour helpline, return-prevention counselling before a surrender is accepted); track the 30-day
  adoption-return rate.
* **Caveats:** surrender reasons are not recorded; adoptions before the extract are invisible.

### Finding 3 — Fewer stray dogs are going home to their owners

* The share of stray-dog visits ending in return to owner fell from 29.46% (2014–2019 average) to
  12.51% (2024); stray-dog RTO visits fell from 2,036 (2019) to 386 (2024).
* RTO is the shortest path out of the shelter (dogs: median 1.82 days, 63.5% within 3 days), so each
  reunification frees capacity quickly.
* **Action:** strengthen reunification — microchip and ID-tag every dog at outcome, scan and post
  found dogs on intake day, and measure RTO % of stray dogs alongside field returns.
* *Calculation:* 29.46% is the unweighted average of annual intake-cohort shares rounded per year
  (unrounded 29.47%, pooled 29.43%); denominator = primary matched stray-dog visits. *Sensitivity:*
  29.47–29.50% and 12.48–12.51% (2024) across all matching scenarios.
* **Caveats:** field returns without an intake are not in the data; the share may partly reflect which
  dogs reach the shelter. Verify against operational records before presenting as performance.

## Not recommended as director findings

* Breed patterns (stigma, unreliable labels); live-release rate (definition unverified); transfer
  dependency (category mixes partner transfer and community-cat return); attributing the 2020 break to
  any cause.
