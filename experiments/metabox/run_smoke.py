"""Phase-1A P0 smoke (P0-R1-Corrective): verified identity, live controllers, full traces."""
from __future__ import annotations

import hashlib
import json
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402
from typing import Any, Dict, List  # noqa: E402

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


def _git_sha() -> str:
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=10)
        if out.returncode == 0:
            return out.stdout.strip()
    except Exception:
        pass
    return "unknown"


class DirtyWorktreeError(RuntimeError):
    """Raised when an official reproducible run is attempted on uncommitted code."""


def _git_status_porcelain() -> str:
    out = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, timeout=10)
    return out.stdout if out.returncode == 0 else ""


def ensure_clean_worktree(*, allow_dirty: bool = False) -> Dict[str, str]:
    """Verify the worktree is clean before an official run.

    Returns a provenance dict. If dirty and ``allow_dirty`` is False, raises
    DirtyWorktreeError — never labels a dirty run as a clean-SHA run.
    """
    sha = _git_sha()
    dirty = _git_status_porcelain().strip()
    if dirty and not allow_dirty:
        raise DirtyWorktreeError(
            "worktree is dirty; commit first or pass --allow-dirty "
            "(dirty runs are recorded as dirty, not as clean-SHA runs). "
            "Diff:\n" + dirty[:2000]
        )
    return {
        "git_sha": sha,
        "worktree_dirty": "true" if dirty else "false",
        "dirty_files": dirty[:2000] if dirty else "",
    }


