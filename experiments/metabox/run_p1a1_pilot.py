"""P1A-1 pilot runner: 6 methods × 3 train functions × 2 seeds.

Methods:
1. official_meta_de  — MetaBox DE (external baseline implementation)
2. fixed_classic_de  — controlled DE F=0.5 CR=0.9
3. fixed_explore_de  — controlled DE exploration controller
4. stagnation_heuristic — deterministic stagnation rule (no LLM)
5. random_valid_controller — seeded random DSL actions
6. llm_agent — DeepSeek agent selecting DSL actions from live state

All methods 2-6 share controlled_de; official DE is a separate implementation
(comparison is labeled accordingly).
"""
from __future__ import annotations

import json
import os
import sys
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402

from experiments.metabox.adapter import (  # noqa: E402
    BBOB_FAMILIES,
    METABOX_DIFFICULT,
    config_hash,
    import_metabox,
    load_function,
    run_optimizer,
    split_manifest,
)
from experiments.metabox.controller_dsl import (  # noqa: E402
    compile_controller,
    fixed_controller_a,
    fixed_controller_b,
)
from experiments.metabox.controlled_de import run_controlled_de  # noqa: E402
from experiments.metabox.p1a1_agent_controller import (  # noqa: E402
    AgentAPIError,
    BudgetExceeded,
    LLMBackend,
    LLMStats,
    P1A1AgentController,
)
from experiments.metabox.provenance import (  # noqa: E402
    DirtyWorktreeError,
    ensure_clean_worktree,
    ensure_unique_artifacts,
    make_run_id,
)

# split_v2 train: [1,2,4,6,7,10,11,12,15,18,20,21]
# Pick 3 covering families + at least one difficult:
#   F1 separable (difficult), F10 high_conditioning (easy), F20 multimodal_weak (easy)
FUNCTIONS = [1, 10, 20]
SEEDS = [11, 22]
MAX_FES = 300
NP_SIZE = 20
EXPERIMENT = "P1A1_AGENT_DE_PILOT"


class StagnationHeuristicController:
    controller_id = "stagnation_heuristic"
    controller_hash = "static-stag-heuristic-v1"

    def select_action(self, state):
        if float(state.get("stagnation_steps", 0)) >= 5.0:
            return {"action": "set_F", "params": {"value": 0.9}}
        if float(state.get("budget_fraction", 0)) >= 0.8:
            return {"action": "set_CR", "params": {"value": 0.2}}
        return {"action": "set_F", "params": {"value": 0.5}}


class RandomValidController:
    def __init__(self, seed: int) -> None:
        self.controller_id = f"random_valid_{seed}"
        self.controller_hash = f"static-random-{seed}"
        self.rng = np.random.RandomState(seed)

    def select_action(self, state):
        kind = int(self.rng.randint(0, 3))
        if kind == 0:
            return {"action": "set_F", "params": {"value": float(self.rng.uniform(0.1, 1.0))}}
        if kind == 1:
            return {"action": "set_CR", "params": {"value": float(self.rng.uniform(0.0, 1.0))}}
        return {"action": "noop", "params": {}}


def build_methods(llm_available: bool):
    ctrl_a = compile_controller(fixed_controller_a())
    ctrl_b = compile_controller(fixed_controller_b())
    methods = []
    methods.append(("official_meta_de", "official", None))
    methods.append(("fixed_classic_de", "controlled", ctrl_a))
    methods.append(("fixed_explore_de", "controlled", ctrl_b))
    methods.append(("stagnation_heuristic", "controlled", StagnationHeuristicController()))
    methods.append(("random_valid_controller", "controlled", RandomValidController(7)))
    if llm_available:
        methods.append(("llm_agent", "controlled", "LLM"))
    return methods


