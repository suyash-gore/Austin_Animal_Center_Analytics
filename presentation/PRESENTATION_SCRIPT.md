# Austin Animal Center Analytics — Presentation Script

**Target duration:** Approximately 9–10 minutes  
**Power BI demonstration:** Separate 4–5 minute segment

## Slide 1 — Opening

*Open the presentation in full screen. Pause briefly before starting.*

"Good morning, and thank you for giving me this opportunity.

For this assignment, I approached the problem from the perspective of an analyst working with an animal shelter.

The main question I wanted to answer was quite simple: how do animals enter the shelter, what happens to them afterwards, and where can the shelter take action to improve things?

I worked with more than eleven years of Austin Animal Center intake and outcome records. But rather than just building charts around the available data, I wanted to understand the patterns behind it and identify areas where the findings could actually help the shelter.

I eventually narrowed the analysis down to three key findings. I'll take you through how I selected them, what I discovered, and what I would recommend."

*Transition:* "Let me start with the problem I was trying to solve."

## Slide 2 — Understanding the director's questions

"I broke the director's question into three parts.

First, how are animals coming into the shelter? This includes the number of animals, the type of intake and how that changes over time.

Second, what happens after they arrive? Are they adopted, returned to their owners, transferred, or do they have another outcome?

And finally, where should the shelter focus its attention? Which patterns are important enough to take action on?

The two main datasets I received were intake records and outcome records from the City of Austin, covering October 2013 to May 2025.

I treated these as two parts of the same animal journey. That distinction became particularly important when I started working with the data."

*Transition:* "There were quite a few questions I could explore, so I first had to decide which ones were worth pursuing."

## Slide 3 — Choosing the right problems

"I didn't want to start by making charts for every available column. I wanted to identify questions that were relevant to the shelter.

So I listed fifteen possible areas of analysis and scored them using six criteria. These included business relevance, data availability, data reliability, whether I could analyse the question properly, whether the shelter could act on the result, and whether the findings could be interpreted safely.

Owner surrender came out on top, with twenty-eight out of thirty.

Length of stay and adoption patterns also scored highly, followed by return to owner.

From these opportunities, I selected three findings that I felt had a strong combination of evidence and practical value.

I also deliberately avoided a few areas. For example, I didn't want to draw conclusions from breed labels that could be unreliable. I also avoided claiming an official live-release rate because I couldn't verify the City's exact calculation.

The idea was not to find the most interesting chart. It was to find something the shelter could actually use."

*Transition:* "Before I could trust any of those findings, I had to make sure I was working with the right records."

## Slide 4 — Building a trustworthy data foundation

"This was one of the most important parts of the project.

The original files record individual events. One file records an intake, and the other records an outcome.

But here's the challenge: the same animal can enter the shelter more than once. So Animal ID tells us which animal we're looking at, but it doesn't necessarily tell us which visit we're looking at.

If I simply joined the two files using Animal ID, I could accidentally connect one intake to the wrong outcome.

To avoid that, I first checked the data, removed exact duplicate records, standardised dates and data types, and reviewed unusual records.

Then I matched the records in chronological order. In simple terms, I looked for the next valid outcome for each intake, unless another intake had already happened in between.

This gave me around 175,000 candidate visits, of which about 172,500 could be matched.

I kept unmatched records rather than forcing them into a visit. Some animals had no recorded outcome by the end of the dataset, while some outcomes had no intake in the available period.

There were also 225 same-day cases where the records did not give enough information to confirm the correct order. I kept those out of the confirmed matches.

This gave me a much more reliable basis for analysing individual animal journeys."

*Transition:* "Once I had the visits, I could define the measures and start looking for patterns."

## Slide 5 — How I approached the analysis

"I looked at the data in two ways.

The first was at the event level. This helped me understand how many animals were coming in and how those numbers changed.

The second was at the visit level. This helped me understand what happened during an individual stay.

One important measure was length of stay. I calculated the time between an animal's intake and its final recorded outcome, using matched visits.

I used the median as an important measure because some animals have very long stays, which can pull up the average.

There is also one limitation worth mentioning: this is not necessarily the time an animal spent in a physical kennel. The data doesn't give us separate start and end dates for foster care.

With those definitions in place, I moved on to the three findings."

*Transition:* "The first one was about how long dogs are taking to reach an outcome."

## Slide 6 — Finding 1: Dog length of stay

"What stood out to me was the increase in the time dogs spend between intake and their final recorded outcome.

For the earlier period, 2014 to 2019, the pooled median was 5.12 days.

For 2023 and 2024, it had increased to 12.08 days.

That's more than double.

I also wanted to check whether foster placements might be influencing this result. So I looked separately at dog visits without a foster outcome subtype. The median still increased, from 4.95 to 8.94 days.

This suggests that the longer stays are not explained by that factor alone.

Why does this matter? Longer stays can put pressure on available space, even when intake numbers are lower.

My recommendation would be to introduce regular long-stay reviews for dogs, particularly around day fourteen and day thirty. Each review should have a clear placement plan.

I would also monitor the percentage of dog visits lasting more than thirty days.

The data tells us that stays are getting longer. It doesn't tell us exactly why, so that would be an important area for further investigation."

