# Data Problems Discovered — Five-Minute Walkthrough

For the **5-minute "Data problems discovered"** slot (minutes 15–20 of the interview). Spoken script ≈ 700 words
(about 5 minutes). All numbers are from the audit outputs (`outputs/audit/`, `outputs/matching/`,
`docs/DATA_QUALITY_ISSUES.md`) and match the presentation.

**Three kinds of problem — keep them separate when you speak:**

| Type | Meaning | Examples |
|---|---|---|
| **Confirmed problems** | clearly wrong or misleading in the source; fixed in derived data | exact duplicates, the timestamp offset |
| **Ambiguous records** | could be right or wrong; flagged, not forced | 225 same-day time-reversed pairs, 45 animals whose pairing depends on the method |
| **Limitations** | information the source simply doesn't contain | foster dates, surrender reasons, field returns |

---

## 1. Five-minute speaking script

**[0:00 — Framing]**
"Before trusting any finding, I audited both files. The data was structurally clean — every date parsed and every
Animal ID had the same format — but there were six issues that could have changed the results if I'd handled them
carelessly. I'll go through each: what I found, how I handled it, and what would have gone wrong otherwise.

**[0:25 — 1. Exact duplicates]**
First, exact duplicates: rows identical in every column. I found thirty-six extra copies in intakes and twenty-six in
outcomes, by grouping on all twelve columns and counting. I removed the extra copies from the analysis, but kept them
flagged in the cleaned files for traceability. Records with the same animal and time but a different detail — for
example a different intake type — I did *not* delete, because they may be genuine corrections; I flagged them. If I'd
left the duplicates in, the same visit could be matched twice; if I'd deleted near-duplicates, I'd be throwing away
real information.

**[1:15 — 2. The timestamp offset]**
Second, 3,584 outcome timestamps had a "minus five hours" suffix, which looks like a time zone. But every one of them was
exactly midnight, and the suffix was minus five even in winter, when Austin is minus six. And the month-year column in
the file agreed with the plain clock time on every row. So it isn't a real time zone — it marks records where only the
date was recorded. I kept the clock time and stored the suffix as information only. Converting it would have moved those
outcomes to five in the morning and shifted some onto different dates.

**[2:00 — 3. Repeat Animal IDs]**
Third, and most important: Animal ID is not a visit ID. About thirteen and a half thousand animals appear more than
once, and one appears thirty-three times. If you join intakes to outcomes on Animal ID, every intake for that animal
pairs with every outcome — which inflates the counts and creates impossible, even negative, stays. So I rebuilt visits in
time order: each intake pairs with the animal's next outcome, unless the animal came in again first. I tested other
approaches — a simple sequence-number join produced 784 negative durations, and first-in-first-out matching created
overlapping visits for the same animal — and chose the rule that produced neither.

**[2:55 — 4. Unmatched records]**
Fourth, not everything pairs. 1,229 intakes have no matching outcome — mostly animals still in care when the data ends
in May 2025. 1,202 outcomes have no matching intake — mostly animals that came in before October 2013, when the data
starts. I kept these as rows with a clear status and reason instead of forcing matches, and they're excluded from
length of stay. Forcing them would create fake visits with wrong durations.

**[3:35 — 5. The 225 same-day pairs]**
Fifth, a genuinely ambiguous group: 225 cases where an outcome was logged a few hours *before* an intake for the same
animal on the same day. It's probably the order in which staff entered the records — the median gap is four hours —
but the data can't prove they're the same visit, and 37 of them look doubtful on review. So I left them out of the
confirmed matches and kept them in a separate, flagged list. Including them barely changes any result, which I checked.

**[4:15 — 6. Missing and inconsistent fields]**
Finally, field-level issues. Fifty-four percent of outcome subtypes are blank — but that's mostly by design: returns to
owner almost never have a subtype, while transfers always do — so I don't treat blanks as a category. Forty-six outcomes
have no outcome type, a handful of ages are negative, and thirty-three birth dates fall after the outcome date. I flagged
these rather than deleting the records.

