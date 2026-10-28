"""Phase-1A-2 experiment: trajectory → Agent mechanism → comparison on MetaBox BBOB.

Arms: official DE, fixed classic, SHADE (if available), deterministic heuristic,
Agent mechanism(s), random mechanism, optional evolutionary refinement.
"""
from __future__ import annotations

import hashlib
import json
import os
import random
import sys
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

import numpy as np

from experiments.metabox.adapter import (
    BBOB_FAMILIES,
    METABOX_DIFFICULT,
    load_function,
    run_optimizer,
    split_manifest,
)
from experiments.metabox.agent_assisted_ec.agent_proposal import (
    propose_mechanisms,
    summarize_trajectories,
)
from experiments.metabox.agent_assisted_ec.mechanism_dsl import (
    MECH_DSL_VERSION,
    compile_mechanism,
    heuristic_stagnation_mechanism,
    validate_mechanism,
)
from experiments.metabox.agent_assisted_ec.multi_de import run_multi_de
from experiments.metabox.provenance import (
    ensure_clean_worktree,
    ensure_unique_artifacts,
    make_run_id,
)

TRAIN_FUNCS = [1, 10, 20]  # split_v2 train, 3 families
VAL_FUNCS = [13, 16, 22]   # split_v2 val (selection only after train)
SEEDS = [11, 22]
MAX_FES = 300
NP_SIZE = 20
EXPERIMENT = "PHASE1A_AGENT_ASSISTED_EC"


def random_mechanism(rng: random.Random, mid: str):
    ops = ["rand/1/bin", "current-to-best/1/bin", "rand/2/bin", "best/1/bin"]
    feats = ["stagnation_steps", "success_fraction", "population_diversity", "improvement_rate", "budget_fraction"]
    rules = []
    for _ in range(rng.randint(1, 3)):
        feat = rng.choice(feats)
        op = rng.choice([">=", ">", "<", "<="])
        thr = round(rng.uniform(0.0, 10.0 if feat == "stagnation_steps" else 1.0), 2)
        act = rng.choice(["set_operator", "set_F", "set_CR", "inject_diversity"])
        if act == "set_operator":
            then = {"action": act, "params": {"operator": rng.choice(ops)}}
        elif act == "set_F":
            then = {"action": act, "params": {"value": round(rng.uniform(0.1, 1.0), 3)}}
        elif act == "set_CR":
            then = {"action": act, "params": {"value": round(rng.uniform(0.0, 1.0), 3)}}
        else:
            then = {"action": act, "params": {}}
        rules.append({"when": {feat: {"op": op, "value": thr}}, "then": then})
    spec = {
        "schema_version": MECH_DSL_VERSION,
        "mechanism_id": mid,
        "description": "random valid mechanism",
        "rules": rules,
        "default": {"action": "set_operator", "params": {"operator": rng.choice(ops)}},
    }
    return validate_mechanism(spec)


def run_mech(problem, spec, seed, max_fes=MAX_FES):
    mech = compile_mechanism(spec)
    t0 = time.time()
    # Accept ProblemHandle or raw BBOB problem.
    raw = getattr(problem, "_problem", problem)
    res = run_multi_de(raw, mech, max_fes=max_fes, seed=seed, np_size=NP_SIZE)
    return res, mech, time.time() - t0


