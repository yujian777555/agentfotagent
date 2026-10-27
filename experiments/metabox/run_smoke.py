"""Phase-1A P0 smoke: run two fixed controllers through real MetaBox DE path."""
from __future__ import annotations

import json
import platform
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from experiments.metabox.adapter import (  # noqa: E402
    METABOX_GIT_SHA,
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


def main() -> None:
    max_fes = 1500
    seeds = [11, 22]
    function_id = 6  # BBOB F6 (train split)

    mb = import_metabox()
    lock = json.loads((ROOT / "experiments" / "metabox" / "LOCK.json").read_text(encoding="utf-8"))

    ctrl_a = compile_controller(fixed_controller_a())
    ctrl_b = compile_controller(fixed_controller_b())

    rows = []
    for controller in (ctrl_a, ctrl_b):
        for seed in seeds:
            problem = load_function(function_id)
            t0 = time.time()
            result = run_optimizer("DE", problem, max_fes=max_fes, seed=seed, controller=controller)
            elapsed = time.time() - t0
            rows.append(
                {
                    **result,
                    "controller_id": controller.controller_id,
                    "controller_hash": controller.controller_hash,
                    "wall_seconds": round(elapsed, 4),
                    "problem_dim": problem.dim,
                    "problem_bounds": [problem.lower_bound, problem.upper_bound],
                }
            )

    # Reproducibility check: same controller+seed twice (re-seed before each load+run).
    repro = []
    for controller in (ctrl_a, ctrl_b):
        import numpy as _np

        _np.random.seed(33)
        problem = load_function(function_id)
        r1 = run_optimizer("DE", problem, max_fes=max_fes, seed=33, controller=controller)
        _np.random.seed(33)
        problem2 = load_function(function_id)
        r2 = run_optimizer("DE", problem2, max_fes=max_fes, seed=33, controller=controller)
        repro.append(
            {
                "controller_id": controller.controller_id,
                "same_cost_curve": r1["cost_curve"] == r2["cost_curve"],
                "same_reported_fes": r1["reported_fes"] == r2["reported_fes"],
                "same_independent_fes": r1["independent_fes"] == r2["independent_fes"],
                "same_best_cost": r1["best_cost"] == r2["best_cost"],
                "best_cost": r1["best_cost"],
                "independent_fes": r1["independent_fes"],
                "reported_fes": r1["reported_fes"],
            }
        )

    # FE accounting check
    fe_ok = all(r["independent_fes"] == r["reported_fes"] for r in rows)

    # Objective direction check: DE minimizes; best cost should not exceed first logged cost for successful runs.
    direction_ok = all(
        (r["cost_curve"][-1] <= r["cost_curve"][0] + 1e-6) if r["cost_curve"] else False
        for r in rows
    )

    out_dir = ROOT / "results" / "phase1a_smoke"
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "phase": "phase1a-metabox-smoke",
        "engineering_only": True,
        "not_agent_capability": True,
        "metabox": {
            "package": "metaevobox",
            "version": mb["version"],
            "git_sha": METABOX_GIT_SHA,
            "lock": lock,
        },
        "python": sys.version,
        "platform": platform.platform(),
        "split_manifest": split_manifest(),
        "smoke_config": {
            "optimizer": "DE",
            "function_id": function_id,
            "max_fes": max_fes,
            "seeds": seeds,
            "config_hash": config_hash({"optimizer": "DE", "function_id": function_id, "max_fes": max_fes, "seeds": seeds}),
        },
        "controllers": [
            {"id": ctrl_a.controller_id, "hash": ctrl_a.controller_hash, "spec": ctrl_a.spec},
            {"id": ctrl_b.controller_id, "hash": ctrl_b.controller_hash, "spec": ctrl_b.spec},
        ],
        "runs": rows,
        "reproducibility": repro,
        "fe_accounting_match": fe_ok,
        "objective_direction_ok": direction_ok,
    }
    path = out_dir / "manifest.json"
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "runs": len(rows),
        "fe_accounting_match": fe_ok,
        "objective_direction_ok": direction_ok,
        "reproducibility": repro,
        "manifest": str(path),
    }, indent=2))


if __name__ == "__main__":
    main()
