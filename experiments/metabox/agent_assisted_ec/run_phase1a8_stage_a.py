"""Phase-1A-8 Stage A: 20 baseline runs with boundary-event logging.

Functions: F1, F7, F10, F20 (split_v2 train).
Seeds: 11, 22, 33, 44, 55.
Budget: 5,000 FE. Standard L-SHADE only.

Outputs:
- results/phase1a8/stage_a_traces/F{fid}_s{seed}.json
- results/phase1a8/stage_a_manifest.json
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from experiments.metabox.adapter import load_function, split_manifest  # noqa: E402
from experiments.metabox.agent_assisted_ec.lshade_boundary_diag import (  # noqa: E402
    BOUNDARY_DEFINITIONS,
    run_lshade_boundary_diag,
)

FUNCTIONS = [1, 7, 10, 20]
SEEDS = [11, 22, 33, 44, 55]
MAX_FES = 5000
N_INIT = 100
N_MIN = 4

OUT = ROOT / "results" / "phase1a8"
TRACE_DIR = OUT / "stage_a_traces"


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    TRACE_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    t0 = time.time()

    for fid in FUNCTIONS:
        for seed in SEEDS:
            t_run = time.time()
            try:
                handle = load_function(fid)
                res = run_lshade_boundary_diag(
                    handle._problem,
                    max_fes=MAX_FES,
                    seed=seed,
                    n_init=N_INIT,
                    n_min=N_MIN,
                )
                d = res.to_dict()
                tp = TRACE_DIR / f"F{fid:02d}_s{seed}.json"
                tp.write_text(json.dumps(d, indent=2), encoding="utf-8")

                # aggregate boundary stats across all generations
                gl = res.gen_logs
                total_trials = sum(lg["n_trials"] for lg in gl)
                total_oob_trials = sum(lg["n_oob_trials"] for lg in gl)
                total_oob_coords = sum(lg["total_oob_coords"] for lg in gl)
                total_arch_r2 = sum(lg["n_archive_r2"] for lg in gl)
                total_pop_r2 = sum(lg["n_pop_r2"] for lg in gl)
                total_success = sum(lg["successes"] for lg in gl)
                repair_L2_all = [lg["mean_repair_L2"] for lg in gl if lg["mean_repair_L2"] > 0]

                row = {
                    "function_id": fid,
                    "seed": seed,
                    "best_raw": res.best_raw,
                    "best_benchmark_cost": res.best_benchmark_cost,
                    "optimum_is_lower_bound": res.optimum_is_lower_bound,
                    "fes": res.fes,
                    "indep": res.independent_fes,
                    "fe_exact": res.fe_exact,
                    "total_trials": total_trials,
                    "total_oob_trials": total_oob_trials,
                    "oob_trial_rate": total_oob_trials / total_trials if total_trials else 0,
                    "total_oob_coords": total_oob_coords,
                    "total_arch_r2": total_arch_r2,
                    "total_pop_r2": total_pop_r2,
                    "arch_r2_rate": total_arch_r2 / total_trials if total_trials else 0,
                    "total_success": total_success,
                    "mean_repair_L2": float(np.mean(repair_L2_all)) if repair_L2_all else 0.0,
                    "n_gens": len(gl),
                    "trace_file": str(tp.relative_to(ROOT)).replace("\\", "/"),
                    "trace_sha256": sha256_file(tp),
                    "status": "ok",
                    "runtime_sec": round(time.time() - t_run, 2),
                }
                rows.append(row)
                print(
                    f"[ok] F{fid} s={seed} best_raw={res.best_raw:.6g} "
                    f"oob_rate={row['oob_trial_rate']:.3f} arch_r2={row['arch_r2_rate']:.3f} "
                    f"repair_L2={row['mean_repair_L2']:.4f} fe_exact={res.fe_exact}"
                )
            except Exception as exc:  # noqa: BLE001
                rows.append({"function_id": fid, "seed": seed, "status": "fail", "error": repr(exc)})
                print(f"[FAIL] F{fid} s={seed}: {exc}")

    sm = split_manifest("split_v2")
    manifest = {
        "experiment": "PHASE1A8_STAGE_A",
        "algorithm": "lshade-canonical-boundary-diag",
        "provenance": "canonical_reimplementation; not official code",
        "protocol": {
            "functions": FUNCTIONS,
            "seeds": SEEDS,
            "max_fes": MAX_FES,
            "n_init": N_INIT,
            "n_min": N_MIN,
            "interventions": "NONE",
            "llm_calls": 0,
        },
        "split_version": "split_v2",
        "split_manifest_hash": sm["manifest_hash"],
        "boundary_definitions": BOUNDARY_DEFINITIONS,
        "rows": rows,
        "n_ok": sum(1 for r in rows if r.get("status") == "ok"),
        "n_fail": sum(1 for r in rows if r.get("status") == "fail"),
        "total_runtime_sec": round(time.time() - t0, 2),
        "code_sha256": {
            "lshade_boundary_diag.py": sha256_file(
                ROOT / "experiments" / "metabox" / "agent_assisted_ec" / "lshade_boundary_diag.py"
            ),
            "lshade_canonical.py": sha256_file(
                ROOT / "experiments" / "metabox" / "agent_assisted_ec" / "lshade_canonical.py"
            ),
        },
    }
    mp = OUT / "stage_a_manifest.json"
    mp.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"\nDONE ok={manifest['n_ok']} fail={manifest['n_fail']} -> {mp}")

    # quick signal check
    all_oob = [r.get("oob_trial_rate", 0) for r in rows if r.get("status") == "ok"]
    all_arch = [r.get("arch_r2_rate", 0) for r in rows if r.get("status") == "ok"]
    print(f"Signal check: mean oob_trial_rate={np.mean(all_oob):.4f}, mean arch_r2_rate={np.mean(all_arch):.4f}")
    if np.mean(all_oob) < 0.01:
        print("WARNING: boundary repair events may be insufficient (oob_trial_rate < 1%)")
    if np.mean(all_arch) < 0.05:
        print("WARNING: archive sampling may be insufficient (arch_r2_rate < 5%)")


if __name__ == "__main__":
    main()
