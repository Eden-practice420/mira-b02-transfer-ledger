"""Counterfactual replay on intact service-day pairs, never shuffle timestamps."""
import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

def replay(rows, cap):
    logs = []
    for row in rows:
        d = {k:int(v) for k,v in row.items() if k != "stop"}
        if d["cancelled"] not in (0,1) or min(d[k] for k in ("walk","transfer_n","onboard_n","next_headway")) < 0:
            raise ValueError("Invalid passenger, walking, headway or service flag")
        ready = d["feeder_arrival"] + d["walk"]
        gap = ready - d["connector_depart"]
        # A connection can be held only if the feeder is known to be within cap.
        held = gap if not d["cancelled"] and 0 < gap <= cap else 0
        caught = not d["cancelled"] and gap <= held
        # All transferring passengers in this fixture become ready before the following bus.
        if gap > d["next_headway"]:
            raise ValueError("Passenger may miss more than one bus; inspect following timetable")
        alternative = d["connector_depart"] + d["next_headway"]
        depart = d["connector_depart"] + held if caught else alternative
        wait = (depart-ready) * d["transfer_n"]
        inconvenience = held * d["onboard_n"]
        logs.append(dict(day=d["day"], gap=gap, hold=held, caught=d["transfer_n"] if caught else 0,
                         transfer_n=d["transfer_n"], transfer_wait_pm=wait, onboard_delay_pm=inconvenience,
                         cancelled=d["cancelled"]))
    score = {"caught":sum(r["caught"] for r in logs),"eligible":sum(r["transfer_n"] for r in logs),
             "wait_pm":sum(r["transfer_wait_pm"] for r in logs),"delay_pm":sum(r["onboard_delay_pm"] for r in logs)}
    score["cost_pm"] = score["wait_pm"] + score["delay_pm"]
    score["pct"] = round(100 * score["caught"]/score["eligible"],1) if score["eligible"] else None
    return {"summary":score,"days":logs}

if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("csv", type=Path)
    args=parser.parse_args()
    groups=defaultdict(list)
    seen=set()
    with args.csv.open(encoding="utf-8-sig", newline="") as src:
        for r in csv.DictReader(src):
            key=(r["stop"],int(r["day"]))
            if key in seen:
                raise ValueError(f"duplicate day {key}")
            seen.add(key)
            groups[r["stop"]].append(r)
    print(json.dumps({stop:{str(c):replay(rows,c) for c in range(4)} for stop,rows in groups.items()},ensure_ascii=False,indent=2))
