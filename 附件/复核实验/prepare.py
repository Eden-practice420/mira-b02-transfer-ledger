"""New 90-day synthetic ledger, independent of the original hand-crafted cases."""
import csv,random
from pathlib import Path
ROOT=Path(__file__).resolve().parent
rng=random.Random(202907)
with (ROOT/"new_service_days.csv").open("w",encoding="utf-8",newline="") as fp:
    w=csv.writer(fp);w.writerow(["scenario","day","feeder_arrival","connector_depart","walk","transfer_n","onboard_n","next_headway","cancelled"])
    for scenario,headway,crowd in [("frequent",8,38),("ordinary",16,22),("late",30,10)]:
        for day in range(1,31):
            traffic=rng.choice([0,0,1,1,2,3])
            feeder=traffic+rng.choice([-3,-2,-1,0,1,2,3])
            departure=traffic+rng.choice([0,0,0,1,1,2])
            w.writerow([scenario,day,feeder,departure,rng.choice([1,2,3]),rng.randint(4,12),crowd+rng.randint(-4,4),headway,int(day==25 and scenario=="late")])
