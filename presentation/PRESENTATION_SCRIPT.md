# Presentation Script — Austin Animal Center (10 minutes)

Aligned slide-by-slide with `website/index.html`. Target ≈ 10 minutes for the website (≈ 1,450 spoken words at
about 145 words per minute; rehearse with a timer). The Power BI Desktop demonstration is a **separate segment** — see
`presentation/POWER_BI_DEMO_PLAN.md`.

**Delivery notes**
* Words in *italics* are stage directions. Numbers are written as you should say them.
* Always name the statistic: "pooled median", "share of owner surrenders", "share of stray-dog visits".
* If time runs short, shorten slides 4, 5 and 9 — never the three findings.
* Press **N** on any slide for a one-line cue.

| Slide | Target | Cumulative |
|---|---:|---:|
| 1 Opening | 0:45 | 0:45 |
| 2 Director's questions | 0:50 | 1:35 |
| 3 Choosing the right problems | 1:15 | 2:50 |
| 4 Trustworthy foundation | 1:15 | 4:05 |
| 5 Analytical approach | 0:50 | 4:55 |
| 6 Finding 1 | 1:15 | 6:10 |
| 7 Finding 2 | 1:05 | 7:15 |
| 8 Finding 3 | 1:00 | 8:15 |
| 9 Context | 0:50 | 9:05 |
| 10 Recommendations | 0:55 | 10:00 |

---

## Slide 1 — Opening (0:45)

*Full screen on. Pause before speaking.*

"Thank you for having me. The brief put me in the role of analyst for an animal shelter, with one director's
question: how do animals come in, what happens to them, and where should we act?

I worked with eleven years of Austin Animal Center records — just over one hundred and seventy-three thousand
intakes and a similar number of outcomes. I rebuilt those records into individual shelter visits, which gave me
one hundred and seventy-two thousand five hundred matched visits, and then narrowed everything down to three
findings the shelter can actually act on.

In the next ten minutes I'll explain how I chose those three, why I trust the numbers behind them, and what I'd
recommend."

*Transition:* "Let me start with what the director actually asked."

## Slide 2 — The director's questions (0:50)

"The question breaks into three parts. How do animals come in — that's demand: volume, intake type and
season. What happens to them — adoption, return to owner, transfer — and I measured that per visit, not per
record. And where should we act — which patterns can the shelter actually influence?

I had two public datasets from the City of Austin: intakes and outcomes, running from October 2013 to May
2025. That means the first and last years are partial, which matters for any year-on-year comparison.

The brief also asked for a Power BI report, which I'll show afterwards. Today I want to focus on the third
question — where to act — because that's where the value is."

*Transition:* "There were many possible answers to that, so the first job was choosing well."

## Slide 3 — Choosing the right problems (1:15)

"Rather than start with charts, I listed fifteen candidate opportunities and scored each one from one to five on
six criteria — from business relevance and data reliability to whether the shelter can act on it and how safely
it can be interpreted.

*Point to the table.* The top eight are here. Owner-surrender patterns scored highest, at twenty-eight out of
thirty. Length of stay and return to owner were close behind.

I chose the final three — highlighted — because each one combines three things: evidence that holds up under
every test I ran, a lever the shelter controls, and a definition I can state in one sentence.

Just as important is what I left out: breed patterns, because the labels are visual guesses and risk
stigmatising animals; the official live-release rate, because I couldn't verify the City's formula; and the cause
of the 2020 drop, because the data shows when, not why.

These are my recommended findings for the director to consider — not something that has already been
approved."

*Transition:* "Before trusting any of these, I had to make sure the data could support them."

## Slide 4 — Building a trustworthy foundation (1:15)

"The original tables record events: an intake is one event, an outcome is another. The same animal can come in
and leave several times — one animal had thirty-three visits. So if you simply join intakes to outcomes on
Animal ID, you pair the wrong records and get nonsense durations.

*Walk the flow left to right.* I audited and cleaned the originals — removed exact duplicates, standardised dates
and data types, flagged quality issues rather than deleting them — and then reconstructed visits chronologically:
an intake is paired with that animal's next outcome, unless the animal was taken in again first.

The result is about one hundred and seventy-five thousand candidate visits, of which one hundred and seventy-two
thousand five hundred are matched. About twelve hundred intakes have no outcome yet — mostly animals still in care —
and about twelve hundred outcomes have no intake, mostly animals that arrived before 2013. I kept them rather than
forcing matches. And two hundred and twenty-five same-day cases that the data can't prove are one visit are left
out of the confirmed matches; including them barely changes anything."

*Transition:* "With visits in place, I fixed the definitions before looking at results."

## Slide 5 — Analytical approach (0:50)

"Two levels of analysis. Events answer volume questions — how many came in. Visits answer journey questions —
how long, and how it ended. I never divide one by the other and call it a conversion rate.

Length of stay is the time from intake to the final recorded outcome, for matched visits. I use medians because
stays are very skewed: the median is six days, but the ninetieth percentile is about fifty-five. And it's
important to say what it isn't: it's not confirmed kennel time, because foster periods aren't recorded.

For time comparisons I use complete years — a 2014-to-2019 baseline against recent years.

*Point to the bottom panel.* Each director question then maps to one finding: where is capacity going, why do
animals come back, and are lost dogs getting home?"

*Transition:* "Let's start with capacity."

## Slide 6 — Finding 1: Dog length of stay (1:15)

