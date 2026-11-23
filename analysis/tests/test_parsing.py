"""Date, timestamp and age parsing."""
import pandas as pd

from common import age_band, fmt_ddmmyyyy, parse_age, parse_intake_datetime, parse_outcome_datetime
from matching_engine import sequencing_key


def test_intake_datetime_12h_clock():
    s = pd.Series(["10/01/2013 07:51:00 AM", "05/04/2025 11:44:00 PM", "12/31/2019 12:00:00 AM",
                   "12/31/2019 12:00:00 PM"])
    out = parse_intake_datetime(s)
    assert list(out) == [pd.Timestamp("2013-10-01 07:51"), pd.Timestamp("2025-05-04 23:44"),
                         pd.Timestamp("2019-12-31 00:00"), pd.Timestamp("2019-12-31 12:00")]


def test_intake_datetime_is_month_first_not_day_first():
    assert parse_intake_datetime(pd.Series(["02/03/2020 01:00:00 PM"]))[0] == pd.Timestamp("2020-02-03 13:00")


def test_invalid_intake_datetime_becomes_nat():
    out = parse_intake_datetime(pd.Series(["2020-02-03", "13/40/2020 01:00:00 PM", ""]))
    assert out.isna().all()


def test_outcome_offset_preserved_as_metadata_not_applied():
    s = pd.Series(["2013-12-02T00:00:00-05:00", "2019-06-01T17:30:15", "bad"])
    out = parse_outcome_datetime(s)
    # wall clock kept: no shift to UTC (+5h) for the offset row
    assert out.loc[0, "outcome_datetime"] == pd.Timestamp("2013-12-02 00:00:00")
    assert out.loc[0, "outcome_tz_offset"] == "-05:00"
    assert out.loc[1, "outcome_datetime"] == pd.Timestamp("2019-06-01 17:30:15")
    assert pd.isna(out.loc[1, "outcome_tz_offset"])
    assert out["outcome_datetime"].dt.tz is None
    assert pd.isna(out.loc[2, "outcome_datetime"]) and not out.loc[2, "outcome_format_valid"]


def test_date_only_outcome_sequenced_at_end_of_day_without_changing_value():
    s = pd.Series(pd.to_datetime(["2016-05-14 00:00:00", "2016-05-14 09:15:00"]))
    key = sequencing_key(s)
    assert key[0] == pd.Timestamp("2016-05-14 23:59:59")
    assert key[1] == s[1]
    assert s[0] == pd.Timestamp("2016-05-14")  # original untouched


def test_age_parsing_including_negative_and_null():
    out = parse_age(pd.Series(["2 years", "1 year", "3 weeks", "-1 years", "NULL", "0 years"]))
    assert out["age_days"].tolist()[:3] == [730.5, 365.25, 21.0]
    assert out.loc[3, "age_days"] == -365.25
    assert pd.isna(out.loc[4, "age_days"])
    bands = age_band(out["age_days"]).tolist()
    assert bands[3] == "Invalid / unknown" and bands[4] == "Invalid / unknown" and bands[5] == "Under 1 month"


def test_display_format_is_dd_mm_yyyy():
    assert fmt_ddmmyyyy(pd.Timestamp("2025-05-04 13:00")) == "04-05-2025"
    assert fmt_ddmmyyyy(pd.NaT) == ""