def main() -> int:
    allow_dirty = "--allow-dirty" in sys.argv[1:]
    out_root = ROOT / "results" / "p1a1_pilot"
    out_root.mkdir(parents=True, exist_ok=True)

    try:
        prov = ensure_clean_worktree(allow_dirty=allow_dirty)
    except DirtyWorktreeError as exc:
        print("DIRTY WORKTREE:", exc)
        prov = {"git_sha": "unknown", "worktree_dirty": "true", "dirty_files": str(exc)}

    run_id = make_run_id(prov["git_sha"], worktree_dirty=prov["worktree_dirty"], tag="p1a1")
    manifest_path = out_root / f"manifest_{run_id}.json"
    trace_dir = out_root / "traces" / run_id
    ensure_unique_artifacts(manifest_path, trace_dir)
    trace_dir.mkdir(parents=True, exist_ok=True)

    api_key = os.environ.get("DEEPSEEK_API_KEY") or ""
    llm_available = bool(api_key)
    backend = LLMBackend(api_key=api_key, model="deepseek-flash") if llm_available else None
    llm_status = "AVAILABLE" if llm_available else "LLM_EXPERIMENT_BLOCKED"

    methods = build_methods(llm_available)
    mb = import_metabox()

    rows = []
    failures = []
    for fid in FUNCTIONS:
        problem_meta = {
            "function_id": fid,
            "family": BBOB_FAMILIES[fid],
            "difficulty": "difficult" if fid in METABOX_DIFFICULT else "easy",
        }
        for seed in SEEDS:
            for method_name, path, ctrl in methods:
                t0 = time.time()
                try:
                    if path == "official":
                        p = load_function(fid)
                        # Official DE has no live controller hook; use default F/Cr.
                        result = run_optimizer("DE", p, max_fes=MAX_FES, seed=seed, controller=None)
                        row = {
                            "method": method_name,
                            "path": "official_meta_de",
                            **problem_meta,
                            "seed": seed,
                            "max_fes": MAX_FES,
                            "reported_fes": result["reported_fes"],
                            "independent_fes": result["independent_fes"],
                            "best_raw_objective": result["best_cost"],
                            "best_regret": result["best_cost"],  # official cost is already regret-like
                            "primary_metric": "regret_like_official_cost",
                            "cost_curve_tail": result["cost_curve"][-5:],
                            "n_action_events": 0,
                            "action_events": [],
                            "llm_stats": None,
                            "wall_seconds": round(time.time() - t0, 4),
                            "status": "ok",
                        }
                    else:
                        p = load_function(fid)
                        if ctrl == "LLM":
                            agent = P1A1AgentController(backend)
                            # Inject current F/CR into state for the agent prompt.
                            class AgentWrapper:
                                def __init__(self, a):
                                    self.a = a
                                    self.controller_id = a.controller_id
                                    self.controller_hash = a.controller_hash

                                def select_action(self, state):
                                    s = dict(state)
                                    s.setdefault("F", 0.5)
                                    s.setdefault("CR", 0.5)
                                    return self.a.select_action(s)

                            ctrl_obj = AgentWrapper(agent)
                        else:
                            ctrl_obj = ctrl
                            agent = None
                        res = run_controlled_de(
                            p._problem, ctrl_obj, max_fes=MAX_FES, seed=seed, np_size=NP_SIZE
                        )
                        row = {
                            "method": method_name,
                            "path": "controlled_de",
                            **problem_meta,
                            "seed": seed,
                            "max_fes": MAX_FES,
                            "reported_fes": res.fes,
                            "independent_fes": res.independent_fes,
                            "init_fes": res.init_fes,
                            "best_raw_objective": res.best_raw_objective,
                            "best_regret": res.best_regret,
                            "primary_metric": res.primary_metric,
                            "cost_curve_tail": res.cost_curve[-5:],
                            "n_action_events": len(res.action_events),
                            "action_events": res.action_events,
                            "applied_F_history": res.applied_F_history,
                            "applied_CR_history": res.applied_CR_history,
                            "llm_stats": (backend.stats.to_dict() if agent else None),
                            "wall_seconds": round(time.time() - t0, 4),
                            "status": "ok",
                        }
                        # full trace
                        tp = trace_dir / f"{method_name}_F{fid}_seed{seed}.json"
                        tp.write_text(
                            json.dumps(
                                {
                                    "run_id": run_id,
                                    "git_sha": prov["git_sha"],
                                    "method": method_name,
                                    "function_id": fid,
                                    "seed": seed,
                                    "payload": res.to_manifest_dict(),
                                    "llm_events": agent.events if agent else None,
                                },
                                sort_keys=True,
                                default=str,
                            ),
                            encoding="utf-8",
                        )
                        import hashlib

                        row["trace_path"] = str(tp.relative_to(ROOT)).replace("\\", "/")
                        row["trace_sha256"] = hashlib.sha256(tp.read_bytes()).hexdigest()
                    rows.append(row)
                    print("OK", method_name, "F"+str(fid), "seed", seed, row.get("best_regret") or row.get("best_raw_objective"))
                except (AgentAPIError, BudgetExceeded) as exc:
                    failures.append(
                        {
                            "method": method_name,
                            "function_id": fid,
                            "seed": seed,
                            "error": f"{type(exc).__name__}: {exc}",
                            "status": "llm_blocked",
                        }
                    )
                    print("LLM_FAIL", method_name, "F"+str(fid), seed, exc)
                except Exception as exc:
                    failures.append(
                        {
                            "method": method_name,
                            "function_id": fid,
                            "seed": seed,
                            "error": f"{type(exc).__name__}: {exc}",
                            "traceback": traceback.format_exc()[-500:],
                            "status": "error",
                        }
                    )
                    print("FAIL", method_name, "F"+str(fid), seed, exc)

    llm_final = backend.stats.to_dict() if backend else {"status": "LLM_EXPERIMENT_BLOCKED"}
    manifest = {
        "experiment": EXPERIMENT,
        "run_id": run_id,
        "git_sha": prov["git_sha"],
        "worktree_dirty": prov["worktree_dirty"],
        "llm_status": llm_status,
        "llm_model": backend.model if backend else None,
        "llm_stats": llm_final,
        "protocol": {
            "functions": [
                {"id": f, "family": BBOB_FAMILIES[f], "difficulty": "difficult" if f in METABOX_DIFFICULT else "easy"}
                for f in FUNCTIONS
            ],
            "seeds": SEEDS,
            "max_fes": MAX_FES,
            "np_size": NP_SIZE,
            "dim": 10,
            "direction": "minimize",
            "budget_caps": {"max_requests": 100, "max_output_tokens": 128, "max_cost_usd": 1.0},
        },
        "methods": [m[0] for m in methods],
        "metabox": {"package": "metaevobox", "version": mb["version"], "distribution": "PyPI"},
        "python": sys.version,
        "rows": rows,
        "failures": failures,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True, default=str), encoding="utf-8")
    print("MANIFEST", manifest_path)
    print("LLM_STATUS", llm_status, llm_final)
    return 0 if rows else 1


if __name__ == "__main__":
    raise SystemExit(main())