**[4:40 — What the data can't tell us]**
And there are limits no cleaning can fix: foster placement dates, surrender reasons and field reunifications aren't
recorded. That's why I describe length of stay as time to the final recorded outcome, not time in a kennel."

---

# Data Quality — Simplified Interview Script

## **[0:00 — Introduction]**

"Before starting the analysis, I checked both datasets carefully.

Although the data was generally well-structured, I found six important issues that needed attention. I'll briefly explain what I found and how I handled each one."

## **[0:25 — 1. Duplicate Records]**

"First, I found duplicate records — 36 extra rows in the intake data and 26 in the outcome data.

I removed the extra copies from the analysis but kept them flagged for reference.

I also found some records with the same animal and timestamp but different details. I didn't delete those because they could be genuine corrections. I kept them flagged for review."

## **[1:15 — 2. Timestamp Issue]**

"Second, I found 3,584 outcome records with a minus-five-hour timestamp.

Initially, this looked like a time-zone issue. However, all these records were at midnight, and the timestamp pattern didn't match Austin's seasonal time changes.

So I treated it as a date-only recording pattern and retained the original clock time rather than converting it. Otherwise, some records could have shifted to a different time or date."

## **[2:00 — 3. Repeated Animal IDs]**

"Third, I found that the same Animal ID could appear multiple times. In fact, one animal appeared in as many as 33 intake records.

This means Animal ID alone cannot be used to connect an intake with an outcome, because it could match the wrong visits.

So I matched records chronologically. Each intake was connected to its next valid outcome, unless another intake occurred first.

This helped avoid incorrect matches and unrealistic Length of Stay calculations."

## **[2:55 — 4. Unmatched Records]**

"Fourth, some records could not be matched.

We had 1,229 intakes without a matching outcome and 1,202 outcomes without a matching intake.

This can happen because some animals were still in care when the dataset ended, while others had entered the shelter before our dataset started.

I kept these records separately with their status instead of forcing a match. They were excluded from Length of Stay calculations."

## **[3:35 — 5. Same-Day Matching Issues]**

"Fifth, I found 225 cases where the outcome was recorded a few hours before the intake on the same day.

These could be recording mistakes, but the data doesn't confirm that they belong to the same visit.

So I kept them separate and flagged them instead of treating them as confirmed matches."

## **[4:15 — 6. Missing and Inconsistent Fields]**

"Finally, I found some missing and inconsistent values.

For example, around 54% of outcome subtypes were blank. Most of these blanks were expected based on the type of outcome, so I didn't automatically treat them as errors.

I also flagged 46 outcomes with missing outcome types, some negative animal ages and 33 birth dates that were later than the outcome dates.

I retained these records rather than deleting potentially useful information."

## **[4:40 — Limitations and Closing]**

"Finally, there were some limitations in the available data.

We didn't have foster placement dates, reasons for owner surrender or records of field reunifications.

So, throughout the analysis, I refer to Length of Stay as the time between intake and the final recorded outcome, rather than claiming it represents actual time spent in the shelter."

---

## 2. Issue by issue (reference table)

| # | Issue | How identified | How handled | Why | Risk if mishandled |
|---|---|---|---|---|---|
| 1 | **Exact duplicate rows** — 36 intake, 26 outcome excess copies | group by all 12 source columns, count > 1 | excess copies excluded from analysis; flagged in cleaned files (173,776 and 173,749 events remain) | identical rows can't be two real events | double-counted events; one visit matched twice; FIFO/LIFO match counts changed by 35 when duplicates were removed |
| 1b | **Same Animal ID + timestamp, other fields differ** — 12 intake rows (6 pairs), 2 outcome rows (1 pair) | same ID and timestamp text, differing columns | kept and flagged | may be corrections; no basis to pick one | losing genuine information |
| 2 | **"-05:00" suffix on 3,584 outcome timestamps** | profiling timestamp formats; all offset rows at exactly 00:00:00; 884 in Nov–Feb when Austin is −06:00; `MonthYear` agrees with wall-clock time on 100% of rows | wall-clock time kept; suffix stored as metadata; midnight outcomes treated as "date only" | it marks date-only records, not a time zone | dates shifted by converting; same-day visits mis-ordered |
| 3 | **Repeat Animal IDs** — 13,487 animals with 2+ intakes; up to 33 | counting rows per Animal ID | visits rebuilt chronologically, one-to-one | Animal ID ≠ visit | row multiplication, wrong pairs, negative durations (rank join: 784) |
| 4 | **Unmatched records** — 1,229 intake-only, 1,202 outcome-only | records left over after matching, each with a reason | kept as rows with status and reason; excluded from LOS | data window cuts visits at both ends | fake visits with invented durations |
| 5 | **225 same-day time-reversed pairs** — outcome logged before a same-day intake | unmatched outcome + unmatched intake, same animal, same date, intake later | excluded from confirmed matches; flagged list; reviewed (188 plausible, 37 ambiguous) | data can't prove they are one visit | confirmed matches resting on an assumption; including them moves P90 LOS only 55.56 → 55.34 |
| 6 | **Field-level gaps** — outcome subtype 54.16% blank; 46 blank outcome types; 10 negative ages in each file; 33 birth dates after the outcome date | column profiling | kept and flagged; blanks not treated as a category | mostly structural; deletion would lose records | false categories; biased counts |
| 6b | **Categories change over time** — "Abandoned" first appears in 2020; "Euthanasia Request" ≤ 4 per year from 2018 | yearly counts by intake type | noted when comparing intake-type trends | coding changes, not behaviour | misreading a coding change as a real trend |

**Limitations (cannot be fixed from this data):** foster start/end dates · surrender reasons · field reunifications ·
outcomes before 01-10-2013 · official live-release formula · cause of the March 2020 drop.

---

## 3. Likely follow-up questions

1. **"How did you find the duplicates?"**
   "I grouped the raw file by all twelve columns and counted rows per group — any group with more than one row is an
   exact duplicate. In SQL that's a GROUP BY with HAVING COUNT(*) > 1."

2. **"Why didn't you delete the unmatched records?"**
   "Because they're real records with an explainable reason — still in care, or arrived before the data starts.
   Deleting them would hide that, and forcing a match would invent visits. They're kept with a status and excluded
   only from length of stay."

3. **"How do you know the offset isn't a real time zone?"**
   "Three checks: every offset row is exactly midnight; the offset is wrong for winter in Austin; and the file's own
   month-year column matches the plain clock time on every row."

4. **"Would including the 225 pairs change your findings?"**
   "No. I ran it both ways: the dog length-of-stay median, the owner-surrender share and the stray return-to-owner share
   all move by less than a twentieth of a percentage point, or a few hundredths of a day."

5. **"What's the biggest limitation?"**
   "Foster dates. Without them I can't separate shelter time from foster time, so I describe length of stay as time to
   the final recorded outcome — and I checked the dog finding on visits without a foster outcome, where it still holds."

6. **"Which issue mattered most?"**
   "Repeat Animal IDs. Every visit-level number — length of stay, outcome shares, the owner-surrender finding — depends on
   pairing the right intake with the right outcome."
