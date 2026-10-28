"""Phase-1A-2 analysis: per-function paired comparisons."""
import json, statistics, sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ms = sorted((ROOT/"results"/"agent_assisted_ec").glob("manifest_a2-*.json"), key=lambda p: p.stat().st_mtime)
man = json.loads(ms[-1].read_text(encoding="utf-8"))
rows = [r for r in man["rows"] if r.get("status") == "ok"]
print("run_id", man["run_id"], "agent_mechs", len(man.get("agent_mechanisms", [])))
print("proposal_stats", man.get("proposal_stats"))
for i, spec in enumerate(man.get("agent_mechanisms", [])):
    print(f"MECH {spec['mechanism_id']}: {spec.get('description','')[:100]}")
    for r in spec.get("rules", [])[:4]:
        print("   ", r)

by = defaultdict(dict)
for r in rows:
    by[(r["function_id"], r["seed"])][r["arm"]] = r["metric"]

methods = sorted({r["arm"] for r in rows})
print("\n=== metrics (lower better) ===")
hdr = "func seed | " + " | ".join(m[:12] for m in methods)
print(hdr)
for k in sorted(by):
    print(k, "|", " | ".join(f"{by[k].get(m, float('nan')):.4g}" if m in by[k] else "-" for m in methods))

print("\n=== median ===")
for m in methods:
    vals = [v[m] for v in by.values() if m in v]
    if vals:
        print(f"{m}: n={len(vals)} median={statistics.median(vals):.6g}")

def paired(a, b):
    w=l=t=0
    for k,v in by.items():
        if a not in v or b not in v: continue
        if v[a] < v[b]-1e-12: w+=1
        elif v[a] > v[b]+1e-12: l+=1
        else: t+=1
    return w,l,t

print("\n=== agent_mech_1 paired (W-L-T) ===")
for other in methods:
    if other == "agent_mech_1": continue
    print(f"vs {other}: {paired('agent_mech_1', other)}")

print("\n=== best per run ===")
for k,v in sorted(by.items()):
    best = min(v.items(), key=lambda kv: kv[1])
    print(k, "best=", best[0], f"{best[1]:.4g}")
