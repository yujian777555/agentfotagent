"""Phase-1A P0 smoke: two fixed controllers through real MetaBox DE + controlled DE.

P0-R1: function identity is verified from the loaded class name. Old manifests
are preserved as INVALIDATED.
"""
from __future__ import annotations

import json
import platform
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402

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
from experiments.metabox.controlled_de import run_controlled_de  # noqa: E402


def main() -> None:
    max_fes = 1500
    seeds = [11, 22]
    function_id = 6  # will be verified against loaded class
    run_id = "phase1a-smoke-r1-20261027"

    mb = import_metabox()
    lock = json.loads((ROOT / "experiments" / "metabox" / "LOCK.json").read_text(encoding="utf-8"))

    ctrl_a = compile_controller(fixed_controller_a())
    ctrl_b = compile_controller(fixed_controller_b())

    rows = []
    for controller in (ctrl_a, ctrl_b):
        for seed in seeds:
            problem = load_function(function_id)
            assert problem.function_id == function_id
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
                    "path": "official_de",
                }
            )

    # Controlled DE with live trajectory → controller hooks.
    controlled_rows = []
    for controller in (ctrl_a, ctrl_b):
        for seed in seeds:
            problem = load_function(function_id)
            t0 = time.time()
            res = run_controlled_de(problem._problem, controller, max_fes=max_fes, seed=seed)
            elapsed = time.time() - t0
            controlled_rows.append(
                {
                    "optimizer": "controlled_de",
                    "path": "controlled_de",
                    "problem_id": problem.problem_id,
                    "function_id": problem.function_id,
                    "actual_class_name": problem.actual_class_name,
                    "family": problem.family,
                    "seed": seed,
                    "max_fes": max_fes,
                    "reported_fes": res.fes,
                    "independent_fes": res.fes,
                    "objective_direction": "minimize",
                    "cost_curve": res.cost_curve[-10:],
                    "best_cost": res.best_cost,
                    "controller_id": controller.controller_id,
                    "controller_hash": controller.controller_hash,
                    "action_events": res.action_events,
                    "applied_F_history": res.applied_F_history,
                    "applied_CR_history": res.applied_CR_history,
                    "wall_seconds": round(elapsed, 4),
                }
            )

    # Function identity sweep F1/F6/F24
    identity = []
    for fid in (1, 6, 24):
        p = load_function(fid)
        identity.append(
            {
                "requested": fid,
                "actual_function_id": p.function_id,
                "actual_class_name": p.actual_class_name,
                "family": p.family,
                "dim": p.dim,
                "bounds": [p.lower_bound, p.upper_bound],
                "objective_direction": p.objective_direction,
            }
        )

    # Reproducibility on controlled DE
    repro = []
    for controller in (ctrl_a, ctrl_b):
        p1 = load_function(function_id)
        r1 = run_controlled_de(p1._problem, controller, max_fes=max_fes, seed=33)
        p2 = load_function(function_id)
        r2 = run_controlled_de(p2._problem, controller, max_fes=max_fes, seed=33)
        repro.append(
            {
                "controller_id": controller.controller_id,
                "same_cost_curve": r1.cost_curve == r2.cost_curve,
                "same_best_cost": r1.best_cost == r2.best_cost,
                "same_fes": r1.fes == r2.fes,
                "same_action_sequence": [e["action"] for e in r1.action_events]
                == [e["action"] for e in r2.action_events],
                "best_cost": r1.best_cost,
                "n_action_events": len(r1.action_events),
            }
        )

    fe_ok = all(r["independent_fes"] == r["reported_fes"] for r in rows)
    direction_ok = all(
        (r["cost_curve"][-1] <= r["cost_curve"][0] + 1e-6) if r["cost_curve"] else False for r in rows
    )

    out_dir = ROOT / "results" / "phase1a_smoke"
    out_dir.mkdir(parents=True, exist_ok=True)
    # Preserve old artifact as INVALIDATED (do not overwrite).
    old = out_dir / "manifest.json"
    if old.exists():
        invalidated = out_dir / "INVALIDATED_manifest_p0_f6_mislabeled.json"
        if not invalidated.exists():
            shutil.copy2(old, invalidated)

    manifest = {
        "run_id": run_id,
        "phase": "phase1a-metabox-smoke-p0-r1",
        "engineering_only": True,
        "not_agent_capability": True,
        "invalidates": "results/phase1a_smoke/manifest.json (P0 F6 labels were misidentified; preserved as INVALIDATED_manifest_p0_f6_mislabeled.json)",
        "metabox": {
            "package": "metaevobox",
            "version": mb["version"],
            "git_sha": METABOX_GIT_SHA,
            "lock": lock,
        },
        "python": sys.version,
        "platform": platform.platform(),
        "split_v1": split_manifest("split_v1"),
        "split_v2": split_manifest("split_v2"),
        "function_identity_check": identity,
        "smoke_config": {
            "optimizer": "DE",
            "function_id": function_id,
            "max_fes": max_fes,
            "seeds": seeds,
            "config_hash": config_hash(
                {"optimizer": "DE", "function_id": function_id, "max_fes": max_fes, "seeds": seeds, "run_id": run_id}
            ),
        },
        "controllers": [
            {"id": ctrl_a.controller_id, "hash": ctrl_a.controller_hash, "spec": ctrl_a.spec},
            {"id": ctrl_b.controller_id, "hash": ctrl_b.controller_hash, "spec": ctrl_b.spec},
        ],
        "official_de_runs": rows,
        "controlled_de_runs": controlled_rows,
        "reproducibility": repro,
        "fe_accounting_match": fe_ok,
        "objective_direction_ok": direction_ok,
    }
    path = out_dir / f"manifest_{run_id}.json"
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    # Pointer for current valid artifact
    (out_dir / "CURRENT.txt").write_text(str(path.name), encoding="utf-8")
    print(
        json.dumps(
            {
                "run_id": run_id,
                "identity": identity,
                "fe_accounting_match": fe_ok,
                "objective_direction_ok": direction_ok,
                "controlled_repro": repro,
                "manifest": str(path),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
