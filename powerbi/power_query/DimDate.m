// DimDate — continuous calendar for the extract window. Mark as date table on [Date] in Power BI.
// Range   : 01-10-2013 to 05-05-2025 inclusive (4,235 days). Bounds come from the source extract
//           (intakes 01-10-2013..04-05-2025; outcomes 01-10-2013..05-05-2025).
// Display : set the [Date] column format to dd-MM-yyyy in the model. The column stays a true Date type;
//           no date is stored as formatted text.
// Partial : 2013 (from 01-10) and 2025 (to 05-05) are partial extract years (D-015).
//           05-05-2025 is a partial day (outcomes only to 07:22, no intakes), so the last complete day
//           common to both files is 04-05-2025.
let
    StartDate = #date(2013, 10, 1),
    EndDate = #date(2025, 5, 5),
    LastCompleteDate = #date(2025, 5, 4),
    // Like-for-like window used for partial-year comparisons: 01-01 to 04-05 of each year (D-015).
    WindowEndMonth = Date.Month(LastCompleteDate),
    WindowEndDay = Date.Day(LastCompleteDate),

    Dates = List.Dates(StartDate, Duration.Days(EndDate - StartDate) + 1, #duration(1, 0, 0, 0)),
    Base = Table.FromList(Dates, Splitter.SplitByNothing(), type table [Date = date]),

    IsFullYear = (y as number) as logical => #date(y, 1, 1) >= StartDate and #date(y, 12, 31) <= EndDate,

    AddCols = Table.AddColumn(Base, "Year", each Date.Year([Date]), Int64.Type),
    AddMonthNo = Table.AddColumn(AddCols, "Month Number", each Date.Month([Date]), Int64.Type),
    AddMonthName = Table.AddColumn(AddMonthNo, "Month Name", each Date.MonthName([Date], "en-US"), type text),
    AddMonthShort = Table.AddColumn(AddMonthName, "Month Short Name", each Text.Start(Date.MonthName([Date], "en-US"), 3), type text),
    AddQuarter = Table.AddColumn(AddMonthShort, "Quarter", each "Q" & Text.From(Date.QuarterOfYear([Date])), type text),
    AddYM = Table.AddColumn(AddQuarter, "Year-Month", each
        Text.From([Year]) & "-" & Text.PadStart(Text.From([Month Number]), 2, "0"), type text),
    AddYMSort = Table.AddColumn(AddYM, "Year-Month Sort", each [Year] * 100 + [Month Number], Int64.Type),
    AddMYDisplay = Table.AddColumn(AddYMSort, "Month-Year Display", each [Month Short Name] & " " & Text.From([Year]), type text),
    AddDay = Table.AddColumn(AddMYDisplay, "Day", each Date.Day([Date]), Int64.Type),
    AddDow = Table.AddColumn(AddDay, "Day of Week", each Date.DayOfWeekName([Date], "en-US"), type text),
    // 1 = Monday ... 7 = Sunday
    AddDowNo = Table.AddColumn(AddDow, "Day of Week Number", each Date.DayOfWeek([Date], Day.Monday) + 1, Int64.Type),
    AddFull = Table.AddColumn(AddDowNo, "Is Full Calendar Year", each IsFullYear([Year]), type logical),
    AddPartial = Table.AddColumn(AddFull, "Is Partial Extract Year", each not IsFullYear([Year]), type logical),
    // A year is YoY-comparable only if it and the prior year are both complete (2015-2024).
    AddYoY = Table.AddColumn(AddPartial, "Is YoY Comparable Year", each IsFullYear([Year]) and IsFullYear([Year] - 1), type logical),
    AddComplete = Table.AddColumn(AddYoY, "Is Complete Extract Day", each [Date] <= LastCompleteDate, type logical),
    AddLfl = Table.AddColumn(AddComplete, "Is Jan to 04-May Window", each
        [Month Number] < WindowEndMonth or ([Month Number] = WindowEndMonth and [Day] <= WindowEndDay), type logical),
    AddQ4 = Table.AddColumn(AddLfl, "Is Oct to Dec Window", each [Month Number] >= 10, type logical),
    Keyed = Table.AddKey(AddQ4, {"Date"}, true)
in
    Keyed
