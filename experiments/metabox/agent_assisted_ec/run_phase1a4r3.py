"""Phase-1A-4R3: N+I interventions on canonical L-SHADE reimplementation."""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from experiments.metabox.agent_assisted_ec.lshade_reimpl import run_lshade
from experiments.metabox.adapter import BBOB_FAMILIES, METABOX_DIFFICULT, load_function
from experiments.metabox.provenance import ensure_clean_worktree, make_run_id

TRAIN_FUNCS = [1, 2, 4, 6, 7, 10, 11, 12, 15, 18, 20, 21]
SEEDS = [11, 22, 33, 44, 55, 66, 77, 88, 99, 111]
MAX_FES = 10000
N_INIT = 100
COOLDOWN_FE = 200


def exact_fe_schedule(k: int, seed: int, max_fes: int) -> list:
    if k <= 0:
        return []
    lo, hi = 200, max_fes - 200
    slots = list(range(lo, hi + 1, COOLDOWN_FE))
    if k > len(slots):
        return []
    rng = random.Random(seed * 7919 + 3)
    rng.shuffle(slots)
    return sorted(slots[:k])


def main():
    prov = ensure_clean_worktree(allow_dirty=False)
    run_id = make_run_id(prov["git_sha"], worktree_dirty=prov["worktree_dirty"], tag="a4r3")
    out = ROOT / "results" / "phase1a4r3"
    out.mkdir(parents=True, exist_ok=True)
    manifest_path = out / f"manifest_{run_id}.json"
    if manifest_path.exists():
        raise SystemExit("exists")

    rows = []
    match_log = []
    n_expected = 5 * len(TRAIN_FUNCS) * len(SEEDS)
    for fid in TRAIN_FUNCS:
        for seed in SEEDS:
            # 1) L_SHADE baseline
            p = load_function(fid)
            base = run_lshade(p._problem, max_fes=MAX_FES, seed=seed, n_init=N_INIT)
            rows.append({"method": "L_SHADE", "function_id": fid, "seed": seed,
                         "metric": base.best_regret if base.best_regret is not None else base.best_raw,
                         "primary": base.primary_metric, "best_raw": base.best_raw,
                         "fes": base.fes, "indep": base.independent_fes,
                         "n_events": len(base.events), "status": "ok"})

            # 2) NI_state first (to get event schedule k)
            p = load_function(fid)
            ni_state = run_lshade(p._problem, max_fes=MAX_FES, seed=seed, n_init=N_INIT,
                                  use_N=True, use_I=True, trigger_mode="state",
                                  gen_reset_min=5)
            k_state = len(ni_state.events)
            rows.append({"method": "NI_state", "function_id": fid, "seed": seed,
                         "metric": ni_state.best_regret if ni_state.best_regret is not None else ni_state.best_raw,
                         "primary": ni_state.primary_metric, "best_raw": ni_state.best_raw,
                         "fes": ni_state.fes, "indep": ni_state.independent_fes,
                         "n_events": k_state, "status": "ok"})

            # 3) exact-count random schedule (state-blind)
            fe_sched = exact_fe_schedule(k_state, seed, MAX_FES)
            ivs = [{"fe": fe, "do_N": True, "do_I": True} for fe in fe_sched]
            p = load_function(fid)
            ni_rand = run_lshade(p._problem, max_fes=MAX_FES, seed=seed, n_init=N_INIT,
                                 interventions=ivs)
            k_rand = len(ni_rand.events)
            rows.append({"method": "NI_random_matched", "function_id": fid, "seed": seed,
                         "metric": ni_rand.best_regret if ni_rand.best_regret is not None else ni_rand.best_raw,
                         "primary": ni_rand.primary_metric, "best_raw": ni_rand.best_raw,
                         "fes": ni_rand.fes, "indep": ni_rand.independent_fes,
                         "n_events": k_rand, "status": "ok"})

            # 4) N-only replay of state schedule
            ivs_n = [{"fe": e["fes_at_event"], "do_N": True, "do_I": False} for e in ni_state.events]
            p = load_function(fid)
            n_only = run_lshade(p._problem, max_fes=MAX_FES, seed=seed, n_init=N_INIT,
                                interventions=ivs_n)
            rows.append({"method": "N_only_replay", "function_id": fid, "seed": seed,
                         "metric": n_only.best_regret if n_only.best_regret is not None else n_only.best_raw,
                         "primary": n_only.primary_metric, "best_raw": n_only.best_raw,
                         "fes": n_only.fes, "indep": n_only.independent_fes,
                         "n_events": len(n_only.events), "status": "ok"})

            # 5) I-only replay of state schedule
            ivs_i = [{"fe": e["fes_at_event"], "do_N": False, "do_I": True} for e in ni_state.events]
            p = load_function(fid)
            i_only = run_lshade(p._problem, max_fes=MAX_FES, seed=seed, n_init=N_INIT,
                                interventions=ivs_i)
            rows.append({"method": "I_only_replay", "function_id": fid, "seed": seed,
                         "metric": i_only.best_regret if i_only.best_regret is not None else i_only.best_raw,
                         "primary": i_only.primary_metric, "best_raw": i_only.best_raw,
                         "fes": i_only.fes, "indep": i_only.independent_fes,
                         "n_events": len(i_only.events), "status": "ok"})

            match_log.append({
                "function_id": fid, "seed": seed, "k_state": k_state, "k_rand": k_rand,
                "match_ok": k_state == k_rand,
                "fe_schedule": fe_sched,
                "effective_shrinks_state": sum(1 for e in ni_state.events if e.get("effective_shrink")),
            })

    all_match = all(m["match_ok"] for m in match_log)
    manifest = {
        "experiment": "PHASE1A4R3_LSHADE_RESTART",
        "run_id": run_id,
        "git_sha": prov["git_sha"],
        "algorithm_identity": "canonical L-SHADE reimplementation (not official code)",
        "protocol": {"functions": TRAIN_FUNCS, "seeds": SEEDS, "max_fes": MAX_FES, "n_init": N_INIT,
                     "expected_runs": n_expected, "cooldown_fe": COOLDOWN_FE,
                     "arms": ["L_SHADE", "N_only_replay", "I_only_replay", "NI_state", "NI_random_matched"]},
        "rows": rows,
        "match_log": match_log,
        "all_matched": all_match,
        "n_runs": len(rows),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, default=str), encoding="utf-8")

    def paired(a, b):
        w = l = t = 0
        per_func = {}
        for fid in TRAIN_FUNCS:
            wf = lf = tf = 0
            for seed in SEEDS:
                ra = next((r["metric"] for r in rows if r["method"] == a and r["function_id"] == fid and r["seed"] == seed), None)
                rb = next((r["metric"] for r in rows if r["method"] == b and r["function_id"] == fid and r["seed"] == seed), None)
                if ra is None or rb is None:
                    continue
                if ra < rb - 1e-12:
                    w += 1; wf += 1
                elif ra > rb + 1e-12:
                    l += 1; lf += 1
                else:
                    t += 1; tf += 1
            per_func[fid] = [wf, lf, tf]
        return (w, l, t), per_func

    print("n_runs", len(rows), "all_matched", all_match)
    for pair in [("NI_random_matched", "L_SHADE"), ("NI_state", "NI_random_matched"),
                 ("NI_state", "L_SHADE"), ("N_only_replay", "L_SHADE"), ("I_only_replay", "L_SHADE")]:
        tot, per = paired(*pair)
        wins = sum(1 for v in per.values() if v[0] > v[1])
        print(f"{pair[0]} vs {pair[1]}: total {tot} funcs_won {wins}/12")
        print("   per_func", per)
    print("WROTE", manifest_path)


if __name__ == "__main__":
    main()
