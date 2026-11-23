# Data Quality Issues Register

Every issue found in the Stage 1 audit, with its size, treatment and analytical impact. No record has
been deleted from the source; treatments apply to derived data only. Severity: **High** = can change a
headline metric if mishandled; **Medium** = affects a segment or definition; **Low** = cosmetic or
negligible. Evidence files are under `outputs/`.

| ID | Issue | Dataset | Size | Severity | Treatment | Impact / residual risk | Evidence |
|---|---|---|---:|---|---|---|---|
| DQ-001 | Animal ID is not a visit key; animals recur (max 33 intakes) | both | 13,487 / 13,507 repeated IDs; 31,012 / 31,045 rows | High | Visit matching (D-010) | Naive ID join would duplicate rows and corrupt LOS | `audit/animal_id_frequency.csv` |
| DQ-002 | No sequence / visit field in either file | both | – | High | Rank join evaluated and rejected (784 negative durations) | Earlier "sequence" results superseded | `matching/method_comparison.csv` |
| DQ-003 | Outcome timestamps carry a constant `-05:00` offset on midnight rows only, incl. 884 rows in CST months | outcomes | 3,584 | High | Wall-clock interpretation; offset kept as metadata (D-008) | Converting would shift dates/LOS | `audit/date_quality.csv` |
| DQ-004 | Outcomes recorded date-only (00:00:00) | outcomes | 3,788 | High | Sequenced at end of day (D-011); LOS for same-date cases floored to 0 and flagged | LOS for these visits has day precision only | `matching/candidate_visits.csv` (`outcome_is_midnight`) |
| DQ-005 | Same-date outcome recorded earlier than its intake | both | 225 matched by second pass | Medium | D-012 rule, LOS = 0, flagged | Small downward effect on LOS (P90 55.56 → 55.34) | `matching/los_percentiles.csv` |
| DQ-006 | Exact duplicate rows | both | 36 / 26 excess rows | Medium | Flagged; excluded from analytic events and matching | Changes FIFO/LIFO matches by 35 | `audit/exact_duplicate_rows_*.csv`, `matching/deduplication_impact.csv` |
| DQ-007 | Same ID + timestamp with different Found Location / Intake Type / Subtype | both | 6 intake pairs, 1 outcome pair | Low | Retained, flagged; in ambiguity list | One of each pair becomes unmatched | `audit/same_id_timestamp_conflicts.csv` |
| DQ-008 | Consecutive same-kind events < 24 h apart (suspected duplicate events) | both | 10 intakes, 17 outcomes | Low | Retained; second outcome typically unmatched | Negligible | `audit/suspected_duplicate_events.csv` |
| DQ-009 | Intake with no later outcome | intakes | 1,004 unmatched (864 IDs with no outcome at all; 849 of those dated 2024–2025) | Medium | Kept as "Intake without matched outcome" rows; excluded from LOS | Recent cohorts right-censored; open stays not in LOS | `matching/unmatched_intakes.csv` |
| DQ-010 | Outcome with no earlier intake | outcomes | 977 unmatched (798 dated 2013) | Medium | Kept as "Outcome without matched intake" rows | Extract starts mid-stream (01-10-2013) | `matching/unmatched_outcomes.csv` |
| DQ-011 | Ambiguous pairings (method-dependent) | both | 45 animals, 84 visits | Low | Recommended assignment kept, flagged | ≤ 0.04 day effect on any LOS percentile | `matching/ambiguous_matches.csv` |
| DQ-012 | Outcome Subtype blank | outcomes | 94,115 (54.16%) | Medium | Kept blank; shown as "(not recorded)" in analysis | Blank is structural: RTO 98.9%, Rto-Adopt 100%, Adoption 78.2% blank; Transfer 0%, Euthanasia 2.6%. Do not analyse subtype across types. | `analysis/outcome_subtype_by_type.csv` |
| DQ-013 | Outcome Type blank | outcomes | 46 | Low | "Not recorded" group; indeterminate status | Excluded from live/non-live shares by definition | `audit/categorical_distributions.csv` |
| DQ-014 | Negative ages | both | 10 / 10 | Low | Flagged invalid; age band "Invalid / unknown" | Negligible | `audit/age_and_dob_exceptions.csv` |
| DQ-015 | `NULL` age / sex tokens | both | 9 outcome ages; 1 sex each | Low | Converted to missing | Negligible | `audit/column_profile.csv` |
| DQ-016 | Date of birth after outcome date | outcomes | 33 | Low | Flagged `dob_after_outcome` | DOB-based ages unreliable for these | `audit/age_and_dob_exceptions.csv` |
| DQ-017 | Age is derived from DOB in the source | both | all | Low | Noted | Age cannot validate stay length | `matching/candidate_visits.csv` (`intake_age_dob_gap_days` < 1 year for 100%) |
| DQ-018 | Category set changes over time: Abandoned appears 2020; Euthanasia Request ≤ 4/year from 2018 | intakes | 1,910 / 264 rows | Medium | Labels kept as-is | Intake-type trends across 2020 partly reflect coding | `analysis/annual_intakes_by_type.csv` |
| DQ-019 | Overlapping / non-ordinal condition labels (Medical, Med Attn, Med Urgent; Sick vs Parvo/Panleuk) | intakes | 20 labels | Medium | Not merged (D-014) | Welfare KPIs need an agreed mapping | `audit/semantic_label_review.csv` |
| DQ-020 | "Transfer" includes community-cat return programmes (Snr, SCRP) | outcomes | 27.44% of cat transfer visits | Medium | Subtype retained | "Transfer dependency" overstated for cats if read as partner placement | `analysis/transfer_subtype_by_animal.csv` |
| DQ-021 | "Disposal" undefined; 582 of 876 are Other (wildlife) | outcomes | 876 | Medium | Status "Other / indeterminate" | Not counted as live or non-live | `analysis/visit_outcome_mix.csv` |
| DQ-022 | Foster time included in LOS (Adoption/Foster, Died/In Foster, etc.) | outcomes | 18,136 matched visits with a foster subtype | High for LOS interpretation | Reported with and without foster outcomes | Median LOS 54.05 d for foster subtypes vs 5.03 d otherwise; 75.2% of 365+ day visits | `analysis/los_by_foster_subtype.csv`, `analysis/los_trend_by_intake_year.csv`, `analysis/long_stay_profile.csv` |
| DQ-023 | Wildlife in the Other type: 87.1% of Wildlife-intake visits end in euthanasia (mostly Rabies Risk) | both | 6,478 visits | High for live-release metrics | Kept; shown separately | Must follow the official wildlife treatment before quoting any live-release rate | `analysis/visit_outcome_mix.csv` |
| DQ-024 | Breed labels: 3,006 values, 69.31% mixes or slash combinations | both | – | Medium | Breed analysis limited to ≥ 500-visit labels; not recommended for director findings | Visual breed ID is unreliable | `analysis/breed_label_profile.csv` |
| DQ-025 | Found Location is free text (70,183 values), 832 rows with repeated spaces | intakes | – | Low | Whitespace collapsed in derived copy | Spatial analysis needs geocoding | `audit/column_profile.csv` |
| DQ-026 | Colour spelling variant `Blue Cream` vs `Blue/Cream` | both | 98 / 100 rows | Low | Not merged | Negligible | `audit/label_variants.csv` |
| DQ-027 | Return intakes after a non-live outcome (1 after Died, 2 after Euthanasia) | both | 3 | Low | Retained; listed | Probably ID reuse or record error | `analysis/return_intake_previous_outcome.csv` |
| DQ-028 | Partial years 2013 (from 01-10) and 2025 (to 05-05) | both | – | High for trends | Like-for-like windows (D-015) | Direct annual comparison would mislead | `analysis/like_for_like_periods.csv` |
| DQ-029 | Structural break from 03-2020; volumes stay ~36% below 2014–2019 | both | – | High for trends | Reported descriptively, no cause attributed | Pre/post-2020 comparisons need context | `analysis/structural_break_screen.csv` |
| DQ-030 | Name prefix `*` (assumed shelter-assigned) | both | 43,333 / 43,369 | Low | Stripped into a flag | Assumption, unverified | `data/processed/*_clean.csv` |
| DQ-031 | Preliminary "155,448 latest-preceding matches" not reproducible | – | – | Low | Documented; method rejected | None on final results | `matching/preliminary_reconciliation.csv` |

## Unresolved limitations

1. **Live-release definition** (DECISION_LOG §12 Q4): the provisional live-outcome share (92.20% of
   matched visits) is a descriptive grouping, not the City's rate. Wildlife, Disposal and Missing need
   the official treatment.
2. **Ground truth for ambiguous and superseded records** cannot be established from the extract.
3. **Foster vs on-site time** cannot be separated; LOS measures custody time.
4. **Cause of the 2020 break** and of later trend changes is not identifiable from the data.
5. **Field activity** (e.g. animals returned to owners without an intake record) is invisible, so
   shares such as stray RTO describe sheltered animals only.
6. **Open stays at 05-05-2025** are not observed to completion; LOS for 2024–2025 intake cohorts is
   biased low for long stays.
