"""Shared loading, parsing and cleaning helpers for the Austin Animal Center audit.

Design rules (see CLAUDE.md and DECISION_LOG.md):
* Raw CSVs in data/raw/ are read-only. Nothing in this module writes to them.
* All source columns are read as text first so that nothing is silently coerced;
  typed columns are then derived explicitly and parse failures are counted.
* Timestamps are interpreted as Austin *wall-clock* (source-local) time and kept
  as timezone-naive datetimes. Outcome offsets are recorded as metadata, never
  used to shift the clock (DQ-003 / D-010).
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = REPO_ROOT / "data" / "raw"
PROCESSED_DIR = REPO_ROOT / "data" / "processed"
REFERENCE_DIR = REPO_ROOT / "data" / "reference"
OUT_AUDIT = REPO_ROOT / "outputs" / "audit"
OUT_MATCH = REPO_ROOT / "outputs" / "matching"
OUT_ANALYSIS = REPO_ROOT / "outputs" / "analysis"

INTAKE_FILE = RAW_DIR / "Austin_Animal_Center_Intakes__10_01_2013_to_05_05_2025_.csv"
OUTCOME_FILE = RAW_DIR / "Austin_Animal_Center_Outcomes__10_01_2013_to_05_05_2025_.csv"
CHECKSUM_FILE = REFERENCE_DIR / "source_checksums.csv"

INTAKE_DT_FORMAT = "%m/%d/%Y %I:%M:%S %p"
# Last calendar date covered by the extract (from the file name and max timestamps).
EXTRACT_END = pd.Timestamp("2025-05-05 23:59:59")

# Text tokens that represent a missing value in the source (distinct from the
# legitimate category "Unknown", which is retained as a category).
NULL_TOKENS = {"", "NULL"}

AGE_UNIT_DAYS = {"day": 1.0, "week": 7.0, "month": 30.4375, "year": 365.25}

# Provisional outcome grouping. This is NOT the City of Austin live-release
# formula (open question DECISION_LOG §12 Q4); it is a descriptive grouping.
OUTCOME_GROUP = {
    "Adoption": "Adoption",
    "Rto-Adopt": "Return to Owner",
    "Return to Owner": "Return to Owner",
    "Transfer": "Transfer",
    "Relocate": "Relocate",
    "Euthanasia": "Euthanasia",
    "Died": "Died",
    "Disposal": "Disposal",
    "Missing": "Missing / Lost / Stolen",
    "Lost": "Missing / Lost / Stolen",
    "Stolen": "Missing / Lost / Stolen",
}
# Provisional live / non-live status. "Disposal" and missing/lost/stolen are
# deliberately NOT counted as either live or non-live outcomes.
OUTCOME_STATUS = {
    "Adoption": "Live outcome",
    "Return to Owner": "Live outcome",
    "Transfer": "Live outcome",
    "Relocate": "Live outcome",
    "Euthanasia": "Non-live outcome",
    "Died": "Non-live outcome",
    "Disposal": "Other / indeterminate",
    "Missing / Lost / Stolen": "Other / indeterminate",
    "Not recorded": "Other / indeterminate",
}


# --------------------------------------------------------------------------- io
def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_raw(path: Path) -> pd.DataFrame:
    """Read a source CSV with every column as text and no NA inference."""
    return pd.read_csv(path, dtype=str, keep_default_na=False, na_filter=False)


def ensure_dirs() -> None:
    for d in (PROCESSED_DIR, REFERENCE_DIR, OUT_AUDIT, OUT_MATCH, OUT_ANALYSIS):
        d.mkdir(parents=True, exist_ok=True)


def write_csv(df: pd.DataFrame, path: Path, **kw) -> Path:
    """Write a CSV with compact, typed-friendly encodings.

    Booleans are written as 1/0 and floats are rounded to 6 decimals
    (< 0.1 second for day-valued durations) to keep file sizes manageable.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    df = df.copy()
    for c in df.columns:
        if df[c].dtype == object:
            nn = df[c].dropna()
            if len(nn) and nn.map(lambda x: isinstance(x, (bool, np.bool_))).all():
                df[c] = df[c].map({True: 1, False: 0}).astype("Int8")
                continue
        if pd.api.types.is_datetime64_any_dtype(df[c]) and (c.endswith("_date") or c == "date_of_birth"):
            df[c] = df[c].dt.strftime("%Y-%m-%d")  # date-only columns written without a time part
        elif df[c].dtype == bool:
            df[c] = df[c].astype("int8")
        elif str(df[c].dtype) == "boolean":
            df[c] = df[c].astype("Int8")
        elif pd.api.types.is_float_dtype(df[c]):
            df[c] = df[c].round(6)
    # ISO-8601 datetimes in files: unambiguous, typed on import into Power BI.
    df.to_csv(path, index=False, date_format="%Y-%m-%d %H:%M:%S", lineterminator="\n", **kw)
    return path


