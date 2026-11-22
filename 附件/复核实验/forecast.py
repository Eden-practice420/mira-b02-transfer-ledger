"""Paired counterfactual replay with forecast error. All costs are passenger-minutes."""
import csv,json,random
from collections import defaultdict
from pathlib import Path
from statistics import mean,median
ROOT=Path(__file__).resolve().parent
CAP=2
SCENARIOS={"perfect":(0,0),"noise1":(0,1),"noise2":(0,2),"noise4":(0,4),"optimistic":(-2,1),"pessimistic":(2,1)}

def replay(row,error):
    g=row["feeder_arrival"]+row["walk"]-row["connector_depart"]
    pred=g+error
    decision=not row["cancelled"] and 0<pred<=CAP
    # Dispatcher can wait up to CAP once the hold is authorized, then leaves.
    hold=min(CAP,max(0,g)) if decision else 0
    caught=not row["cancelled"] and g<=hold
    base_caught=not row["cancelled"] and g<=0
    departure_wait=(hold-g) if caught else row["next_headway"]-g
    base_wait=-g if base_caught else row["next_headway"]-g
    assert min(base_wait,departure_wait)>=0
    saved=(base_wait-departure_wait)*row["transfer_n"]
    onboard=hold*row["onboard_n"]
    return dict(gap=g,error=error,forecast=pred,actual_hold=hold,additional_caught=(int(caught)-int(base_caught))*row["transfer_n"],
                saved_transfer_pm=saved,onboard_delay_pm=onboard,net_pm=saved-onboard,
                empty_hold=int(hold>0 and not caught))

with (ROOT/"new_service_days.csv").open(encoding="utf-8") as fp:
    rows=[{k:int(v) if k!="scenario" else v for k,v in r.items()} for r in csv.DictReader(fp)]
assert len(rows)==90
# Independent hand checks: a late feeder predicted in range creates an empty hold.
probe=dict(feeder_arrival=2,walk=2,connector_depart=0,transfer_n=5,onboard_n=7,next_headway=10,cancelled=0)
assert replay(probe,-2)["net_pm"]==-14 and replay(probe,-2)["empty_hold"]==1
assert replay(probe,0)["net_pm"]==0
keys=["additional_caught","saved_transfer_pm","onboard_delay_pm","net_pm","empty_hold"]
records=[];examples=[]
for rep in range(200):
    gen=random.Random(4109+rep)
    noises=[gen.gauss(0,1) for row in rows]
    for name,(bias,sigma) in SCENARIOS.items():
        totals={k:0 for k in keys};bygroup=defaultdict(lambda:{k:0 for k in keys})
        for row,z in zip(rows,noises):
            result=replay(row,round(bias+sigma*z))
            if rep==0:examples.append(dict(model=name,scenario=row["scenario"],day=row["day"],**result))
            for k in keys:
                totals[k]+=result[k];bygroup[row["scenario"]][k]+=result[k]
        records.append(dict(repeat=rep,model=name,scope="ALL",**totals))
        for group,sub in bygroup.items():records.append(dict(repeat=rep,model=name,scope=group,**sub))
def dump_csv(fn,items):
    with (ROOT/fn).open("w",newline="",encoding="utf-8") as fp:
        w=csv.DictWriter(fp,fieldnames=items[0].keys());w.writeheader();w.writerows(items)
dump_csv("paired_repeats.csv",records);dump_csv("day_trace_rep0.csv",examples)
output={}
for name in SCENARIOS:
    batch=[r for r in records if r["model"]==name and r["scope"]=="ALL"]
    a=sorted(r["net_pm"] for r in batch)
    output[name]={"net_pm_p10":a[19],"net_pm_median":median(a),"net_pm_p90":a[179],
                  "avg_empty_hold_days":round(mean(r["empty_hold"] for r in batch),2),
                  "avg_additional_caught":round(mean(r["additional_caught"] for r in batch),2)}
(ROOT/"results.json").write_text(json.dumps(output,indent=2),encoding="utf-8")
print(json.dumps(output))
