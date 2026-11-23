import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def ev(rows):
    """Build an event frame from (event_id, animal_id, 'YYYY-MM-DD HH:MM') tuples."""
    return pd.DataFrame(rows, columns=["event_id", "animal_id", "dt"]).assign(dt=lambda d: pd.to_datetime(d["dt"]))


@pytest.fixture
def make_events():
    return ev
