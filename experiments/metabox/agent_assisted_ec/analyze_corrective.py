"""Phase-1A-2R analysis: paired stats, rule triggers, random distribution."""
import json, statistics
from collections import defaultdict, Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
man = json.loads((ROOT/"results"/"agent_assisted_ec_corrective"/"manifest_a2r-a0f435e328d1-clean-20261028T122041.json").read_text(encoding="utf-8"))
rows = [r for r in man["rows"] if r.get("status")=="ok"]
by = defaultdict(dict)
for r in rows:
    by[(r["function_id"], r["seed"])][r["arm"]] = r

def paired(a, b, key="metric"):
    w=l=t=0
    for v in by.values():
        if a not in v or b not in v: continue
        va, vb = v[a][key], v[b][key]
        if va<vb-1e-12: w+=1
        elif va>vb+1e-12: l+=1
        else: t+=1
    return w,l,t

def med(arm):
    vals=[v[arm]["metric"] for v in by.values() if arm in v]
    return statistics.median(vals) if vals else float("nan")

arms = sorted({r["arm"] for r in rows})
print("=== median metric (lower better) ===")
for a in arms:
    if a.startswith("random_mech") and a != "random_mech_00":
        continue
    print(f"{a}: {med(a):.6g}")
rand_meds = [med(f"random_mech_{i:02d}") for i in range(20)]
print(f"random_mech median-of-medians: {statistics.median(rand_meds):.6g}")
print(f"random_mech best-of-20: {min(rand_meds):.6g}  worst: {max(rand_meds):.6g}")

print("\n=== agent_mech_3 paired W-L-T ===")
for other in ["fixed_classic", "deterministic", "official_meta_de", "SHADE", "shuffled_map", "ablate_no_stag", "ablate_no_div"]:
    print(f"vs {other}: {paired('agent_mech_3', other)}")
wins_rand = [paired("agent_mech_3", f"random_mech_{i:02d}") for i in range(20)]
print("vs 20 random mechs: mean W", sum(w for w,_,_ in wins_rand)/20,
      "mean L", sum(l for _,l,_ in wins_rand)/20)
better_than_rand = sum(1 for w,l,_ in wins_rand if w>l)
print("random mechs where mech_3 wins more than loses:", better_than_rand, "/20")

print("\n=== per-function mech_3 vs deterministic / random_best ===")
for fid in [1,2,4,6,7,10,11,12,15,18,20,21]:
    w1,l1,t1 = 0,0,0
    w2,l2,t2 = 0,0,0
    for (f,s),v in by.items():
        if f!=fid: continue
        va, vd = v["agent_mech_3"]["metric"], v["deterministic"]["metric"]
        if va<vd-1e-12: w1+=1
        elif va>vd+1e-12: l1+=1
        else: t1+=1
        vr = min(v[f"random_mech_{i:02d}"]["metric"] for i in range(20))
        if va<vr-1e-12: w2+=1
        elif va>vr+1e-12: l2+=1
        else: t2+=1
    print(f"F{fid}: vs det {w1}-{l1}-{t1}  vs best-random {w2}-{l2}-{t2}")

print("\n=== mech_3 rule triggers & operators (aggregate) ===")
rule_c = Counter(); op_c = Counter(); inj = 0; inj_ok = 0
for r in rows:
    if r["arm"] != "agent_mech_3": continue
    op_c.update(r.get("operator_counts") or {})
    inj += r.get("n_inject", 0)
    for ev in r.get("inject_events") or []:
        inj_ok += ev.get("resampled", 0)
print("operators", dict(op_c))
print("inject events", inj, "total resampled", inj_ok)

print("\n=== FE exactness ===")
print(all(r["fes"]==300 and r["indep_fes"]==300 for r in rows if "indep_fes" in r))
print("traces", len(man["traces"]), "frozen mech hash", man["frozen_mech3_hash"][:16])
