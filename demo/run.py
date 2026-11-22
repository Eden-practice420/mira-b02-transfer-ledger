"""Replay the local demonstration from any working directory (Python 3.10+)."""
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "demo"
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("stage", choices=["input", "run", "challenge"])
stage = parser.parse_args().stage
import csv
import json
import shutil
import subprocess
import sys
import tempfile

LAB = ROOT / "附件" / "复核实验"

def replay(script, fixture):
    # Work inside a temporary copy: the underlying research script also writes its logs.
    with tempfile.TemporaryDirectory() as td:
        working = Path(td)
        for name in (script, fixture):
            shutil.copy2(LAB/name, working/name)
        subprocess.run([sys.executable, "-B", working/script], check=True, capture_output=True)
        return json.loads((working/"results.json").read_text(encoding="utf-8"))

fixture="new_service_days.csv"
if stage=="input":
    with (LAB/fixture).open(encoding="utf-8",newline="") as fp:
        days=list(csv.DictReader(fp))
    r=days[0]
    print(f"service days   {len(days)} simulated")
    print(f"day 1 / {r['scenario']} | walk {r['walk']} min")
    print(f"transfer {r['transfer_n']}  onboard {r['onboard_n']}")
    print(f"next service after {r['next_headway']} min")
else:
    result=replay("forecast.py",fixture)
    if stage=="run":
        print("hold cap       2 min")
        print("paired repeats 200")
        for model,label in (("perfect","perfect"),("noise2","noise 2 min")):
            print(f"{label:<12} {result[model]['net_pm_median']:+.0f} pax-min")
    else:
        s=result["optimistic"]
        print("arrival bias   -2 min | SD 1")
        print(f"median         {s['net_pm_median']:+.0f} pax-min")
        print(f"P10 / P90      {s['net_pm_p10']:+.0f} / {s['net_pm_p90']:+.0f}")
        print(f"empty hold     {s['avg_empty_hold_days']:.2f} days / 90")
