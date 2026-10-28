"""Phase-1A-4R corrected pilot: factorial (M,N,I) + matched-random timing."""
from __future__ import annotations

import itertools
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from experiments.metabox.agent_assisted_ec.dpr_shade_v2 import run_dpr_shade_like
from experiments.metabox.adapter import load_function, run_optimizer
from experiments.metabox.provenance import ensure_clean_worktree, make_run_id

FUNCS = [1, 10, 20]
SEEDS = [11, 22, 33]
MAX_FES = 500
NP = 20
COOLDOWN = 5


def run_state(fid, seed, M, N, I):
    p = load_function(fid)
    return run_dpr_shade_like(
        p._problem, max_fes=MAX_FES, seed=seed, np_init=NP,
        use_M=M, use_N=N, use_I=I, trigger_mode="state",
        gen_reset_min=COOLDOWN,
    )


def matched_fe_schedule(target: int, seed: int, max_fes: int, cooldown_fe: int = 80):
    """FE-based intervention schedule, independent of search state.

    Samples FE thresholds from [init_N, max_fes) with cooldown in FE units so
    the schedule is reachable under any generation trajectory.
    """
    rng = random.Random(seed * 991 + 17)
    lo, hi = NP + cooldown_fe, max_fes - 5
    candidates = list(range(lo, hi, cooldown_fe))
    rng.shuffle(candidates)
    picks = sorted(candidates[:target])
    return picks


def main():
    prov = ensure_clean_worktree(allow_dirty=False)
    run_id = make_run_id(prov["git_sha"], worktree_dirty=prov["worktree_dirty"], tag="a4r")
    out = ROOT / "results" / "phase1a4r"
    out.mkdir(parents=True, exist_ok=True)
    manifest_path = out / f"manifest_{run_id}.json"
    if manifest_path.exists():
        raise SystemExit("exists")

    rows = []
    trigger_log = []
    configs = list(itertools.product([0, 1], repeat=3))  # (M,N,I)
    for fid in FUNCS:
        for seed in SEEDS:
            # state-triggered full first (for matched counts)
            full = run_state(fid, seed, 1, 1, 1)
            n_state = sum(1 for e in full.events if e.get("fired"))
            trigger_log.append({
                "function_id": fid, "seed": seed, "n_state_fires": n_state,
                "stall_only": sum(1 for e in full.events if e.get("fired") and e.get("stall_fire") and not e.get("div_fire")),
                "div_only": sum(1 for e in full.events if e.get("fired") and e.get("div_fire") and not e.get("stall_fire")),
                "both": sum(1 for e in full.events if e.get("fired") and e.get("div_fire") and e.get("stall_fire")),
                "cooldown_blocked": sum(1 for e in full.events if (e.get("stall_fire") or e.get("div_fire")) and not e.get("cooldown_ok")),
                "n_immigrants_total": sum(e.get("n_immigrants", 0) for e in full.events),
            })
            rows.append({
                "method": "state_M1N1I1", "function_id": fid, "seed": seed,
                "metric": full.best_regret if full.best_regret is not None else full.best_raw,
                "primary": full.primary_metric, "fes": full.fes, "indep": full.independent_fes,
                "n_fires": n_state, "status": "ok",
            })
            # factorial
            for M, N, I in configs:
                if (M, N, I) == (1, 1, 1):
                    continue
                res = run_state(fid, seed, M, N, I)
                rows.append({
                    "method": f"M{M}N{N}I{I}", "function_id": fid, "seed": seed,
                    "metric": res.best_regret if res.best_regret is not None else res.best_raw,
                    "primary": res.primary_metric, "fes": res.fes, "indep": res.independent_fes,
                    "n_fires": sum(1 for e in res.events if e.get("fired")), "status": "ok",
                })
            # matched random timing (FE-based, count-matched to state full)
            fe_sched = matched_fe_schedule(n_state, seed, MAX_FES)
            p = load_function(fid)
            mr = run_dpr_shade_like(
                p._problem, max_fes=MAX_FES, seed=seed, np_init=NP,
                use_M=True, use_N=True, use_I=True,
                trigger_mode="matched_fe", trigger_fe_schedule=fe_sched,
                gen_reset_min=COOLDOWN,
            )
            rows.append({
                "method": "matched_random_timing", "function_id": fid, "seed": seed,
                "metric": mr.best_regret if mr.best_regret is not None else mr.best_raw,
                "primary": mr.primary_metric, "fes": mr.fes, "indep": mr.independent_fes,
                "n_fires": sum(1 for e in mr.events if e.get("fired")),
                "target_fires": n_state, "fe_schedule": fe_sched,
                "schedule_match_ok": sum(1 for e in mr.events if e.get("fired")) == n_state,
                "status": "ok",
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
        "experiment": "PHASE1A4R_CORRECTED_PILOT",
        "run_id": run_id,
        "git_sha": prov["git_sha"],
        "algorithm_identity": "DPR-SHADE-like (no archive, no linear N(t)); external SHADE is independent MetaBox impl",
        "protocol": {"functions": FUNCS, "seeds": SEEDS, "max_fes": MAX_FES, "np": NP,
                     "factorial": "2x2x2 M,N,I", "cooldown": COOLDOWN},
        "rows": rows,
        "trigger_log": trigger_log,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, default=str), encoding="utf-8")

    def m(method):
        vals = [r["metric"] for r in rows if r.get("status") == "ok" and r["method"] == method]
        return sum(vals) / len(vals) if vals else float("nan")

    def paired(a, b):
        w = l = t = 0
        for fid in FUNCS:
            for seed in SEEDS:
                ra = next((r["metric"] for r in rows if r["method"] == a and r["function_id"] == fid and r["seed"] == seed and r.get("status") == "ok"), None)
                rb = next((r["metric"] for r in rows if r["method"] == b and r["function_id"] == fid and r["seed"] == seed and r.get("status") == "ok"), None)
                if ra is None or rb is None:
                    continue
                if ra < rb - 1e-9: w += 1
                elif ra > rb + 1e-9: l += 1
                else: t += 1
        return w, l, t

    for method in ["M0N0I0", "M1N0I0", "M0N1I0", "M0N0I1", "M1N1I0", "M1N0I1", "M0N1I1", "M1N1I1", "matched_random_timing", "official_meta_de", "SHADE"]:
        print(f"{method:24} mean={m(method):.6g}")
    print("state full vs matched", paired("M1N1I1", "matched_random_timing"))
    print("state full vs baseline M0N0I0", paired("M1N1I1", "M0N0I0"))
    print("state full vs SHADE", paired("M1N1I1", "SHADE"))
    print("trigger_log sample", trigger_log[0])
    print("WROTE", manifest_path)


if __name__ == "__main__":
    main()
