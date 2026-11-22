"""Construct trip-paired service days. Minutes relative to scheduled connection."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sets = {
    "同向延误": ([0,2,5,-1,3,4,1,-2,6,0,2,7], [0,1,3,0,2,2,1,0,3,0,1,5]),
    "反向错位": ([0,2,5,-1,3,4,1,-2,6,0,2,7], [5,3,0,3,0,1,2,2,0,1,1,0]),
    "晚班接续": ([2,4,7,1,0,-1,6,3,1,0,4,3], [2,1,3,0,1,0,1,1,0,1,0,1]),
}
with (ROOT/"service_days.csv").open("w", encoding="utf-8", newline="") as dst:
    wr = csv.writer(dst)
    wr.writerow(["stop","day","feeder_arrival","connector_depart","walk","transfer_n","onboard_n","next_headway","cancelled"])
    for stop, (arr, dep) in sets.items():
        for i,(a,b) in enumerate(zip(arr,dep)):
            wr.writerow([stop, i+1, a-2, b, 2, [5,7,9,4,11,8][i%6], [12,18,10,22][i%4], 35 if stop=="晚班接续" else 15, int(stop=="晚班接续" and i==9)])