# ---------------------------------------------------------------------- parsing
def parse_intake_datetime(s: pd.Series) -> pd.Series:
    """Parse 'MM/DD/YYYY hh:mm:ss AM' strictly; failures become NaT."""
    return pd.to_datetime(s, format=INTAKE_DT_FORMAT, errors="coerce")


_ISO_RE = re.compile(r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})([+-]\d{2}:\d{2})?$")


def parse_outcome_datetime(s: pd.Series) -> pd.DataFrame:
    """Parse ISO-8601 outcome timestamps as source-local wall-clock time.

    Returns columns: outcome_datetime (naive), outcome_tz_offset (text or NA),
    outcome_format_valid (bool). The offset is retained as metadata only.
    """
    parts = s.str.extract(_ISO_RE)
    dt = pd.to_datetime(parts[0], format="%Y-%m-%dT%H:%M:%S", errors="coerce")
    return pd.DataFrame(
        {
            "outcome_datetime": dt,
            "outcome_tz_offset": parts[1],
            "outcome_format_valid": parts[0].notna(),
        },
        index=s.index,
    )


_AGE_RE = re.compile(r"^\s*(-?\d+)\s+(day|week|month|year)s?\s*$")


def parse_age(s: pd.Series) -> pd.DataFrame:
    """Parse 'N unit(s)' age text into a number, unit and approximate days."""
    parts = s.str.extract(_AGE_RE)
    num = pd.to_numeric(parts[0], errors="coerce")
    unit = parts[1]
    days = num * unit.map(AGE_UNIT_DAYS)
    return pd.DataFrame({"age_value": num, "age_unit": unit, "age_days": days}, index=s.index)


def age_band(age_days: pd.Series) -> pd.Series:
    """Life-stage bands. Negative or missing ages map to 'Invalid / unknown'."""
    bins = [-np.inf, -0.0001, 30, 182.6, 365.25, 365.25 * 3, 365.25 * 7, np.inf]
    labels = [
        "Invalid / unknown",
        "Under 1 month",
        "1-5 months",
        "6-11 months",
        "1-2 years",
        "3-6 years",
        "7+ years",
    ]
    out = pd.cut(age_days, bins=bins, labels=labels, right=False).astype(object)
    return out.fillna("Invalid / unknown")


def clean_text(s: pd.Series) -> pd.Series:
    """Trim and collapse internal whitespace; map NULL tokens to NA."""
    out = s.str.strip().str.replace(r"\s{2,}", " ", regex=True)
    return out.where(~out.isin(NULL_TOKENS), pd.NA)


# ---------------------------------------------------------------- duplicates
def flag_duplicates(raw: pd.DataFrame, id_col: str, dt_col: str) -> pd.DataFrame:
    """Return duplicate flags computed on the *raw text* of every source column.

    * is_exact_duplicate: True for the 2nd+ occurrence of a fully identical row.
    * exact_duplicate_group_size: number of identical rows in the group.
    * is_same_id_timestamp_conflict: same Animal ID + timestamp text as another
      row but differing in at least one other column (suspected duplicate event,
      retained for matching but flagged).
    """
    cols = list(raw.columns)
    exact = raw.duplicated(subset=cols, keep="first")
    group_size = raw.groupby(cols, sort=False)[cols[0]].transform("size")
    # same id+timestamp groups, counted on distinct rows only
    distinct = raw[~exact]
    n_versions = distinct.groupby([id_col, dt_col])[id_col].transform("size")
    conflict = pd.Series(False, index=raw.index)
    conflict.loc[distinct.index] = n_versions > 1
    return pd.DataFrame(
        {
            "is_exact_duplicate": exact,
            "exact_duplicate_group_size": group_size.astype(int),
            "is_same_id_timestamp_conflict": conflict,
        },
        index=raw.index,
    )


