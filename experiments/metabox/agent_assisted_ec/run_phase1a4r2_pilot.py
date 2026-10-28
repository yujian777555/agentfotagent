"""Phase-1A-4R2: exact-count matched random timing for N+I restarts."""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from experiments.metabox.agent_assisted_ec.dpr_shade_v2 import run_dpr_shade_like
from experiments.metabox.adapter import BBOB_FAMILIES, load_function, run_optimizer
from experiments.metabox.provenance import ensure_clean_worktree, make_run_id

FUNCS = [1, 10, 20]
SEEDS = [11, 22, 33]
MAX_FES = 500
NP = 20
COOLDOWN_GEN = 5
COOLDOWN_FE = 25  # FE cooldown for random schedule


def exact_fe_schedule(k: int, seed: int, max_fes: int) -> list:
    """Exactly k FE thresholds, spaced >= COOLDOWN_FE, within [50, max_fes-10].

    No state information is read. Returns [] if k cannot be matched.
    """
    if k <= 0:
        return []
    lo, hi = 50, max_fes - 10
    slots = list(range(lo, hi + 1, COOLDOWN_FE))
    if k > len(slots):
        return []  # MATCH IMPOSSIBLE
    rng = random.Random(seed * 7919 + 3)
    rng.shuffle(slots)
    return sorted(slots[:k])


def main():
    prov = ensure_clean_worktree(allow_dirty=False)
    run_id = make_run_id(prov["git_sha"], worktree_dirty=prov["worktree_dirty"], tag="a4r2")
    out = ROOT / "results" / "phase1a4r2"
    out.mkdir(parents=True, exist_ok=True)
    manifest_path = out / f"manifest_{run_id}.json"
    if manifest_path.exists():
        raise SystemExit("exists")

    rows = []
    match_log = []
    for fid in FUNCS:
        for seed in SEEDS:
            # 1) baseline (no N, no I)
            p = load_function(fid)
            base = run_dpr_shade_like(p._problem, max_fes=MAX_FES, seed=seed, np_init=NP,
                                      use_M=False, use_N=False, use_I=False,
                                      trigger_mode="schedule", trigger_schedule=[])
            # 2) N only
            p = load_function(fid)
            n_only = run_dpr_shade_like(p._problem, max_fes=MAX_FES, seed=seed, np_init=NP,
                                        use_M=False, use_N=True, use_I=False,
                                        trigger_mode="state", gen_reset_min=COOLDOWN_GEN)
            # 3) NI_state (frozen state triggers)
            p = load_function(fid)
            ni_state = run_dpr_shade_like(p._problem, max_fes=MAX_FES, seed=seed, np_init=NP,
                                          use_M=False, use_N=True, use_I=True,
                                          trigger_mode="state", gen_reset_min=COOLDOWN_GEN)
            k_state = sum(1 for e in ni_state.events if e.get("fired"))

            # 4) NI_random_matched — exact count
            sched = exact_fe_schedule(k_state, seed, MAX_FES)
            p = load_function(fid)
            ni_rand = run_dpr_shade_like(p._problem, max_fes=MAX_FES, seed=seed, np_init=NP,
                                         use_M=False, use_N=True, use_I=True,
                                         trigger_mode="matched_fe",
                                         trigger_fe_schedule=sched,
                                         gen_reset_min=COOLDOWN_GEN)
            k_rand = sum(1 for e in ni_rand.events if e.get("fired"))
            match_ok = (k_rand == k_state)

            for method, res, n_f in (
                ("baseline", base, 0),
                ("N_only", n_only, sum(1 for e in n_only.events if e.get("fired"))),
                ("NI_state", ni_state, k_state),
                ("NI_random_matched", ni_rand, k_rand),
            ):
                rows.append({
                    "method": method, "function_id": fid, "seed": seed,
                    "metric": res.best_regret if res.best_regret is not None else res.best_raw,
                    "primary": res.primary_metric, "best_raw": res.best_raw,
                    "fes": res.fes, "indep": res.independent_fes,
                    "n_fires": n_f, "status": "ok",
                })
            match_log.append({
                "function_id": fid, "seed": seed, "k_state": k_state,
                "k_rand": k_rand, "match_ok": match_ok, "fe_schedule": sched,
                "state_fire_fes": [e.get("fes_after") for e in ni_state.events if e.get("fired")],
                "rand_fire_fes": [e.get("fes_after") for e in ni_rand.events if e.get("fired")],
            })

    all_match = all(m["match_ok"] for m in match_log)
    manifest = {
        "experiment": "PHASE1A4R2_MATCHED_CONTROL",
        "run_id": run_id,
        "git_sha": prov["git_sha"],
        "algorithm_identity": "DPR-SHADE-like (M off; N+I focus); not full L-SHADE",
        "protocol": {"functions": FUNCS, "seeds": SEEDS, "max_fes": MAX_FES, "np": NP,
                     "cooldown_gen": COOLDOWN_GEN, "cooldown_fe": COOLDOWN_FE,
                     "arms": ["baseline", "N_only", "NI_state", "NI_random_matched"]},
        "rows": rows,
        "match_log": match_log,
        "all_matched": all_match,
        "n_runs": len(rows),
        "n_failures": sum(1 for r in rows if r.get("status") != "ok"),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, default=str), encoding="utf-8")

    def m(method):
        vals = [r["metric"] for r in rows if r.get("status") == "ok" and r["method"] == method]
        return sum(vals) / len(vals) if vals else float("nan")

    def paired(a, b):
        w = l = t = 0
        per_func = {}
        for fid in FUNCS:
            wf = lf = tf = 0
            for seed in SEEDS:
                ra = next((r["metric"] for r in rows if r["method"] == a and r["function_id"] == fid and r["seed"] == seed), None)
                rb = next((r["metric"] for r in rows if r["method"] == b and r["function_id"] == fid and r["seed"] == seed), None)
                if ra is None or rb is None:
                    continue
                if ra < rb - 1e-9:
                    w += 1; wf += 1
                elif ra > rb + 1e-9:
                    l += 1; lf += 1
                else:
                    t += 1; tf += 1
            per_func[fid] = (wf, lf, tf)
        return (w, l, t), per_func

    print("all_matched", all_match, "n_runs", len(rows), "failures", manifest["n_failures"])
    for method in ["baseline", "N_only", "NI_state", "NI_random_matched"]:
        print(f"{method:20} mean={m(method):.6g}")
    for pair in [("NI_state", "baseline"), ("NI_state", "NI_random_matched"), ("N_only", "baseline"), ("NI_random_matched", "baseline")]:
        tot, per = paired(*pair)
        print(f"{pair[0]} vs {pair[1]}: total {tot} per_func {per}")
    for ml in match_log:
        print("match", ml["function_id"], ml["seed"], ml["k_state"], ml["k_rand"], ml["match_ok"], ml["fe_schedule"])
    print("WROTE", manifest_path)


if __name__ == "__main__":
    main()