*Transition:* "The second finding looks at what happens after an animal has already found a home."

## Slide 7 — Finding 2: Owner surrender after adoption

"This was another interesting pattern.

I looked at owner-surrender visits between 2016 and 2024 and checked whether the animal's previous recorded visit at the shelter had ended in adoption.

I found that 24.46% of these owner-surrender visits involved an animal that had previously been adopted from the shelter.

I then looked at how recently that adoption had happened.

14.89% of all owner-surrender visits involved animals adopted within the previous thirty days. And 8.96% involved animals adopted within just seven days.

That tells us that early post-adoption support could be worth looking at.

For example, the shelter could consider checking in with adopters after a few days and again after two weeks. It could also offer behaviour support or guidance when people are struggling.

I want to be careful about the interpretation, though. The dataset doesn't record the actual reasons for surrender. So I can't say why these animals came back.

What I can say is that the timing gives the shelter a useful place to focus its attention."

*Transition:* "My third finding looks at a different part of the animal journey: getting lost dogs back to their owners."

## Slide 8 — Finding 3: Stray dogs returned to their owners

"Returning a stray dog to its owner is one of the quickest outcomes in the data.

For dogs, the median time to this outcome was about 1.82 days, and around 63.5% were returned within three days.

But I noticed that the share of stray-dog visits ending in return to owner had fallen.

Between 2014 and 2019, the average was 29.46%. By 2024, it was 12.51%.

The number of dogs returned also fell, from around 2,036 in 2019 to 386 in 2024.

My recommendation is to make reunification as quick as possible. That means checking for microchips at intake, posting found animals quickly, and making sure owner-contact information is useful and up to date.

There is one important gap in this data: if an animal is reunited directly in the field without entering the shelter, it won't appear in these records.

So before using this as a complete performance measure, I would want to compare it with the shelter's field-return records."

*Transition:* "I also looked at the wider policy and welfare context around these findings."

## Slide 9 — Welfare, policy and environmental context

"I wanted to understand the wider environment in which the shelter operates, but I kept that separate from the findings in my dataset.

For example, Texas law sets standards for animal shelter housing, sanitation and separation. It also requires shelters to scan animals for microchips as soon as practicable after taking them into custody. The law also provides for an annual veterinary inspection of animal shelters.

Austin's public guidance describes a seventy-two-hour stray hold. The City also has a stated live-outcome commitment, with wildlife treated separately in its reporting.

The City Auditor's 2023 work highlighted challenges around overcrowding, conflicting priorities and limited intake capacity.

That context is relevant to my first finding, because longer stays can put further pressure on available space.

I also looked at the wildlife records. Many wildlife visits in this dataset ended in euthanasia, with rabies risk commonly recorded. Texas public-health information identifies bats and skunks among the wildlife species of concern.

Finally, environmental factors such as extreme heat may affect animal welfare, but my dataset does not contain enough information to measure that. So I treat it as an area for further investigation, not as a finding from this analysis."

*Transition:* "So, bringing everything together, these are the actions I would prioritise."

## Slide 10 — Recommendations and conclusion

"I would take three priorities forward.

First, capacity. Introduce a long-stay review process for dogs and monitor how many visits go beyond thirty days.

Second, prevention. Provide more support to adopters during the first thirty days, and track how many owner surrenders follow a recent adoption.

Third, reunification. Make it easier to identify owners quickly through microchip checks, timely online listings and better contact information. I would also track field returns alongside shelter returns.

There are things I would want to improve in the data as well. Foster dates, surrender reasons and field reunifications would help us understand these patterns much better.

The main takeaway from this project is that the data is not just about counting animals. It can help us understand where animals are spending time, where they may be returning, and where the shelter could make practical improvements.

So, three findings and three possible areas of action: help long-stay dogs move towards placement, support adopters early, and help lost dogs get home faster.

Thank you. I'll now switch to the Power BI report and show how these patterns can be explored."

---

## Transition to the Power BI demonstration

*Exit full screen and switch to Power BI Desktop, with the submitted report already open.*

"This is the report I submitted. It has three pages.

The Executive Summary brings the main findings together. Shelter Overview looks at intake and outcome patterns. And Operational Insights focuses on length of stay and year-on-year changes.

I'll quickly show how the report can be explored using the filters and visuals."

*Follow the separate Power BI demonstration plan.*

## Short answers to remember

**Why didn't you join the two tables directly using Animal ID?**

"Because Animal ID identifies the animal, not the individual visit. The same animal can enter the shelter several times, so I matched the records in date order instead."

**Does twelve days mean twelve days in a kennel?**

"No. It measures the time from intake to the final recorded outcome. The data doesn't give us separate foster dates, so I can't call it physical shelter occupancy."

**Why did you choose those three findings?**

"I wanted findings that had reliable evidence, were relevant to the shelter and could lead to practical action."

**Do you know why owner surrenders happened?**

"Not from this dataset. It doesn't contain the reasons for surrender. I can identify the timing and previous adoption history, but not the cause."

**Did the director approve these recommendations?**

"They are my findings and recommendations based on the available data. They are intended for the director to consider."

**What would you improve with more data?**

"I'd want foster start and end dates, reasons for surrender, and records of animals reunited directly in the field. Those would help us measure the full picture more accurately."