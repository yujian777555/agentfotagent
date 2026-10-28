"""Phase-1A-4 pilot: DPR-SHADE vs controls on split_v2 train (real MetaBox)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from experiments.metabox.adapter import BBOB_FAMILIES, load_function, run_optimizer
from experiments.metabox.agent_assisted_ec.dpr_shade import run_dpr_shade
from experiments.metabox.provenance import ensure_clean_worktree, make_run_id

# Frozen pilot config
FUNCS = [1, 10, 20]  # train: separable / high-cond / multimodal-weak
SEEDS = [11, 22, 33]
MAX_FES = 500
NP = 20
MODES = ["full", "no_reset", "no_shrink", "shuffled_triggers"]


def main():
    prov = ensure_clean_worktree(allow_dirty=False)
    run_id = make_run_id(prov["git_sha"], worktree_dirty=prov["worktree_dirty"], tag="a4pilot")
    out = ROOT / "results" / "phase1a4"
    out.mkdir(parents=True, exist_ok=True)
    manifest_path = out / f"manifest_{run_id}.json"
    if manifest_path.exists():
        raise SystemExit("manifest exists")

    rows = []
    for fid in FUNCS:
        for seed in SEEDS:
            # L-SHADE-style control: full mode minus triggers is approximated by
            # no_reset+no_shrink (i.e. vanilla success-history adaptation).
            for mode in MODES:
                p = load_function(fid)
                res = run_dpr_shade(p._problem, max_fes=MAX_FES, seed=seed, mode=mode)
                rows.append({
                    "method": f"dpr_{mode}", "function_id": fid, "seed": seed,
                    "metric": res.best_regret if res.best_regret is not None else res.best_raw,
                    "primary": res.primary_metric, "fes": res.fes, "indep": res.independent_fes,
                    "n_resets": len(res.resets), "final_n": res.n_history[-1],
                    "resets": res.resets, "status": "ok",
                })
            # external baselines
            for name, opt in (("official_meta_de", "DE"), ("SHADE", "SHADE")):
                try:
                    p = load_function(fid)
                    r = run_optimizer(opt, p, max_fes=MAX_FES, seed=seed)
                    rows.append({"method": name, "function_id": fid, "seed": seed,
                                 "metric": r["best_cost"], "primary": "regret_like",
                                 "fes": r["independent_fes"], "status": "ok"})
                except Exception as exc:
                    rows.append({"method": name, "function_id": fid, "seed": seed,
                                 "status": "error", "error": str(exc)[:100]})

    manifest = {
        "experiment": "PHASE1A4_PILOT",
        "run_id": run_id,
        "git_sha": prov["git_sha"],
        "protocol": {"functions": FUNCS, "seeds": SEEDS, "max_fes": MAX_FES, "np": NP,
                     "modes": MODES, "split": "split_v2 train only"},
        "rows": rows,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, default=str), encoding="utf-8")

    def m(method, fid=None):
        vals = [r["metric"] for r in rows if r.get("status") == "ok" and r["method"] == method and (fid is None or r["function_id"] == fid)]
        return sum(vals) / len(vals) if vals else float("nan")

    def paired(a, b):
        w = l = t = 0
        for fid in FUNCS:
            for seed in SEEDS:
                ra = next((r["metric"] for r in rows if r["method"] == a and r["function_id"] == fid and r["seed"] == seed and r.get("status") == "ok"), None)
                rb = next((r["metric"] for r in rows if r["method"] == b and r["function_id"] == fid and r["seed"] == seed and r.get("status") == "ok"), None)
                if ra is None or rb is None:
                    continue
                if ra < rb - 1e-9:
                    w += 1
                elif ra > rb + 1e-9:
                    l += 1
                else:
                    t += 1
        return w, l, t

    for method in ["dpr_full", "dpr_no_reset", "dpr_no_shrink", "dpr_shuffled_triggers", "official_meta_de", "SHADE"]:
        print(f"{method:24} mean={m(method):.6g}")
    for fid in FUNCS:
        print("F", fid, {k: round(m(k, fid), 4) for k in ["dpr_full", "dpr_no_reset", "dpr_no_shrink", "dpr_shuffled_triggers"]})
    print("paired full vs no_reset", paired("dpr_full", "dpr_no_reset"))
    print("paired full vs no_shrink", paired("dpr_full", "dpr_no_shrink"))
    print("paired full vs shuffled", paired("dpr_full", "dpr_shuffled_triggers"))
    print("paired full vs official", paired("dpr_full", "official_meta_de"))
    print("paired full vs SHADE", paired("dpr_full", "SHADE"))
    print("WROTE", manifest_path)


if __name__ == "__main__":
    main()
