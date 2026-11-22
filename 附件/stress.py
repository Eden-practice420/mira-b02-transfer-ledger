import csv
import json
from collections import defaultdict
from pathlib import Path
from analyze import replay

ROOT=Path(__file__).resolve().parent
groups=defaultdict(list)
with (ROOT/"service_days.csv").open(encoding="utf-8") as fh:
    for row in csv.DictReader(fh):
        groups[row["stop"]].append(row)
assert sorted(r["connector_depart"] for r in groups["同向延误"])==sorted(r["connector_depart"] for r in groups["反向错位"])
out={}
for stop,rows in groups.items():
    base=replay(rows,0)["summary"]
    alt=replay(rows,2)["summary"]
    out[stop]={"saved_transfer_pm":base["wait_pm"]-alt["wait_pm"],"extra_onboard_pm":alt["delay_pm"],
               "break_even_onboard_weight":round((base["wait_pm"]-alt["wait_pm"])/alt["delay_pm"],2)}
(ROOT/"stress.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