# ------------------------------------------------------------- derived tables
def build_intakes(raw: pd.DataFrame) -> pd.DataFrame:
    """Derive the typed, cleaned intake event table (one row per source row)."""
    df = pd.DataFrame(index=raw.index)
    df["intake_event_id"] = [f"IN{n:06d}" for n in range(1, len(raw) + 1)]
    df["source_row"] = np.arange(2, len(raw) + 2)  # line number in the CSV file
    df["animal_id"] = raw["Animal ID"].str.strip()
    df["intake_datetime"] = parse_intake_datetime(raw["DateTime"])
    df["intake_date"] = df["intake_datetime"].dt.normalize()
    df["intake_datetime_raw"] = raw["DateTime"]
    df["monthyear_raw"] = raw["MonthYear"]
    df["monthyear_consistent"] = df["intake_datetime"].dt.strftime("%B %Y") == raw["MonthYear"]
    name = clean_text(raw["Name"])
    df["name"] = name.str.lstrip("*")
    df["name_has_asterisk"] = raw["Name"].str.startswith("*")
    df["found_location"] = clean_text(raw["Found Location"])
    df["intake_type"] = clean_text(raw["Intake Type"])
    df["intake_condition"] = clean_text(raw["Intake Condition"])
    df["animal_type"] = clean_text(raw["Animal Type"])
    df["sex_upon_intake"] = clean_text(raw["Sex upon Intake"])
    df["age_upon_intake_raw"] = raw["Age upon Intake"]
    age = parse_age(raw["Age upon Intake"])
    df["age_upon_intake_days"] = age["age_days"]
    df["age_upon_intake_invalid"] = age["age_days"].isna() | (age["age_days"] < 0)
    df["age_band_intake"] = age_band(age["age_days"])
    df["breed"] = clean_text(raw["Breed"])
    df["breed_is_mix"] = df["breed"].str.contains(r"Mix|/", regex=True, na=False)
    df["color"] = clean_text(raw["Color"])
    df = pd.concat([df, flag_duplicates(raw, "Animal ID", "DateTime")], axis=1)
    return df


def build_outcomes(raw: pd.DataFrame) -> pd.DataFrame:
    """Derive the typed, cleaned outcome event table (one row per source row)."""
    df = pd.DataFrame(index=raw.index)
    df["outcome_event_id"] = [f"OUT{n:06d}" for n in range(1, len(raw) + 1)]
    df["source_row"] = np.arange(2, len(raw) + 2)
    df["animal_id"] = raw["Animal ID"].str.strip()
    parsed = parse_outcome_datetime(raw["DateTime"])
    df["outcome_datetime"] = parsed["outcome_datetime"]
    df["outcome_date"] = df["outcome_datetime"].dt.normalize()
    df["outcome_datetime_raw"] = raw["DateTime"]
    df["outcome_tz_offset"] = parsed["outcome_tz_offset"]
    # All offset-bearing rows are exactly midnight with a constant -05:00,
    # including winter dates (CST would be -06:00): treated as date-only.
    df["outcome_time_is_date_only"] = parsed["outcome_tz_offset"].notna()
    df["outcome_is_midnight"] = df["outcome_datetime"].dt.strftime("%H:%M:%S") == "00:00:00"
    df["monthyear_raw"] = raw["MonthYear"]
    df["monthyear_consistent"] = df["outcome_datetime"].dt.strftime("%m-%Y") == raw["MonthYear"]
    df["date_of_birth"] = pd.to_datetime(raw["Date of Birth"], format="%Y-%m-%d", errors="coerce")
    df["dob_after_outcome"] = df["date_of_birth"] > df["outcome_date"]
    name = clean_text(raw["Name"])
    df["name"] = name.str.lstrip("*")
    df["name_has_asterisk"] = raw["Name"].str.startswith("*")
    otype = clean_text(raw["Outcome Type"])
    df["outcome_type"] = otype
    df["outcome_type_missing"] = otype.isna()
    df["outcome_subtype"] = clean_text(raw["Outcome Subtype"])
    grp = otype.map(OUTCOME_GROUP)
    grp = grp.where(otype.isna() | grp.notna(), "Other")
    df["outcome_group"] = grp.fillna("Not recorded")
    df["outcome_status_provisional"] = df["outcome_group"].map(OUTCOME_STATUS).fillna("Other / indeterminate")
    df["animal_type"] = clean_text(raw["Animal Type"])
    df["sex_upon_outcome"] = clean_text(raw["Sex upon Outcome"])
    df["age_upon_outcome_raw"] = raw["Age upon Outcome"]
    age = parse_age(raw["Age upon Outcome"])
    df["age_upon_outcome_days"] = age["age_days"]
    df["age_upon_outcome_invalid"] = age["age_days"].isna() | (age["age_days"] < 0)
    df["age_from_dob_days"] = (df["outcome_date"] - df["date_of_birth"]).dt.days
    df["breed"] = clean_text(raw["Breed"])
    df["color"] = clean_text(raw["Color"])
    df = pd.concat([df, flag_duplicates(raw, "Animal ID", "DateTime")], axis=1)
    return df


def load_clean() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load raw sources and return derived (intakes, outcomes) tables."""
    return build_intakes(read_raw(INTAKE_FILE)), build_outcomes(read_raw(OUTCOME_FILE))


def fmt_ddmmyyyy(ts) -> str:
    """Display helper for reports only (DD-MM-YYYY). Never used on stored data."""
    if pd.isna(ts):
        return ""
    return pd.Timestamp(ts).strftime("%d-%m-%Y")


def metrics_frame(d: dict) -> pd.DataFrame:
    """Key-metric dict -> two-column frame, preserving integers as integers."""
    return pd.DataFrame({"metric": list(d.keys()), "value": pd.Series(list(d.values()), dtype=object)})
