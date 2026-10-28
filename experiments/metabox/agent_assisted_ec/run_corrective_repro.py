"""Phase-1A-2R corrective reproduction with frozen agent_mech_3.

No LLM calls. Binds to a frozen manifest by path + hash. Full traces.
"""
from __future__ import annotations

import hashlib
import json
import random
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from experiments.metabox.adapter import (
    BBOB_FAMILIES,
    METABOX_DIFFICULT,
    load_function,
    run_optimizer,
)
from experiments.metabox.agent_assisted_ec.mechanism_dsl import (
    MECH_DSL_VERSION,
    compile_mechanism,
    validate_mechanism,
)
from experiments.metabox.agent_assisted_ec.multi_de import run_multi_de, trace_sha256
from experiments.metabox.provenance import (
    ensure_clean_worktree,
    ensure_unique_artifacts,
    make_run_id,
)

# Frozen protocol (Phase-1A-2R)
TRAIN_FUNCS = [1, 2, 4, 6, 7, 10, 11, 12, 15, 18, 20, 21]
SEEDS = [11, 22, 33, 44, 55]
MAX_FES = 300
NP_SIZE = 20
BASE_F, BASE_CR = 0.5, 0.9
FROZEN_MANIFEST = ROOT / "results" / "agent_assisted_ec" / "manifest_a2-1fc40335619e-clean-20261028T111308.json"
# Git blob object SHA of the frozen manifest (from review):
FROZEN_MANIFEST_GIT_SHA = "3b6fb101820072223058a3644fff799eb411a6b8"

# Feature threshold scales frozen from train public-state observations (P1A-2 logs):
# stag in [0,160], succ in [0,1], div in [~20,60], imp in [0,1], budget in [0,1]
FEAT_SCALES = {
    "stagnation_steps": (0.0, 80.0),
    "success_fraction": (0.0, 1.0),
    "population_diversity": (15.0, 60.0),
    "improvement_rate": (0.0, 1.0),
    "budget_fraction": (0.0, 1.0),
}


def load_frozen_mech3():
    if not FROZEN_MANIFEST.exists():
        raise FileNotFoundError(FROZEN_MANIFEST)
    data = json.loads(FROZEN_MANIFEST.read_text(encoding="utf-8"))
    specs = data.get("agent_mechanisms") or []
    m3 = next((s for s in specs if s.get("mechanism_id") == "agent_mech_3"), None)
    if m3 is None:
        raise ValueError("frozen agent_mech_3 missing")
    return validate_mechanism(m3), data


def random_mechanism(rng: random.Random, mid: str, n_rules: int = 2) -> dict:
    ops = ["rand/1/bin", "current-to-best/1/bin", "rand/2/bin", "best/1/bin"]
    feats = list(FEAT_SCALES)
    rules = []
    for _ in range(n_rules):
        feat = rng.choice(feats)
        lo, hi = FEAT_SCALES[feat]
        thr = round(rng.uniform(lo, hi), 2)
        op = rng.choice([">=", ">", "<", "<="])
        act = rng.choice(["set_operator", "set_F", "set_CR", "inject_diversity"])
        if act == "set_operator":
            then = {"action": act, "params": {"operator": rng.choice(ops)}}
        elif act == "set_F":
            then = {"action": act, "params": {"value": round(rng.uniform(0.1, 1.0), 3)}}
        elif act == "set_CR":
            then = {"action": act, "params": {"value": round(rng.uniform(0.0, 1.0), 3)}}
        else:
            then = {"action": act, "params": {}}
        rules.append({"when": {feat: {"op": op, "value": thr}}, "then": then})
    spec = {
        "schema_version": MECH_DSL_VERSION,
        "mechanism_id": mid,
        "description": "random valid mechanism (corrected scales)",
        "rules": rules,
        "default": {"action": "set_operator", "params": {"operator": rng.choice(ops)}},
    }
    return validate_mechanism(spec)


