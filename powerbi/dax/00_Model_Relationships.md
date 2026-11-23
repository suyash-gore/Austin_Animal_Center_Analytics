# 00 — Model Relationships

Relationships to create **manually** in Power BI Desktop (Model view) after loading the queries in
`powerbi/power_query/`. Full design rationale: `docs/POWER_BI_DATA_MODEL.md`.

## Relationships

| # | From (one side) | To (many side) | Cardinality | Cross-filter | Active |
|---|---|---|---|---|---|
| R1 | `DimDate[Date]` | `FactIntakes[intake_date]` | 1 : * | Single | **Yes** |
| R2 | `DimDate[Date]` | `FactOutcomes[outcome_date]` | 1 : * | Single | **Yes** |
| R3 | `DimDate[Date]` | `FactVisits[intake_date]` | 1 : * | Single | **Yes** |
| R4 | `DimDate[Date]` | `FactVisits[outcome_date]` | 1 : * | Single | **No** (use `USERELATIONSHIP`) |
| R5 | `DimAnimalType[Animal Type]` | `FactIntakes[animal_type]` | 1 : * | Single | Yes |
| R6 | `DimAnimalType[Animal Type]` | `FactOutcomes[animal_type]` | 1 : * | Single | Yes |
| R7 | `DimAnimalType[Animal Type]` | `FactVisits[animal_type]` | 1 : * | Single | Yes |
| R8 | `DimIntakeType[intake_type]` | `FactIntakes[intake_type]` | 1 : * | Single | Yes |
| R9 | `DimIntakeType[intake_type]` | `FactVisits[intake_type]` | 1 : * | Single | Yes |

## Deliberately NOT created

* No relationship on `animal_id` between any tables (Animal ID is not a visit key; DECISION_LOG D-010).
* No relationship between the fact tables (`intake_event_id` / `outcome_event_id` are traceability keys
  only; adding them would create ambiguous filter paths through the shared dimensions).
* No bidirectional and no many-to-many relationships.
* No relationship from DimIntakeType to FactOutcomes (outcome events have no intake type).
* No conformed outcome-type dimension yet: outcome categories stay in their facts
  (`FactOutcomes[outcome_group]`, `FactVisits[outcome_group]`); a slicer on one filters that fact only.

## Intake type

`DimIntakeType[intake_type]` filters intake events and visits together — use it (not the fact columns) for
the required intake-type slicer. FactVisits outcome-only rows (1,202) have a null `intake_type`; they are kept
and belong to the blank member, so selecting any intake type excludes them (they have no intake).

## Date roles

| Measure family | Date meaning when a DimDate filter is applied |
|---|---|
| Intake event measures (`FactIntakes`) | intake date (R1) |
| Outcome event measures (`FactOutcomes`) | outcome date (R2) |
| Visit measures (`FactVisits`), default | **intake date** — intake cohort (R3) |
| `… (by Outcome Date)` visit measures and `Unmatched Outcome Events` | outcome date via `USERELATIONSHIP` (R4) |

A single date slicer therefore does not mean the same event for every measure. Outcome-only visit rows
have no `intake_date`; they are invisible to R3 under any date filter, which is why
`Unmatched Outcome Events` activates R4.

## Settings checklist

1. Mark `DimDate` as date table (Table tools > Mark as date table > `Date`).
2. `DimDate[Date]` format `dd-MM-yyyy`; also format fact date columns `dd-MM-yyyy` and datetimes
   `dd-MM-yyyy HH:mm`.
3. Sort `DimDate[Month Name]` / `[Month Short Name]` by `[Month Number]`, `[Year-Month]` and
   `[Month-Year Display]` by `[Year-Month Sort]`, `[Day of Week]` by `[Day of Week Number]`,
   `DimAnimalType[Animal Type]` by `[Animal Type Sort]`, `DimIntakeType[intake_type]` by `[Intake Type Sort]`.
4. Turn off Auto date/time (File > Options > Current file > Data load).
5. Hide fact columns used only as keys (`intake_date`, `outcome_date`, `animal_type`, `intake_type`) from report view
   once slicers use the dimension columns.
