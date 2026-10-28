"""Validation check for agent_mech_3 vs key baselines (split_v2 val)."""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from experiments.metabox.adapter import load_function
from experiments.metabox.agent_assisted_ec.mechanism_dsl import compile_mechanism
from experiments.metabox.agent_assisted_ec.multi_de import run_multi_de

VAL = [13, 16, 22]
SEEDS = [11, 22]
MAX_FES = 300
NP = 20

ms = sorted((ROOT/"results"/"agent_assisted_ec").glob("manifest_a2-*.json"), key=lambda p: p.stat().st_mtime)
man = json.loads(ms[-1].read_text(encoding="utf-8"))
mech_specs = {s["mechanism_id"]: s for s in man["agent_mechanisms"]}
# baselines
fixed = {"schema_version": "aes-mech-dsl-v1", "mechanism_id": "fixed_classic",
         "description": "", "rules": [{"when": {"stagnation_steps": {"op": ">=", "value": 999}}, "then": {"action": "noop", "params": {}}}],
         "default": {"action": "set_operator", "params": {"operator": "rand/1/bin"}}}
det = json.loads(json.dumps(mech_specs.get("agent_mech_3")))  # placeholder replaced below
from experiments.metabox.agent_assisted_ec.mechanism_dsl import heuristic_stagnation_mechanism
det = heuristic_stagnation_mechanism()

arms = [("fixed_classic", fixed), ("deterministic", det), ("agent_mech_3", mech_specs["agent_mech_3"])]
# random control
import random
rng = random.Random(99)
from experiments.metabox.agent_assisted_ec.run_experiment import random_mechanism
arms.append(("random_mech", random_mechanism(rng, "val_random")))

rows = []
for fid in VAL:
    for seed in SEEDS:
        for name, spec in arms:
            p = load_function(fid)
            m = compile_mechanism(spec)
            res = run_multi_de(p._problem, m, max_fes=MAX_FES, seed=seed, np_size=NP)
            metric = res.best_regret if res.best_regret is not None else res.best_raw_objective
            rows.append({"arm": name, "fid": fid, "seed": seed, "metric": metric, "fes": res.fes})
            print(name, "F"+str(fid), seed, metric)

out = ROOT/"results"/"agent_assisted_ec"/"validation_a2.json"
out.write_text(json.dumps({"rows": rows}, indent=2), encoding="utf-8")
print("WROTE", out)

def paired(a,b):
    w=l=t=0
    for fid in VAL:
        for seed in SEEDS:
            va = next(r["metric"] for r in rows if r["arm"]==a and r["fid"]==fid and r["seed"]==seed)
            vb = next(r["metric"] for r in rows if r["arm"]==b and r["fid"]==fid and r["seed"]==seed)
            if va<vb-1e-12: w+=1
            elif va>vb+1e-12: l+=1
            else: t+=1
    return w,l,t
print("agent_mech_3 vs fixed", paired("agent_mech_3","fixed_classic"))
print("agent_mech_3 vs det", paired("agent_mech_3","deterministic"))
print("agent_mech_3 vs random", paired("agent_mech_3","random_mech"))