def main(argv: List[str] | None = None) -> None:
    argv = list(argv if argv is not None else sys.argv[1:])
    allow_dirty = "--allow-dirty" in argv

    max_fes = 1500
    seeds = [11, 22]
    function_id = 6

    prov = ensure_clean_worktree(allow_dirty=allow_dirty)
    git_sha = prov["git_sha"]
    # Unique run id: sha prefix + worktree flag + timestamp. Never reused.
    stamp = time.strftime("%Y%m%dT%H%M%S")
    dirty_tag = "dirty" if prov["worktree_dirty"] == "true" else "clean"
    run_id = f"phase1a-smoke-{git_sha[:12]}-{dirty_tag}-{stamp}"

    mb = import_metabox()
    lock_path = ROOT / "experiments" / "metabox" / "LOCK.json"
    lock = json.loads(lock_path.read_text(encoding="utf-8")) if lock_path.exists() else {}

    ctrl_a = compile_controller(fixed_controller_a())
    ctrl_b = compile_controller(fixed_controller_b())

    out_dir = ROOT / "results" / "phase1a_smoke"
    out_dir.mkdir(parents=True, exist_ok=True)
    old = out_dir / "manifest.json"
    if old.exists() and not (out_dir / "INVALIDATED_manifest_p0_f6_mislabeled.json").exists():
        shutil.copy2(old, out_dir / "INVALIDATED_manifest_p0_f6_mislabeled.json")

    # Unique trace directory per run — never overwrites prior traces.
    trace_dir = out_dir / "traces" / run_id
    manifest_path = out_dir / f"manifest_{run_id}.json"
    if manifest_path.exists() or trace_dir.exists():
        raise RuntimeError(f"refusing to overwrite existing run artifacts for {run_id}")

    # --- Official DE runs ---
    rows = []
    for controller in (ctrl_a, ctrl_b):
        for seed in seeds:
            problem = load_function(function_id)
            assert problem.function_id == function_id
            t0 = time.time()
            result = run_optimizer("DE", problem, max_fes=max_fes, seed=seed, controller=controller)
            result["wall_seconds"] = round(time.time() - t0, 4)
            result["path"] = "official_de"
            result["actual_class_name"] = problem.actual_class_name
            result["family"] = problem.family
            result["independent_fes"] = result["independent_fes"]
            rows.append(result)

    # --- Controlled DE with live hooks + full traces (per-run directory) ---
    trace_dir.mkdir(parents=True, exist_ok=True)
    controlled_rows = []
    for controller in (ctrl_a, ctrl_b):
        for seed in seeds:
            problem = load_function(function_id)
            t0 = time.time()
            res = run_controlled_de(problem._problem, controller, max_fes=max_fes, seed=seed)
            elapsed = time.time() - t0
            payload = res.to_manifest_dict()
            # Full raw trace on disk with hash.
            trace_obj = {
                "run_id": run_id,
                "git_sha": git_sha,
                "worktree_dirty": prov["worktree_dirty"],
                "controller_id": controller.controller_id,
                "controller_hash": controller.controller_hash,
                "seed": seed,
                "function_id": problem.function_id,
                "actual_class_name": problem.actual_class_name,
                "payload": payload,
            }
            trace_path = trace_dir / f"controlled_{controller.controller_id}_seed{seed}.json"
            if trace_path.exists():
                raise RuntimeError(f"refusing to overwrite trace {trace_path}")
            trace_path.write_text(json.dumps(trace_obj, sort_keys=True, default=str), encoding="utf-8")
            digest = hashlib.sha256(trace_path.read_bytes()).hexdigest()
            controlled_rows.append(
                {
                    "optimizer": "controlled_de",
                    "path": "controlled_de",
                    "problem_id": problem.problem_id,
                    "function_id": problem.function_id,
                    "actual_class_name": problem.actual_class_name,
                    "family": problem.family,
                    "objective_direction": "minimize",
                    "seed": seed,
                    "controller_id": controller.controller_id,
                    "controller_hash": controller.controller_hash,
                    "wall_seconds": round(elapsed, 4),
                    "trace_path": str(trace_path.relative_to(ROOT)).replace("\\", "/"),
                    "trace_sha256": digest,
                    # Inline full payload (also on disk) for reconstruction.
                    **payload,
                }
            )

    # Identity check
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

    # Reproducibility
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
                "same_best_raw": r1.best_raw_objective == r2.best_raw_objective,
                "same_fes": r1.fes == r2.fes and r1.independent_fes == r2.independent_fes,
                "same_action_sequence": [e["action"] for e in r1.action_events]
                == [e["action"] for e in r2.action_events],
                "fe_match": r1.independent_fes == r1.fes,
            }
        )

    fe_ok = all(r["independent_fes"] == r["reported_fes"] for r in rows)
    c_fe_ok = all(r["independent_fes"] == r["fes"] for r in controlled_rows)
    fe_budget_ok = all(r["fes"] == r["max_fes"] and r["independent_fes"] == r["max_fes"] for r in controlled_rows)

    manifest = {
        "run_id": run_id,
        "phase": "phase1a-metabox-smoke-p0-r1-corrective-2",
        "engineering_only": True,
        "not_agent_capability": True,
        "agentfotagent_git_sha": git_sha,
        "worktree_dirty": prov["worktree_dirty"],
        "dirty_files": prov["dirty_files"],
        "run_started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "metabox": {
            "package": "metaevobox",
            "version": mb["version"],
            "git_sha_claimed_upstream": METABOX_GIT_SHA,
            "distribution_source": "PyPI metaevobox==2.0.2 (CI/local install)",
            "note": "PyPI wheel is version-matched to upstream v2.0.0 branch SHA 5565a281 by release naming; not byte-verified against that source tree in this run",
            "lock": lock,
        },
        "python": sys.version,
        "platform": platform.platform(),
        "split_v1": split_manifest("split_v1"),
        "split_v2": split_manifest("split_v2"),
        "function_identity_check": identity,
        "smoke_config": {
            "optimizer": ["DE", "controlled_de"],
            "function_id": function_id,
            "max_fes": max_fes,
            "seeds": seeds,
            "config_hash": config_hash(
                {
                    "optimizer": ["DE", "controlled_de"],
                    "function_id": function_id,
                    "max_fes": max_fes,
                    "seeds": seeds,
                    "run_id": run_id,
                }
            ),
        },
        "metric_semantics": {
            "primary_when_optimum_known": "regret",
            "primary_when_optimum_unknown": "raw_objective",
            "direction": "minimize",
            "official_de_cost": "problem.eval - problem.optimum (when optimum set)",
            "controlled_de": "cost_curve is raw best-so-far; regret_curve when optimum known",
        },
        "controllers": [
            {"id": ctrl_a.controller_id, "hash": ctrl_a.controller_hash, "spec": ctrl_a.spec},
            {"id": ctrl_b.controller_id, "hash": ctrl_b.controller_hash, "spec": ctrl_b.spec},
        ],
        "official_de_runs": rows,
        "controlled_de_runs": controlled_rows,
        "reproducibility": repro,
        "official_fe_accounting_match": fe_ok,
        "controlled_fe_accounting_match": c_fe_ok,
        "controlled_fe_budget_exact": fe_budget_ok,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True, default=str), encoding="utf-8")
    (out_dir / "CURRENT.txt").write_text(manifest_path.name, encoding="utf-8")
    print(
        json.dumps(
            {
                "run_id": run_id,
                "git_sha": git_sha,
                "worktree_dirty": prov["worktree_dirty"],
                "identity": identity,
                "official_fe_match": fe_ok,
                "controlled_fe_match": c_fe_ok,
                "fe_budget_exact": fe_budget_ok,
                "repro": repro,
                "manifest": str(manifest_path),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
