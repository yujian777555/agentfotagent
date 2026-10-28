"""Phase-1A-3 lightweight empirical check: operator credit confounding in A2R traces.

Supports: whether raw success-rate comparison of operators is confounded by
the state in which they were applied (stagnation-triggered switch).
Does NOT support: causal claims; synthetic not used here; no test split.
"""
import json, statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRACE_DIR = ROOT / "results" / "agent_assisted_ec_corrective" / "traces" / "a2r-a0f435e328d1-clean-20261028T122041"

rows = []
for f in TRACE_DIR.glob("agent_mech_3_*.json"):
    obj = json.loads(f.read_text(encoding="utf-8"))
    for ev in obj["payload"]["action_events"]:
        rows.append({
            "fid": obj["function_id"],
            "seed": obj["seed"],
            "stag": ev["state"].get("stagnation_steps", 0),
            "op": ev.get("operator"),
            "succ": ev.get("success_fraction_this_gen"),
            "imp": ev["state"].get("improvement_rate", 0),
            "div": ev["state"].get("population_diversity", 0),
            "budget": ev["state"].get("budget_fraction", 0),
        })

print("total gens", len(rows), "runs", len({(r['fid'],r['seed']) for r in rows}))
by_op = defaultdict(list)
for r in rows:
    by_op[r["op"]].append(r["succ"])
print("=== raw success rate by operator (naive) ===")
for op, vals in by_op.items():
    print(f"{op}: n={len(vals)} mean_suc={statistics.mean(vals):.4f}")

# confound: distribution of stagnation when each operator is used
print("=== state distribution by operator ===")
for op in by_op:
    sub = [r for r in rows if r["op"] == op]
    print(f"{op}: stag_mean={statistics.mean(r['stag'] for r in sub):.1f} "
          f"stag_med={statistics.median(r['stag'] for r in sub):.1f} "
          f"div_mean={statistics.mean(r['div'] for r in sub):.1f} "
          f"budget_mean={statistics.mean(r['budget'] for r in sub):.2f}")

# within-state comparison: bucket by stag>=5 vs <5
print("=== within-bucket success rates ===")
for bucket_name, pred in (("stag<5", lambda r: r["stag"] < 5), ("stag>=5", lambda r: r["stag"] >= 5)):
    for op in ("rand/1/bin", "rand/2/bin"):
        vals = [r["succ"] for r in rows if r["op"] == op and pred(r)]
        if vals:
            print(f"{bucket_name:8} {op}: n={len(vals)} mean={statistics.mean(vals):.4f}")

# first-match effect: when both stag and div could fire
both = [r for r in rows if r["stag"] >= 5 and r["div"] <= 30]
print("gen where stag>=5 AND div<=30:", len(both), "-> op:", {r['op'] for r in both})
div_only = [r for r in rows if r["stag"] < 5 and r["div"] <= 30]
print("gen where stag<5 AND div<=30 (inject eligible):", len(div_only))

out = {
    "n_generations": len(rows),
    "raw_succ_by_op": {k: statistics.mean(v) for k, v in by_op.items()},
    "note": "descriptive only; operator assignment is policy-triggered, not randomized",
}
(ROOT / "results" / "phase1a3").mkdir(parents=True, exist_ok=True)
(ROOT / "results" / "phase1a3" / "credit_confound_check.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
print("WROTE results/phase1a3/credit_confound_check.json")