"Dogs now take more than twice as long to reach a final outcome. The pooled median for dogs taken in between 2014
and 2019 was five point one two days. For dogs taken in during 2023 and 2024 it's twelve point zero eight days.

A fair challenge is: is that just foster care? So I checked dog visits with no foster subtype on the outcome.
The median still rose — from four point nine five to eight point nine four days — and the share staying more than
thirty days went from under nine percent to about twenty-three percent.

Why it matters: intake fell by forty percent between 2019 and 2024, but the estimated number of animals between
intake and outcome fell by only eighteen percent. Longer stays are absorbing the space that lower intake should
have freed up.

My recommendation is a long-stay pathway for dogs: review every dog at day fourteen and day thirty with a named
placement plan, and track the share of dogs over thirty days every month.

What this doesn't tell us is why. That's the next piece of work — breaking long stays down by intake type, age and
outcome."

*Transition:* "The second finding is about animals coming back."

## Slide 7 — Finding 2: Owner surrender after adoption (1:05)

"Between 2016 and 2024 there were about twenty-seven thousand owner-surrender visits. In twenty-four point four
six percent of them, the animal's previous visit at this shelter had ended in adoption.

More striking is the timing. Fourteen point eight nine percent of all owner surrenders were animals adopted
within the previous thirty days, and eight point nine six percent within seven days. In other words, most of these
returns happen early.

The definition matters, so to be precise: it's an owner surrender where that animal's previous matched visit ended
in adoption, timed from the adoption to the surrender.

The recommendation follows from the timing: support adopters in the first thirty days — check-ins around day three
and day fourteen, behaviour support, and a conversation about alternatives before a surrender is accepted.

What I can't say is why these animals were surrendered — the reason isn't recorded. This shows where to focus,
not the cause."

*Transition:* "The third finding is about the fastest way out of the shelter."

## Slide 8 — Finding 3: Stray dog return to owner (1:00)

"Return to owner is the quickest outcome a shelter has: for dogs the median is under two days, and almost two-thirds
go home within three days.

But the share of stray-dog visits ending in return to owner has fallen from an average of twenty-nine point four
six percent between 2014 and 2019 to twelve point five one percent in 2024. In absolute terms, that's from about two
thousand dogs going home in 2019 to under four hundred in 2024.

The recommendation is to reunify at the door: scan every stray for a microchip at intake, post found dogs the same
day, check the quality of owner-contact data, and promote the City's free microchip and ID-tag service.

One important limitation: dogs that officers return to owners in the field never become an intake, so they're not
in this data. If field returns have grown, the shelter share would fall even if reunification overall hasn't. I'd
verify this against operational records before treating it as a performance measure."

*Transition:* "These findings sit inside a wider policy and welfare context."

## Slide 9 — Welfare, policy and environmental context (0:50)

"I've kept external context separate from what the data shows. *Left to right.*

State law sets shelter standards and, through the Safe Outdoor Dogs Act, requires shelter, shade and water for
dogs kept outside. City policy sets a stray hold of about three days and a ninety-five percent live-outcome
commitment that now excludes wildlife. The City Auditor reported in 2023 that the shelter often had to limit intake
for lack of space.

Our data connects to that: longer dog stays bear directly on space, and most wildlife intakes end in euthanasia for
rabies risk — consistent with bats and skunks being the main rabies sources in Texas. Heat may affect animals before
they arrive, but the data doesn't record it, so that stays a hypothesis."

*Transition:* "So what should the director do?"

## Slide 10 — Recommendations and conclusion (0:55)

"Three priorities, each with a baseline to measure against.

First, capacity: a long-stay pathway for dogs, tracked by the share of dogs over thirty days — currently about
twenty-three percent.

Second, prevention: support adopters in the first thirty days, tracked by the share of owner surrenders adopted
within the previous month — about fifteen percent.

Third, reunification: reunify at the door, tracked by the stray-dog return-to-owner share — twelve and a half
percent in 2024 — alongside field returns.

The limits I'd keep in view: length of stay isn't kennel time, surrender reasons and field returns aren't recorded,
and these are patterns, not proven causes. Recording foster dates, surrender reasons and field returns would turn
each of these into a precise operating measure.

*Pause.* So: three findings, three levers — get long-stay dogs moving, support adopters early, and get lost dogs home
faster.

Now let me show you the Power BI report, where the director can explore these patterns directly."

---

## Transition to the Power BI demonstration

*Press F to exit full screen. Switch to Power BI Desktop with `Austin_Animal_Center_Analytics_Final.pbix` already
open on the Executive Summary page.*

"This is the report I submitted. It has three pages: an executive summary with the three findings, a shelter overview
for demand and outcomes, and operational insights for length of stay and year-over-year trends. Let me walk you
through it."

*Follow `presentation/POWER_BI_DEMO_PLAN.md`. Afterwards:* "That's the report. I'm happy to take questions — on the
findings, the data preparation, or the model behind it."

## Short answers to keep ready

* **"Why not join on Animal ID?"** — "Animal ID identifies the animal, not the visit. One animal can have many
  intakes, so a direct join pairs the wrong records. I rebuilt visits chronologically instead."
* **"Is twelve days kennel time?"** — "No — it's time to the final recorded outcome. Foster time isn't recorded,
  which is why I also showed dogs with no foster outcome: the increase holds."
* **"Why 2014–2019 as the baseline?"** — "They're complete years before the 2020 disruption; 2013 is partial."
* **"Did the director approve these?"** — "They're my recommendations for the director to consider."
