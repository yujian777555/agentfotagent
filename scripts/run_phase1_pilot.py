"""Phase-1 pipeline pilot: target-only vs transfer vs shuffled vs random.

PRE-ACCEPTANCE debug pilot. Not confirmatory science. Mock-backed AES policy.
"""
from __future__ import annotations

import json
import platform
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agentfotagent.evolution.conventional_ea import ConventionalEA
from agentfotagent.evolution.harness import BaselineHarness
from agentfotagent.evolution.random_search import RandomSearch
from agentfotagent.genome.schema import GenomeSpace
from agentfotagent.tasks.generators import generate_task
from agentfotagent.transfer.source_prior import SOURCE_ALLELE_WEIGHTS, shuffled_weights
from agentfotagent.transfer.transfer_ea import TransferEA

import random


def build_tasks():
    # Train families only (key_crate + dial_set), small seed set for pilot.
    tasks = []
    for fam in ("key_crate", "dial_set"):
        for seed in (1, 2, 3):
            tasks.append(generate_task(fam, seed, "train"))
    return tasks


def run_arm(name, algorithm, tasks, space, budget, seed):
    harness = BaselineHarness(tasks=tasks, space=space, config={"protocol": f"phase1-pilot-{name}-s{seed}"})
    t0 = time.time()
    art = harness.run_and_collect(algorithm, budget)
    elapsed = time.time() - t0
    records = harness._last_records
    best = max((r.success_rate for r in records), default=0.0)
    return {
        "arm": name,
        "seed": seed,
        "budget": budget,
        "best_success_rate": best,
        "mean_success_rate": sum(r.success_rate for r in records) / max(1, len(records)),
        "accounting": art["accounting"],
        "wall_seconds": round(elapsed, 4),
        "run_id": art.get("run_id"),
    }


def main():
    tasks = build_tasks()
    space = GenomeSpace()
    budget = 12
    seeds = (11, 22, 33)
    rows = []
    for seed in seeds:
        rng = random.Random(seed)
        shuf = shuffled_weights(rng)
        arms = [
            ("random_search", RandomSearch(space, seed=seed)),
            ("target_only_ea", ConventionalEA(space, seed=seed, mu=3, lam=3)),
            ("transfer_ea", TransferEA(space, seed=seed, mu=3, lam=3, weights=SOURCE_ALLELE_WEIGHTS)),
            ("shuffled_mapping", TransferEA(space, seed=seed, mu=3, lam=3, weights=shuf)),
        ]
        for name, algo in arms:
            rows.append(run_arm(name, algo, tasks, space, budget, seed))

    # Aggregate best per arm across pilot seeds.
    agg = {}
    for r in rows:
        agg.setdefault(r["arm"], []).append(r["best_success_rate"])
    summary = {
        "phase": "phase1-pipeline-pilot",
        "not_confirmatory": True,
        "phase0_accepted": False,
        "python": sys.version,
        "platform": platform.platform(),
        "budget": budget,
        "seeds": list(seeds),
        "tasks": [t.task_id for t in tasks],
        "arms": {k: {"best_rates": v, "max": max(v), "mean": sum(v) / len(v)} for k, v in agg.items()},
        "rows": rows,
    }

    # Decision heuristic (pilot only).
    transfer_max = summary["arms"].get("transfer_ea", {}).get("max", 0)
    target_max = summary["arms"].get("target_only_ea", {}).get("max", 0)
    shuf_max = summary["arms"].get("shuffled_mapping", {}).get("max", 0)
    if transfer_max > target_max and transfer_max > shuf_max:
        summary["pilot_decision"] = "CONTINUE_TO_EXPAND_SCALE"
    elif transfer_max > target_max and shuf_max >= transfer_max:
        summary["pilot_decision"] = "NO_GO_MAPPING_ARTIFACT"
    else:
        summary["pilot_decision"] = "NO_GO_OR_PIVOT"

    out_dir = ROOT / "results" / "pilot_phase1"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "pilot_results.json"
    path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"arms": summary["arms"], "pilot_decision": summary["pilot_decision"]}, indent=2))
    print("wrote", path)


if __name__ == "__main__":
    main()
