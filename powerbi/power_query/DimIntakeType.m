// DimIntakeType — conformed intake-type dimension filtering FactIntakes and FactVisits
// (single-direction, one-to-many on [intake_type] -> FactIntakes[intake_type] and FactVisits[intake_type]).
// Built from the distinct NON-NULL intake_type values of both facts, so no fact value can be missing.
// Validated domain (analysis/validate_powerbi_model.py): Stray, Owner Surrender, Public Assist, Wildlife,
// Abandoned, Euthanasia Request — identical spelling in both facts.
// FactVisits[intake_type] is null only on the 1,202 "Outcome without matched intake" rows (no intake exists).
// Those rows are NOT removed: they relate to the relationship's blank member, so they are excluded only when
// a specific intake type is selected — which is correct, because they have no intake.
// Not related to FactOutcomes (outcome events carry no intake type).
let
    Values = List.Distinct(List.RemoveNulls(List.Combine({FactIntakes[intake_type], FactVisits[intake_type]}))),
    Base = Table.FromList(Values, Splitter.SplitByNothing(), type table [intake_type = text]),
    SortOrder = [Stray = 1, #"Owner Surrender" = 2, #"Public Assist" = 3, Wildlife = 4, Abandoned = 5,
                 #"Euthanasia Request" = 6],
    AddSort = Table.AddColumn(Base, "Intake Type Sort", each Record.FieldOrDefault(SortOrder, [intake_type], 99), Int64.Type),
    AddNote = Table.AddColumn(AddSort, "Intake Type Note", each
        if [intake_type] = "Abandoned" then "Category first appears in 2020 (coding change; DQ-018)"
        else if [intake_type] = "Euthanasia Request" then "At most 4 per year from 2018 (DQ-018)"
        else if [intake_type] = "Wildlife" then "Mostly animal type Other"
        else null, type nullable text),
    Sorted = Table.Sort(AddNote, {{"Intake Type Sort", Order.Ascending}}),
    Keyed = Table.AddKey(Sorted, {"intake_type"}, true)
in
    Keyed