def fixed_classic_spec():
    return validate_mechanism({
        "schema_version": MECH_DSL_VERSION,
        "mechanism_id": "fixed_classic",
        "description": "rand/1/bin F=0.5 CR=0.9",
        "rules": [{"when": {"stagnation_steps": {"op": ">=", "value": 99999}},
                   "then": {"action": "noop", "params": {}}}],
        "default": {"action": "set_operator", "params": {"operator": "rand/1/bin"}},
    })


def deterministic_spec():
    """Reachable two-rule deterministic baseline (corrected)."""
    return validate_mechanism({
        "schema_version": MECH_DSL_VERSION,
        "mechanism_id": "deterministic_stag",
        "description": "stag>=5 -> rand/2/bin else rand/1/bin",
        "rules": [
            {"when": {"stagnation_steps": {"op": ">=", "value": 5.0}},
             "then": {"action": "set_operator", "params": {"operator": "rand/2/bin"}}},
        ],
        "default": {"action": "set_operator", "params": {"operator": "rand/1/bin"}},
    })


def main():
    m3_spec, frozen = load_frozen_mech3()
    out_root = ROOT / "results" / "agent_assisted_ec_corrective"
    out_root.mkdir(parents=True, exist_ok=True)
    prov = ensure_clean_worktree(allow_dirty=False)
    run_id = make_run_id(prov["git_sha"], worktree_dirty=prov["worktree_dirty"], tag="a2r")
    manifest_path = out_root / f"manifest_{run_id}.json"
    trace_dir = out_root / "traces" / run_id
    ensure_unique_artifacts(manifest_path, trace_dir)
    trace_dir.mkdir(parents=True, exist_ok=True)

    # arms
    rng = random.Random(20261028)
    arms = [
        ("fixed_classic", fixed_classic_spec()),
        ("deterministic", deterministic_spec()),
        ("agent_mech_3", m3_spec),
    ]
    # 20 random mechanisms, fixed seed, recorded hashes
    rand_specs = []
    for i in range(20):
        s = random_mechanism(rng, f"random_mech_{i:02d}")
        rand_specs.append(s)
        arms.append((s["mechanism_id"], s))
    # shuffled from mech_3
    sh = json.loads(json.dumps(m3_spec))
    sh["mechanism_id"] = "shuffled_map"
    whens = [r["when"] for r in sh["rules"]]
    thens = [r["then"] for r in sh["rules"]]
    rng.shuffle(thens)
    sh["rules"] = [{"when": w, "then": t} for w, t in zip(whens, thens)]
    arms.append(("shuffled_map", validate_mechanism(sh)))
    # ablations from mech_3
    ab1 = json.loads(json.dumps(m3_spec))
    ab1["mechanism_id"] = "ablate_no_stag"
    ab1["rules"] = [r for r in ab1["rules"] if "stagnation_steps" not in r["when"]]
    if not ab1["rules"]:
        raise ValueError("ablate_no_stag produced empty rules")
    arms.append(("ablate_no_stag", validate_mechanism(ab1)))
    ab2 = json.loads(json.dumps(m3_spec))
    ab2["mechanism_id"] = "ablate_no_div"
    ab2["rules"] = [r for r in ab2["rules"] if "population_diversity" not in r["when"]]
    if not ab2["rules"]:
        raise ValueError("ablate_no_div produced empty rules")
    arms.append(("ablate_no_div", validate_mechanism(ab2)))

    rows = []
    traces_meta = []
    for fid in TRAIN_FUNCS:
        for seed in SEEDS:
            # official + SHADE (independent implementations)
            for name, opt_name in (("official_meta_de", "DE"), ("SHADE", "SHADE")):
                try:
                    p = load_function(fid)
                    r = run_optimizer(opt_name, p, max_fes=MAX_FES, seed=seed)
                    rows.append({"arm": name, "function_id": fid, "seed": seed,
                                 "metric": r["best_cost"], "primary": "regret_like_official",
                                 "fes": r["independent_fes"], "status": "ok"})
                except Exception as exc:
                    rows.append({"arm": name, "function_id": fid, "seed": seed,
                                 "status": "error", "error": str(exc)[:120]})
            for arm_name, spec in arms:
                p = load_function(fid)
                mech = compile_mechanism(spec)
                t0 = time.time()
                res = run_multi_de(p._problem, mech, max_fes=MAX_FES, seed=seed,
                                   np_size=NP_SIZE, F=BASE_F, Cr=BASE_CR)
                wall = time.time() - t0
                metric = res.best_regret if res.best_regret is not None else res.best_raw_objective
                payload = {
                    "run_id": run_id,
                    "git_sha": prov["git_sha"],
                    "function_id": fid,
                    "family": BBOB_FAMILIES[fid],
                    "seed": seed,
                    "max_fes": MAX_FES,
                    "np_size": NP_SIZE,
                    "base_F": BASE_F,
                    "base_CR": BASE_CR,
                    "arm": arm_name,
                    "mech_hash": mech.mech_hash,
                    "mechanism": spec,
                    "payload": res.to_manifest_dict(),
                }
                tp = trace_dir / f"{arm_name}_F{fid}_seed{seed}.json"
                tp.write_text(json.dumps(payload, sort_keys=True, default=str), encoding="utf-8")
                digest = trace_sha256(payload)
                traces_meta.append({"path": str(tp.relative_to(ROOT)).replace("\\", "/"),
                                    "sha256": digest, "arm": arm_name,
                                    "function_id": fid, "seed": seed})
                rows.append({
                    "arm": arm_name, "function_id": fid, "seed": seed,
                    "metric": metric, "primary": res.primary_metric,
                    "best_raw": res.best_raw_objective, "fes": res.fes,
                    "indep_fes": res.independent_fes, "mech_hash": mech.mech_hash,
                    "operator_counts": res.operator_counts,
                    "n_inject": len(res.inject_events),
                    "inject_events": res.inject_events,
                    "wall": round(wall, 3), "status": "ok",
                    "trace_path": traces_meta[-1]["path"], "trace_sha256": digest,
                })

    manifest = {
        "experiment": "PHASE1A_A2_CORRECTIVE_REPRO",
        "run_id": run_id,
        "git_sha": prov["git_sha"],
        "worktree_dirty": prov["worktree_dirty"],
        "frozen_manifest": str(FROZEN_MANIFEST.relative_to(ROOT)),
        "frozen_manifest_git_sha": FROZEN_MANIFEST_GIT_SHA,
        "frozen_mech3_hash": compile_mechanism(m3_spec).mech_hash,
        "protocol": {
            "train_functions": TRAIN_FUNCS, "seeds": SEEDS, "max_fes": MAX_FES,
            "np_size": NP_SIZE, "dim": 10, "base_F": BASE_F, "base_CR": BASE_CR,
            "first_match_rules": True,
        },
        "random_mechanisms": [{"id": s["mechanism_id"],
                               "hash": compile_mechanism(s).mech_hash,
                               "spec": s} for s in rand_specs],
        "shuffled_spec": sh,
        "ablate_specs": {"ablate_no_stag": ab1, "ablate_no_div": ab2},
        "rows": rows,
        "traces": traces_meta,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, default=str), encoding="utf-8")
    (out_root / "CURRENT.txt").write_text(manifest_path.name, encoding="utf-8")
    ok_rows = [r for r in rows if r.get("status") == "ok"]
    fe_ok = all(r.get("fes") == MAX_FES and r.get("indep_fes") == MAX_FES for r in ok_rows if "indep_fes" in r)
    print(json.dumps({
        "run_id": run_id, "rows_ok": len(ok_rows), "rows_total": len(rows),
        "fe_exact": fe_ok, "n_traces": len(traces_meta),
        "manifest": str(manifest_path),
    }, indent=2))


if __name__ == "__main__":
    main()
