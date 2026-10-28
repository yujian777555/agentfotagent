"""Phase-1A-6 baseline rebuild: canonical L-SHADE on split_v2 train.

One train-only run set:
- BBOB 10D, split_v2 train functions [1,2,4,6,7,10,11,12,15,18,20,21]
- seeds [11, 22, 33]
- max_fes = 5000 per run
- algorithm: lshade_canonical (no N+I, no state triggers, no restarts, no LLM)

Produces:
- results/phase1a6/rows.json            (per-run summary)
- results/phase1a6/trajectories/<fid>_s<seed>.json  (full curves)
- results/phase1a6/manifest_phase1a6.json
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
from experiments.metabox.agent_assisted_ec.lshade_canonical import (  # noqa: E402
    run_lshade_canonical,
)

FUNCTIONS = [1, 2, 4, 6, 7, 10, 11, 12, 15, 18, 20, 21]
SEEDS = [11, 22, 33]
MAX_FES = 5000
N_INIT = 100
N_MIN = 4
H_MEMORY = 5
P_BEST = 0.1

OUT = ROOT / "results" / "phase1a6"
TRAJ = OUT / "trajectories"


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    h.update(p.read_bytes())
    return h.hexdigest()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    TRAJ.mkdir(parents=True, exist_ok=True)

    rows = []
    failures = []
    t0 = time.time()

    for fid in FUNCTIONS:
        for seed in SEEDS:
            t_run = time.time()
            status = "ok"
            err = None
            res_dict = None
            try:
                handle = load_function(fid)
                # verify identity
                cls_name = type(handle._problem).__name__
                if cls_name != f"F{fid}":
                    raise RuntimeError(f"identity mismatch: expected F{fid}, got {cls_name}")
                res = run_lshade_canonical(
                    handle._problem,
                    max_fes=MAX_FES,
                    seed=seed,
                    n_init=N_INIT,
                    n_min=N_MIN,
                    h_memory=H_MEMORY,
                    p_best=P_BEST,
                    log_every=10,
                )
                res_dict = res.to_dict()
                opt = res.optimum
                lower_ok = res.optimum_is_lower_bound
                row = {
                    "method": "L_SHADE_CANONICAL",
                    "function_id": fid,
                    "seed": seed,
                    "best_raw": res.best_raw,
                    "best_benchmark_cost": res.best_benchmark_cost,
                    "best_regret": res.best_regret,
                    "optimum": opt,
                    "optimum_is_lower_bound": lower_ok,
                    "primary": "regret" if lower_ok else "benchmark_cost",
                    "metric": res.best_regret if lower_ok else res.best_benchmark_cost,
                    "fes": res.fes,
                    "indep": res.independent_fes,
                    "fe_exact": res.fe_exact,
                    "n_final": res.n_history[-1],
                    "n_init_observed": res.n_history[0],
                    "status": "ok",
                }
                # save trajectory
                tp = TRAJ / f"F{fid:02d}_s{seed}.json"
                tp.write_text(json.dumps(res_dict, indent=2), encoding="utf-8")
                row["trajectory_file"] = str(tp.relative_to(ROOT)).replace("\\", "/")
                row["trajectory_sha256"] = sha256_file(tp)
                row["runtime_sec"] = round(time.time() - t_run, 3)
                rows.append(row)
                print(
                    f"[ok] F{fid} seed={seed} best_raw={res.best_raw:.6g} "
                    f"cost={res.best_benchmark_cost:.6g} lower_ok={lower_ok} "
                    f"fes={res.fes} indep={res.independent_fes} "
                    f"N:{res.n_history[0]}->{res.n_history[-1]}"
                )
            except Exception as exc:  # noqa: BLE001
                status = "fail"
                err = repr(exc)
                failures.append({"function_id": fid, "seed": seed, "error": err})
                rows.append(
                    {
                        "method": "L_SHADE_CANONICAL",
                        "function_id": fid,
                        "seed": seed,
                        "status": "fail",
                        "error": err,
                    }
                )
                print(f"[FAIL] F{fid} seed={seed}: {err}")

    sm = split_manifest("split_v2")
    manifest = {
        "experiment": "PHASE1A6_BASELINE_REBUILD",
        "algorithm": "lshade-canonical-reimpl",
        "provenance": "canonical_reimplementation; not official code",
        "suite": "bbob-10D",
        "protocol": {
            "functions": FUNCTIONS,
            "seeds": SEEDS,
            "max_fes": MAX_FES,
            "n_init": N_INIT,
            "n_min": N_MIN,
            "h_memory": H_MEMORY,
            "p_best": P_BEST,
            "interventions": "NONE",
            "llm_calls": 0,
            "expected_runs": len(FUNCTIONS) * len(SEEDS),
        },
        "split_version": "split_v2",
        "split_manifest_hash": sm["manifest_hash"],
        "rows": rows,
        "n_ok": sum(1 for r in rows if r.get("status") == "ok"),
        "n_fail": len(failures),
        "failures": failures,
        "total_runtime_sec": round(time.time() - t0, 2),
        "code_sha256": {
            "lshade_canonical.py": sha256_file(
                ROOT / "experiments" / "metabox" / "agent_assisted_ec" / "lshade_canonical.py"
            ),
            "adapter.py": sha256_file(ROOT / "experiments" / "metabox" / "adapter.py"),
        },
    }
    mp = OUT / "manifest_phase1a6.json"
    mp.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    rp = OUT / "rows.json"
    rp.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(f"\nDONE ok={manifest['n_ok']} fail={manifest['n_fail']} -> {mp}")


if __name__ == "__main__":
    main()
