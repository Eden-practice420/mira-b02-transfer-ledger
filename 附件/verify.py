"""Hand checks, unserved trips and counterfactual replay consistency."""
import json
import subprocess
import sys
from pathlib import Path
from analyze import replay

ROOT=Path(__file__).resolve().parent
toy={"stop":"X","day":"1","feeder_arrival":"1","connector_depart":"1","walk":"2","transfer_n":"5","onboard_n":"9","next_headway":"15","cancelled":"0"}
assert replay([toy],0)["summary"]["cost_pm"] == 65
assert replay([toy],2)["summary"]["cost_pm"] == 18
toy["cancelled"]="1"
assert replay([toy],3)["summary"]["caught"] == 0
raw=subprocess.check_output([sys.executable,"-X","utf8",str(ROOT/"analyze.py"),str(ROOT/"service_days.csv")],encoding="utf-8")
data=json.loads(raw)
for stop,caps in data.items():
    for cap,obj in caps.items():
        assert all(0 <= row["hold"] <= int(cap) and not(row["cancelled"] and row["hold"]) for row in obj["days"])
    assert all(caps[str(i)]["summary"]["caught"] <= caps[str(i+1)]["summary"]["caught"] for i in range(3))
(ROOT/"replay.json").write_text(raw,encoding="utf-8")
summary={stop:{c:v["summary"] for c,v in cc.items()} for stop,cc in data.items()}
(ROOT/"result.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(summary,ensure_ascii=False))
