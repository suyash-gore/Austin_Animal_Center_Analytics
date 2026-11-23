"""Run the full audit pipeline and test suite from the raw source files.

    python analysis/run_all.py            # audit -> matching -> analysis -> pytest
    python analysis/run_all.py --no-tests

Each stage is a separate process so every script is also runnable on its own.
"""
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGES = ["analysis/audit_datasets.py", "analysis/match_visits.py", "analysis/explore_business_opportunities.py"]


def run(cmd):
    t = time.time()
    print(f"\n=== {' '.join(cmd)}", flush=True)
    r = subprocess.run(cmd, cwd=ROOT, stdout=subprocess.DEVNULL if "pytest" not in cmd[2:3] else None)
    print(f"--- exit {r.returncode} in {time.time() - t:.1f}s", flush=True)
    if r.returncode:
        sys.exit(r.returncode)


if __name__ == "__main__":
    for s in STAGES:
        run([sys.executable, s])
    if "--no-tests" not in sys.argv:
        run([sys.executable, "-m", "pytest", "analysis/tests", "-q"])