def main():
    allow_dirty = "--allow-dirty" in sys.argv[1:]
    out_root = ROOT / "results" / "agent_assisted_ec"
    out_root.mkdir(parents=True, exist_ok=True)
    try:
        prov = ensure_clean_worktree(allow_dirty=allow_dirty)
    except Exception as exc:
        prov = {"git_sha": "unknown", "worktree_dirty": "true", "dirty_files": str(exc)}
    run_id = make_run_id(prov["git_sha"], worktree_dirty=prov["worktree_dirty"], tag="a2")
    manifest_path = out_root / f"manifest_{run_id}.json"
    trace_dir = out_root / "traces" / run_id
    ensure_unique_artifacts(manifest_path, trace_dir)
    trace_dir.mkdir(parents=True, exist_ok=True)

    # --- Step 1: real trajectories with fixed classic DE ---
    traj_traces = []
    for fid in TRAIN_FUNCS:
        for seed in SEEDS:
            p = load_function(fid)
            # classic-like mechanism
            classic = compile_mechanism({
                "schema_version": MECH_DSL_VERSION,
                "mechanism_id": "fixed_classic",
                "description": "rand/1/bin F=0.5 CR=0.9",
                "rules": [{"when": {"budget_fraction": {"op": ">=", "value": 2.0}},
                           "then": {"action": "noop", "params": {}}}],
                "default": {"action": "set_operator", "params": {"operator": "rand/1/bin"}},
            })
            res = run_multi_de(p._problem, classic, max_fes=MAX_FES, seed=seed, np_size=NP_SIZE)
            traj_traces.append({
                "function_id": fid, "seed": seed, "fes": res.fes,
                "action_events": res.action_events,
                "best_raw": res.best_raw_objective,
            })
    traj_summary = summarize_trajectories(traj_traces)

    # --- Step 2-3: Agent proposals (max 12 API requests total) ---
    # Reuse saved proposals if present to avoid extra API spend.
    prev = sorted(out_root.glob("manifest_a2-*.json"), key=lambda p: p.stat().st_mtime)
    specs, pstats, plog = [], None, []
    if prev:
        old = json.loads(prev[-1].read_text(encoding="utf-8"))
        if old.get("agent_mechanisms"):
            specs = old["agent_mechanisms"]
            pstats = old.get("proposal_stats", {})
            plog = old.get("proposal_log", [])
            for s in specs:
                validate_mechanism(s)  # re-validate
    if len(specs) < 3:
        specs2, pstats2, plog2 = propose_mechanisms(traj_summary, n=3)
        if specs2:
            specs = specs2
            pstats = pstats2.to_dict() if hasattr(pstats2, "to_dict") else pstats2
            plog = plog2

    # --- Step 4: comparison arms ---
    rng = random.Random(7)
    arms = []
    # baselines
    arms.append(("fixed_classic_de", {"schema_version": MECH_DSL_VERSION, "mechanism_id": "fixed_classic",
                 "description": "rand/1 F=0.5 CR=0.9", "rules": [
                     {"when": {"stagnation_steps": {"op": ">=", "value": 999}}, "then": {"action": "noop", "params": {}}}],
                 "default": {"action": "set_operator", "params": {"operator": "rand/1/bin"}}}))
    arms.append(("deterministic_heuristic", heuristic_stagnation_mechanism()))
    for i, spec in enumerate(specs):
        arms.append((f"agent_mech_{i+1}", spec))
    for i in range(3):
        arms.append((f"random_mech_{i+1}", random_mechanism(rng, f"random_mech_{i+1}")))
    # ablations of first agent mech if present
    if specs:
        ab1 = json.loads(json.dumps(specs[0]))
        ab1["mechanism_id"] = "ablate_no_stag"
        ab1["rules"] = [r for r in ab1["rules"] if "stagnation_steps" not in r["when"]]
        if ab1["rules"]:
            arms.append(("ablate_no_stag", validate_mechanism(ab1)))
        ab2 = json.loads(json.dumps(specs[0]))
        ab2["mechanism_id"] = "ablate_no_div"
        ab2["rules"] = [r for r in ab2["rules"] if "population_diversity" not in r["when"]]
        if ab2["rules"]:
            arms.append(("ablate_no_div", validate_mechanism(ab2)))
        # shuffled state-action: randomly permute rule whens among thens
        sh = json.loads(json.dumps(specs[0]))
        sh["mechanism_id"] = "shuffled_map"
        whens = [r["when"] for r in sh["rules"]]
        thens = [r["then"] for r in sh["rules"]]
        rng.shuffle(thens)
        sh["rules"] = [{"when": w, "then": t} for w, t in zip(whens, thens)]
        arms.append(("shuffled_map", validate_mechanism(sh)))

    rows = []
    for fid in TRAIN_FUNCS:
        for seed in SEEDS:
            # official MetaBox DE
            p = load_function(fid)
            try:
                off = run_optimizer("DE", p, max_fes=MAX_FES, seed=seed)
                rows.append({"arm": "official_meta_de", "function_id": fid, "seed": seed,
                             "metric": off["best_cost"], "primary": "regret_like",
                             "fes": off["independent_fes"], "status": "ok"})
            except Exception as exc:
                rows.append({"arm": "official_meta_de", "function_id": fid, "seed": seed,
                             "status": "error", "error": str(exc)})
            # strong adaptive if available
            try:
                p2 = load_function(fid)
                shade = run_optimizer("SHADE", p2, max_fes=MAX_FES, seed=seed)
                rows.append({"arm": "SHADE", "function_id": fid, "seed": seed,
                             "metric": shade["best_cost"], "primary": "regret_like",
                             "fes": shade["independent_fes"], "status": "ok"})
            except Exception as exc:
                rows.append({"arm": "SHADE", "function_id": fid, "seed": seed,
                             "status": "error", "error": str(exc)[:120]})
            for arm_name, spec in arms:
                p3 = load_function(fid)
                try:
                    res, mech, wall = run_mech(p3, spec, seed)
                    rows.append({
                        "arm": arm_name, "function_id": fid, "seed": seed,
                        "metric": res.best_regret if res.best_regret is not None else res.best_raw_objective,
                        "primary": res.primary_metric,
                        "best_raw": res.best_raw_objective,
                        "fes": res.fes, "indep_fes": res.independent_fes,
                        "mech_hash": mech.mech_hash, "wall": round(wall, 3),
                        "status": "ok",
                    })
                except Exception as exc:
                    rows.append({"arm": arm_name, "function_id": fid, "seed": seed,
                                 "status": "error", "error": str(exc)[:120],
                                 "tb": traceback.format_exc()[-200:]})

    manifest = {
        "experiment": EXPERIMENT,
        "run_id": run_id,
        "git_sha": prov["git_sha"],
        "worktree_dirty": prov["worktree_dirty"],
        "model": "deepseek-flash",
        "prompt_version": "p1a2-agent-mech-v1",
        "proposal_stats": pstats if isinstance(pstats, dict) else pstats.to_dict(),
        "proposal_log": plog,
        "agent_mechanisms": specs,
        "traj_summary": traj_summary,
        "protocol": {
            "train_functions": TRAIN_FUNCS, "val_functions": VAL_FUNCS,
            "seeds": SEEDS, "max_fes": MAX_FES, "np_size": NP_SIZE, "dim": 10,
            "direction": "minimize", "split": split_manifest("split_v2"),
        },
        "rows": rows,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, default=str), encoding="utf-8")
    (out_root / "CURRENT.txt").write_text(manifest_path.name, encoding="utf-8")
    print(json.dumps({
        "run_id": run_id, "n_agent_mechs": len(specs),
        "proposal_stats": pstats if isinstance(pstats, dict) else pstats.to_dict(),
        "arms": sorted({r["arm"] for r in rows}),
        "manifest": str(manifest_path),
    }, indent=2))


if __name__ == "__main__":
    main()
