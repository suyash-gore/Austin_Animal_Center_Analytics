// DimAnimalType — conformed animal-type dimension filtering FactIntakes, FactOutcomes and FactVisits
// (single-direction, one-to-many on [Animal Type] -> fact[animal_type]).
// Built from the distinct non-null animal_type values of all three facts so that no fact value can be
// missing from the dimension. Validated values (analysis/validate_powerbi_model.py):
// Dog, Cat, Other, Bird, Livestock — identical spelling in all three facts; no blanks.
// "Other" is mostly wildlife (bats, raccoons, etc.) — see docs/DATA_AUDIT_REPORT.md.
let
    Values = List.Distinct(List.RemoveNulls(List.Combine({
        FactIntakes[animal_type], FactOutcomes[animal_type], FactVisits[animal_type]}))),
    Base = Table.FromList(Values, Splitter.SplitByNothing(), type table [Animal Type = text]),
    SortOrder = [Dog = 1, Cat = 2, Other = 3, Bird = 4, Livestock = 5],
    AddSort = Table.AddColumn(Base, "Animal Type Sort", each Record.FieldOrDefault(SortOrder, [Animal Type], 99), Int64.Type),
    AddNote = Table.AddColumn(AddSort, "Animal Type Note", each
        if [Animal Type] = "Other" then "Mostly wildlife; separate from companion animals in outcome analysis"
        else null, type nullable text),
    Sorted = Table.Sort(AddNote, {{"Animal Type Sort", Order.Ascending}}),
    Keyed = Table.AddKey(Sorted, {"Animal Type"}, true)
in
    Keyed
