"""Headline metrics quoted in docs must match the generated outputs."""
from pathlib import Path

import pandas as pd
import pytest

from common import OUT_ANALYSIS, OUT_MATCH, REPO_ROOT

DOCS = REPO_ROOT / "docs"
pytestmark = pytest.mark.skipif(not (OUT_MATCH / "matching_key_metrics.csv").exists(),
                                reason="run analysis/run_all.py first")


def fmt(v: float) -> str:
    return f"{int(v):,}" if float(v).is_integer() else f"{v:.2f}"


def metrics(path: Path) -> pd.Series:
    return pd.read_csv(path).set_index("metric")["value"].astype(float)


@pytest.mark.parametrize("doc,keys", [
    ("VISIT_MATCHING_METHODOLOGY.md", ["matched_visits", "unmatched_intakes", "unmatched_outcomes",
                                        "same_day_reversed_candidates_excluded", "los_floored_to_zero",
                                        "long_stays_365plus", "los_p50", "los_p75", "los_p90", "los_p95",
                                        "los_p99"]),
    ("DATA_AUDIT_REPORT.md", ["matched_visits", "unmatched_intakes", "unmatched_outcomes", "los_p99"]),
])
def test_matching_metrics_quoted_correctly(doc, keys):
    text = (DOCS / doc).read_text()
    km = metrics(OUT_MATCH / "matching_key_metrics.csv")
    for k in keys:
        assert fmt(km[k]) in text, f"{doc}: {k}={fmt(km[k])} not found"


def test_opportunity_evidence_quoted_correctly():
    text = (DOCS / "BUSINESS_OPPORTUNITY_REGISTER.md").read_text()
    ev = metrics(OUT_ANALYSIS / "analysis_key_metrics.csv")
    for k in ["owner_surrender_after_adoption_pct_2016_2024", "adoption_returns_within_30d_pct",
              "adoption_returns_within_7d_pct", "dog_median_2014_2019", "dog_median_2023_2024",
              "dog_nf_over30_2014_2019", "dog_nf_over30_2023_2024", "stray_dog_rto_pct_2014_2019",
              "stray_dog_rto_pct_2024", "adoption_share_pct", "transfer_share_pct", "euthanasia_share_pct"]:
        assert fmt(ev[k]) in text, f"{k}={fmt(ev[k])} not found"
