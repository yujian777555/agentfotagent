"""Phase-1A-8 Stage B: 80-run 2x2 factorial (archive × boundary repair).

Arms: A0(archive+clip), A1(no-archive+clip), A2(archive+midpoint), A3(no-archive+midpoint)
Functions: F1, F7, F10, F20. Seeds: 11, 22, 33, 44, 55. Budget: 5000 FE.
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
from experiments.metabox.agent_assisted_ec.lshade_factorial import run_lshade_factorial  # noqa: E402

FUNCTIONS = [1, 7, 10, 20]
SEEDS = [11, 22, 33, 44, 55]
MAX_FES = 5000
N_INIT = 100
N_MIN = 4

ARMS = {
    "A0": {"use_archive": True, "repair_method": "clip"},
    "A1": {"use_archive": False, "repair_method": "clip"},
    "A2": {"use_archive": True, "repair_method": "parent_midpoint"},
    "A3": {"use_archive": False, "repair_method": "parent_midpoint"},
}

OUT = ROOT / "results" / "phase1a8"
STAGE_B = OUT / "stage_b_traces"


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    STAGE_B.mkdir(parents=True, exist_ok=True)
    rows = []
    t0 = time.time()

    for arm_id, arm_kwargs in ARMS.items():
        for fid in FUNCTIONS:
            for seed in SEEDS:
                t_run = time.time()
                try:
                    handle = load_function(fid)
                    res = run_lshade_factorial(
                        handle._problem,
                        max_fes=MAX_FES,
                        seed=seed,
                        n_init=N_INIT,
                        n_min=N_MIN,
                        **arm_kwargs,
                    )
                    d = res.to_dict()
                    tp = STAGE_B / f"{arm_id}_F{fid:02d}_s{seed}.json"
                    tp.write_text(json.dumps(d, indent=2), encoding="utf-8")

                    row = {
                        "arm": arm_id,
                        "use_archive": arm_kwargs["use_archive"],
                        "repair_method": arm_kwargs["repair_method"],
                        "function_id": fid,
                        "seed": seed,
                        "best_raw": res.best_raw,
                        "best_benchmark_cost": res.best_benchmark_cost,
                        "optimum_is_lower_bound": res.optimum_is_lower_bound,
                        "fes": res.fes,
                        "indep": res.independent_fes,
                        "fe_exact": res.fe_exact,
                        "total_trials": res.total_trials,
                        "total_oob_trials": res.total_oob_trials,
                        "oob_trial_rate": res.total_oob_trials / res.total_trials if res.total_trials else 0,
                        "total_archive_r2": res.total_archive_r2,
                        "total_pop_r2": res.total_pop_r2,
                        "total_success": res.total_success,
                        "trace_file": str(tp.relative_to(ROOT)).replace("\\", "/"),
                        "trace_sha256": sha256_file(tp),
                        "status": "ok",
                    }
                    rows.append(row)
                    print(
                        f"[ok] {arm_id} F{fid} s={seed} best_raw={res.best_raw:.6g} "
                        f"oob={row['oob_trial_rate']:.3f} fe_exact={res.fe_exact}"
                    )
                except Exception as exc:  # noqa: BLE001
                    rows.append({"arm": arm_id, "function_id": fid, "seed": seed, "status": "fail", "error": repr(exc)})
                    print(f"[FAIL] {arm_id} F{fid} s={seed}: {exc}")

    sm = split_manifest("split_v2")
    manifest = {
        "experiment": "PHASE1A8_STAGE_B",
        "algorithm": "lshade-factorial",
        "provenance": "canonical_reimplementation; not official code",
        "arms": ARMS,
        "protocol": {
            "functions": FUNCTIONS,
            "seeds": SEEDS,
            "max_fes": MAX_FES,
            "n_init": N_INIT,
            "n_min": N_MIN,
            "expected_runs": len(ARMS) * len(FUNCTIONS) * len(SEEDS),
        },
        "split_version": "split_v2",
        "split_manifest_hash": sm["manifest_hash"],
        "rows": rows,
        "n_ok": sum(1 for r in rows if r.get("status") == "ok"),
        "n_fail": sum(1 for r in rows if r.get("status") == "fail"),
        "total_runtime_sec": round(time.time() - t0, 2),
        "code_sha256": {
            "lshade_factorial.py": sha256_file(
                ROOT / "experiments" / "metabox" / "agent_assisted_ec" / "lshade_factorial.py"
            ),
            "lshade_canonical.py": sha256_file(
                ROOT / "experiments" / "metabox" / "agent_assisted_ec" / "lshade_canonical.py"
            ),
        },
    }
    mp = OUT / "stage_b_manifest.json"
    mp.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"\nDONE ok={manifest['n_ok']} fail={manifest['n_fail']} -> {mp}")


if __name__ == "__main__":
    main()
