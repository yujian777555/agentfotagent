"""Phase-1A-7 Phase A: fine-grained diagnostic trace reconstruction.

Runs lshade_canonical_diag on split_v2 train functions x seeds 11,22,33
with 5,000 FE, saving per-run full diagnostic traces.

Outputs:
- results/phase1a7/diagnostic_traces/F{fid}_s{seed}.json
- results/phase1a7/diag_manifest.json
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from experiments.metabox.adapter import load_function, split_manifest  # noqa: E402
from experiments.metabox.agent_assisted_ec.lshade_canonical_diag import (  # noqa: E402
    DIAGNOSTIC_DEFINITIONS,
    run_lshade_canonical_diag,
)

FUNCTIONS = [1, 2, 4, 6, 7, 10, 11, 12, 15, 18, 20, 21]
SEEDS = [11, 22, 33]
MAX_FES = 5000
N_INIT = 100
N_MIN = 4
H_MEMORY = 5
P_BEST = 0.1

OUT = ROOT / "results" / "phase1a7"
TRACE_DIR = OUT / "diagnostic_traces"


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    TRACE_DIR.mkdir(parents=True, exist_ok=True)

    rows = []
    failures = []
    t0 = time.time()

    for fid in FUNCTIONS:
        for seed in SEEDS:
            t_run = time.time()
            try:
                handle = load_function(fid)
                cls_name = type(handle._problem).__name__
                if cls_name != f"F{fid}":
                    raise RuntimeError(f"identity mismatch: F{fid} vs {cls_name}")

                res = run_lshade_canonical_diag(
                    handle._problem,
                    max_fes=MAX_FES,
                    seed=seed,
                    n_init=N_INIT,
                    n_min=N_MIN,
                    h_memory=H_MEMORY,
                    p_best=P_BEST,
                )
                d = res.to_dict()
                tp = TRACE_DIR / f"F{fid:02d}_s{seed}.json"
                tp.write_text(json.dumps(d, indent=2), encoding="utf-8")

                row = {
                    "function_id": fid,
                    "seed": seed,
                    "best_raw": res.best_raw,
                    "best_benchmark_cost": res.best_benchmark_cost,
                    "best_regret": res.best_regret,
                    "optimum_is_lower_bound": res.optimum_is_lower_bound,
                    "fes": res.fes,
                    "indep": res.independent_fes,
                    "fe_exact": res.fe_exact,
                    "n_final": res.n_history[-1],
                    "n_gens": len(res.gen_logs),
                    "trace_file": str(tp.relative_to(ROOT)).replace("\\", "/"),
                    "trace_sha256": sha256_file(tp),
                    "status": "ok",
                    "runtime_sec": round(time.time() - t_run, 3),
                }
                rows.append(row)
                print(
                    f"[ok] F{fid} s={seed} best_raw={res.best_raw:.6g} "
                    f"gens={len(res.gen_logs)} fe_exact={res.fe_exact}"
                )
            except Exception as exc:  # noqa: BLE001
                failures.append({"function_id": fid, "seed": seed, "error": repr(exc)})
                rows.append(
                    {"function_id": fid, "seed": seed, "status": "fail", "error": repr(exc)}
                )
                print(f"[FAIL] F{fid} s={seed}: {exc}")

    sm = split_manifest("split_v2")
    manifest = {
        "experiment": "PHASE1A7_TRACE_RECONSTRUCTION",
        "algorithm": "lshade-canonical-diag",
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
        },
        "split_version": "split_v2",
        "split_manifest_hash": sm["manifest_hash"],
        "diagnostic_definitions": DIAGNOSTIC_DEFINITIONS,
        "rows": rows,
        "n_ok": sum(1 for r in rows if r.get("status") == "ok"),
        "n_fail": len(failures),
        "failures": failures,
        "total_runtime_sec": round(time.time() - t0, 2),
        "code_sha256": {
            "lshade_canonical_diag.py": sha256_file(
                ROOT / "experiments" / "metabox" / "agent_assisted_ec" / "lshade_canonical_diag.py"
            ),
            "lshade_canonical.py": sha256_file(
                ROOT / "experiments" / "metabox" / "agent_assisted_ec" / "lshade_canonical.py"
            ),
        },
    }
    mp = OUT / "diag_manifest.json"
    mp.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"\nDONE ok={manifest['n_ok']} fail={manifest['n_fail']} -> {mp}")


if __name__ == "__main__":
    main()
