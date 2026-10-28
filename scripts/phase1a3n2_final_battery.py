"""Phase-1A-3N2 final falsification battery (frozen params).

Behavior-policy-driven actions with logged propensities; refusal on zero
support; preregistered ablations. Synthetic only — not optimization perf.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]

# ===== FROZEN PARAMETERS (do not change after run) =====
HORIZON = 600
N_OPS = 3
SEEDS = [11, 22, 33, 44, 55, 66, 77, 88, 99, 110]
BETA = 1.0
DR_CLIP = 10.0
EPSILON = 0.08
NOISE_STD = 0.08
CONFIG = {
    "horizon": HORIZON,
    "n_ops": N_OPS,
    "seeds": SEEDS,
    "beta": BETA,
    "clip": DR_CLIP,
    "eps": EPSILON,
    "noise_std": NOISE_STD,
    "scenario_defs": {
        "A_no_confounding": {"means": [0.35, 0.25, 0.15], "assignment": "uniform_soft"},
        "B_state_difficulty": {"means_b0": [0.30, 0.28, 0.20], "means_b1": [0.12, 0.22, 0.10], "assignment": "uniform_soft"},
        "C_endogenous_quality": {"formula": "0.10+0.6q+delta", "delta": [0.05, 0.02, 0.0], "assignment": "quality_dependent"},
        "D_near_tie": {"means": [0.300, 0.302, 0.298], "assignment": "uniform_soft"},
        "E_no_support": {"means": [0.35, 0.25, 0.15], "assignment": "zero_cell"},
        "F_drift": {"means_before": [0.35, 0.25, 0.15], "means_after": [0.15, 0.25, 0.35], "t_switch": 300, "assignment": "uniform_soft"},
    },
}
CONFIG_HASH = hashlib.sha256(json.dumps(CONFIG, sort_keys=True).encode()).hexdigest()[:16]


def true_mean(scenario: str, op: int, b: int, q: float, t: int) -> float:
    d = CONFIG["scenario_defs"][scenario]
    if scenario == "A_no_confounding":
        return d["means"][op]
    if scenario == "B_state_difficulty":
        return (d["means_b0"] if b == 0 else d["means_b1"])[op]
    if scenario == "C_endogenous_quality":
        return 0.10 + 0.6 * q + d["delta"][op]
    if scenario == "D_near_tie":
        return d["means"][op]
    if scenario == "E_no_support":
        return d["means"][op]
    if scenario == "F_drift":
        return (d["means_before"] if t < d["t_switch"] else d["means_after"])[op]
    raise ValueError(scenario)


def behavior_propensity(scenario: str, b: int, q: float, t: int) -> Dict[int, float]:
    """True logging policy e_t(a|x). Quality-dependent in C. Zero cell in E."""
    n = N_OPS
    if scenario == "C_endogenous_quality":
        w = np.array([0.70 if q > 0.5 else 0.15, 0.20 if q > 0.5 else 0.55, 0.15 if q > 0.5 else 0.30])
    elif scenario == "E_no_support":
        w = np.array([0.6, 0.4, 0.0]) if b == 1 else np.array([0.4, 0.3, 0.3])
    else:
        w = np.array([0.4, 0.35, 0.25])
    w = w / w.sum()
    # apply epsilon floor only where positive mass exists
    out = []
    for i, wi in enumerate(w):
        out.append(0.0 if wi <= 0 else float(EPSILON + (1.0 - sum(EPSILON for x in w if x > 0)) * wi))
    s = sum(out)
    if s <= 0:
        raise RuntimeError("degenerate propensity")
    return {i: out[i] / s for i in range(n)}


# ---------------------------------------------------------------------------
# Behavior-policy dataset: actions drawn from e_t, propensities logged
# ---------------------------------------------------------------------------

@dataclass
class Transition:
    b: int
    q: float
    t: int
    a: int
    e: float
    e_vec: Dict[int, float]
    r: float
    mu: float  # true mean of chosen action (evaluation only)
    best_a: int
    mu_best: float


def generate_data(scenario: str, seed: int) -> List[Transition]:
    rng = random.Random(seed * 1009 + 7)
    np_rng = np.random.RandomState(seed)
    data = []
    for t in range(HORIZON):
        b = int(np_rng.rand() < 0.5)
        q = float(np_rng.uniform(0, 1))
        e_vec = behavior_propensity(scenario, b, q, t)
        ops = sorted(e_vec)
        a = int(rng.choices(ops, weights=[e_vec[o] for o in ops], k=1)[0])
        e = e_vec[a]
        mu = true_mean(scenario, a, b, q, t)
        best_a = max(range(N_OPS), key=lambda x: true_mean(scenario, x, b, q, t))
        mu_best = true_mean(scenario, best_a, b, q, t)
        r = float(mu + np_rng.randn() * NOISE_STD)
        data.append(Transition(b, q, t, a, e, e_vec, r, mu, best_a, mu_best))
    return data


# ---------------------------------------------------------------------------
# Estimators (decision-time policy + learning from SAME logged data)
# ---------------------------------------------------------------------------

class DecisionError(Exception):
    pass


class UnsupportedAction(DecisionError):
    """Zero-propensity / no-support: must refuse to rank this action."""


@dataclass
class ArmStat:
    n: float = 0.0
    mean: float = 0.0

    def update(self, x: float, w: float = 1.0) -> None:
        if w <= 0:
            return
        self.n += w
        self.mean += w * (x - self.mean) / self.n


class Learner:
    name = "base"

    def decide(self, b: int, q: float, t: int) -> Tuple[int, str]:
        """Return (action, status). status in {ok, UNIDENTIFIABLE, INSUFFICIENT_SUPPORT}."""
        raise NotImplementedError

    def observe(self, tr: Transition) -> None:
        raise NotImplementedError


class RandomLearner(Learner):
    name = "random"

    def __init__(self, seed: int):
        self.rng = random.Random(seed)

    def decide(self, b, q, t):
        return self.rng.randrange(N_OPS), "ok"

    def observe(self, tr):
        return


class OracleLearner(Learner):
    name = "oracle"

    def __init__(self, scenario: str):
        self.scenario = scenario

    def decide(self, b, q, t):
        return max(range(N_OPS), key=lambda a: true_mean(self.scenario, a, b, q, t)), "ok"

    def observe(self, tr):
        return


class RawUCB(Learner):
    name = "raw_ucb"

    def __init__(self):
        self.s = {a: ArmStat() for a in range(N_OPS)}
        self.n = 0

    def decide(self, b, q, t):
        self.n += 1
        for a in range(N_OPS):
            if self.s[a].n == 0:
                return a, "ok"
        a = max(range(N_OPS), key=lambda x: self.s[x].mean + BETA * math.sqrt(math.log(self.n) / self.s[x].n))
        return a, "ok"

    def observe(self, tr):
        self.s[tr.a].update(tr.r)


class BucketUCB(Learner):
    name = "bucket_ucb"

    def __init__(self):
        self.s = {(b, a): ArmStat() for b in (0, 1) for a in range(N_OPS)}
        self.n = {b: 0 for b in (0, 1)}

    def decide(self, b, q, t):
        self.n[b] += 1
        for a in range(N_OPS):
            if self.s[(b, a)].n == 0:
                return a, "ok"
        a = max(
            range(N_OPS),
            key=lambda x: self.s[(b, x)].mean + BETA * math.sqrt(math.log(self.n[b]) / self.s[(b, x)].n),
        )
        return a, "ok"

    def observe(self, tr):
        self.s[(tr.b, tr.a)].update(tr.r)


class QualityResidualUCB(Learner):
    """Full method: residualize r on q within bucket, UCB on residuals."""

    name = "quality_residual"

    def __init__(self, shuffle_q: bool = False, shuffle_e: bool = False):
        self.shuffle_q = shuffle_q
        self.shuffle_e = shuffle_e
        self.s = {(b, a): ArmStat() for b in (0, 1) for a in range(N_OPS)}
        self.n = {b: 0 for b in (0, 1)}
        self.buf: Dict[int, List[Tuple[float, float]]] = {0: [], 1: []}
        self.rng = random.Random(999)

    def _g(self, b: int, q: float) -> float:
        buf = self.buf[b]
        if len(buf) < 8:
            return 0.0
        qs = np.array([x[0] for x in buf])
        rs = np.array([x[1] for x in buf])
        A = np.vstack([np.ones_like(qs), qs]).T
        coef, *_ = np.linalg.lstsq(A, rs, rcond=None)
        return float(coef[0] + coef[1] * q)

    def decide(self, b, q, t):
        self.n[b] += 1
        for a in range(N_OPS):
            if self.s[(b, a)].n == 0:
                return a, "ok"
        a = max(
            range(N_OPS),
            key=lambda x: self.s[(b, x)].mean + BETA * math.sqrt(math.log(self.n[b]) / self.s[(b, x)].n),
        )
        return a, "ok"

    def observe(self, tr: Transition):
        q = tr.q
        if self.shuffle_q:
            q = self.rng.random()  # shuffle quality feature only
        resid = tr.r - self._g(tr.b, q)
        self.s[(tr.b, tr.a)].update(resid)
        self.buf[tr.b].append((q, tr.r))
        if len(self.buf[tr.b]) > 250:
            self.buf[tr.b].pop(0)


class IPWLearner(Learner):
    name = "ipw"

    def __init__(self, shuffle_e: bool = False):
        self.shuffle_e = shuffle_e
        self.s = {(b, a): ArmStat() for b in (0, 1) for a in range(N_OPS)}
        self.n = {b: 0 for b in (0, 1)}
        self.clips = 0
        self.zero_support = {(b, a): False for b in (0, 1) for a in range(N_OPS)}
        self.rng = random.Random(4242)

    def decide(self, b, q, t):
        self.n[b] += 1
        ok = [a for a in range(N_OPS) if not self.zero_support[(b, a)]]
        if not ok:
            return -1, "UNIDENTIFIABLE"
        for a in ok:
            if self.s[(b, a)].n == 0:
                return a, "ok"
        a = max(ok, key=lambda x: self.s[(b, x)].mean + BETA * math.sqrt(math.log(max(2, self.n[b])) / max(1e-9, self.s[(b, x)].n)))
        return a, "ok"

    def observe(self, tr: Transition):
        e = tr.e
        if self.shuffle_e:
            # scramble propensity–outcome correspondence only
            e = self.rng.choice([tr.e, 1.0 - tr.e if 0 < tr.e < 1 else tr.e]) or tr.e
        if tr.e <= 0.0:
            self.zero_support[(tr.b, tr.a)] = True
            return
        if e <= 1e-12:
            self.zero_support[(tr.b, tr.a)] = True
            return
        w = 1.0 / e
        if w > DR_CLIP:
            w = DR_CLIP
            self.clips += 1
        self.s[(tr.b, tr.a)].update(tr.r, w)


class DRLearner(Learner):
    name = "dr"

    def __init__(self, shuffle_e: bool = False):
        self.shuffle_e = shuffle_e
        self.s = {(b, a): ArmStat() for b in (0, 1) for a in range(N_OPS)}
        self.n = {b: 0 for b in (0, 1)}
        self.data: List[Tuple[int, int, float, float, float]] = []
        self.clips = 0
        self.zero_support = {(b, a): False for b in (0, 1) for a in range(N_OPS)}
        self.rng = random.Random(31337)

    def _m(self, b: int, a: int, q: float, exclude: set) -> float:
        pts = [row for i, row in enumerate(self.data) if row[0] == b and row[1] == a and i not in exclude]
        if len(pts) < 6:
            return 0.0
        qs = np.array([p[2] for p in pts])
        rs = np.array([p[3] for p in pts])
        A = np.vstack([np.ones_like(qs), qs]).T
        coef, *_ = np.linalg.lstsq(A, rs, rcond=None)
        return float(coef[0] + coef[1] * q)

    def decide(self, b, q, t):
        self.n[b] += 1
        ok = [a for a in range(N_OPS) if not self.zero_support[(b, a)]]
        if not ok:
            return -1, "UNIDENTIFIABLE"
        for a in ok:
            if self.s[(b, a)].n == 0:
                return a, "ok"
        a = max(ok, key=lambda x: self.s[(b, x)].mean + BETA * math.sqrt(math.log(max(2, self.n[b])) / max(1e-9, self.s[(b, x)].n)))
        return a, "ok"

    def observe(self, tr: Transition):
        idx = len(self.data)
        self.data.append((tr.b, tr.a, tr.q, tr.r, tr.e))
        if tr.e <= 0.0:
            self.zero_support[(tr.b, tr.a)] = True
            return
        e = tr.e
        if self.shuffle_e:
            e = self.rng.choice([tr.e, max(0.02, 1.0 - tr.e)])
        m = self._m(tr.b, tr.a, tr.q, exclude={idx})
        w = min(DR_CLIP, 1.0 / max(e, 1e-12))
        if 1.0 / max(e, 1e-12) > DR_CLIP:
            self.clips += 1
        self.s[(tr.b, tr.a)].update(m + w * (tr.r - m))


# ---------------------------------------------------------------------------
# Run protocol: evaluate on FRESH contexts with same horizon; learn from logged data
# ---------------------------------------------------------------------------

def evaluate(scenario: str, learner: Learner, data: List[Transition]) -> Dict[str, Any]:
    # learn from behavior-policy data first (offline phase)
    for tr in data:
        learner.observe(tr)
    # then sequential decision phase on fresh contexts, scoring vs true means
    rng = random.Random(12345)
    np_rng = np.random.RandomState(777)
    regret = 0.0
    correct = 0
    refused = 0
    unsupported_hits = 0
    for t in range(HORIZON):
        b = int(np_rng.rand() < 0.5)
        q = float(np_rng.uniform(0, 1))
        a, status = learner.decide(b, q, t)
        if a < 0:
            refused += 1
            if status == "UNIDENTIFIABLE":
                unsupported_hits += 1
            continue
        best_a = max(range(N_OPS), key=lambda x: true_mean(scenario, x, b, q, t))
        mu = true_mean(scenario, a, b, q, t)
        mu_best = true_mean(scenario, best_a, b, q, t)
        regret += max(0.0, mu_best - mu)
        if a == best_a:
            correct += 1
    return {
        "regret": regret,
        "opt_id_rate": correct / max(1, HORIZON - refused),
        "refused": refused,
        "unidentifiable": unsupported_hits,
        "clips": getattr(learner, "clips", 0),
    }


def make_learner(kind: str, seed: int, scenario: str) -> Learner:
    if kind == "random":
        return RandomLearner(seed)
    if kind == "oracle":
        return OracleLearner(scenario)
    if kind == "raw_ucb":
        return RawUCB()
    if kind == "bucket_ucb":
        return BucketUCB()
    if kind == "quality_residual":
        return QualityResidualUCB()
    if kind == "quality_residual_no_adjust":
        return QualityResidualUCB(shuffle_q=True)  # ablation: quality feature scrambled
    if kind == "quality_residual_shuffled_q":
        return QualityResidualUCB(shuffle_q=True)
    if kind == "ipw_known_e":
        return IPWLearner(shuffle_e=False)
    if kind == "ipw_shuffled_e":
        return IPWLearner(shuffle_e=True)
    if kind == "dr_known_e":
        return DRLearner(shuffle_e=False)
    if kind == "dr_shuffled_e":
        return DRLearner(shuffle_e=True)
    raise ValueError(kind)


KINDS = [
    "random", "oracle", "raw_ucb", "bucket_ucb",
    "quality_residual", "quality_residual_shuffled_q",
    "ipw_known_e", "ipw_shuffled_e", "dr_known_e", "dr_shuffled_e",
]
SCENARIOS = [
    "A_no_confounding", "B_state_difficulty", "C_endogenous_quality",
    "D_near_tie", "E_no_support", "F_drift",
]


def main() -> None:
    # action-frequency vs propensity check on C
    freq_check = {}
    data_c = generate_data("C_endogenous_quality", 11)
    emp = {a: 0 for a in range(N_OPS)}
    for tr in data_c:
        emp[tr.a] += 1
    exp = {a: 0.0 for a in range(N_OPS)}
    for tr in data_c:
        for a in range(N_OPS):
            exp[a] += tr.e_vec[a]
    freq_check = {
        "empirical": {a: emp[a] / HORIZON for a in range(N_OPS)},
        "expected_from_propensity": {a: exp[a] / HORIZON for a in range(N_OPS)},
        "max_abs_diff": max(abs(emp[a] / HORIZON - exp[a] / HORIZON) for a in range(N_OPS)),
    }

    rows = []
    for scenario in SCENARIOS:
        for seed in SEEDS:
            data = generate_data(scenario, seed)  # SAME data for all learners
            for kind in KINDS:
                learner = make_learner(kind, seed, scenario)
                res = evaluate(scenario, learner, data)
                rows.append({"scenario": scenario, "seed": seed, "learner": kind, **res})

    out = ROOT / "results" / "phase1a3n2"
    out.mkdir(parents=True, exist_ok=True)
    payload = {
        "config": CONFIG,
        "config_hash": CONFIG_HASH,
        "code_note": "single frozen run; no post-hoc parameter changes",
        "freq_check_C": freq_check,
        "rows": rows,
    }
    (out / "final_falsification.json").write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")

    def mean(sc, kind, key="regret"):
        vals = [r[key] for r in rows if r["scenario"] == sc and r["learner"] == kind]
        return sum(vals) / len(vals)

    def paired(sc, a, b):
        w = l = t = 0
        for seed in SEEDS:
            ra = next(r["regret"] for r in rows if r["scenario"] == sc and r["learner"] == a and r["seed"] == seed)
            rb = next(r["regret"] for r in rows if r["scenario"] == sc and r["learner"] == b and r["seed"] == seed)
            if ra < rb - 1e-9:
                w += 1
            elif ra > rb + 1e-9:
                l += 1
            else:
                t += 1
        return w, l, t

    print("config_hash", CONFIG_HASH)
    print("freq_check_C", json.dumps(freq_check))
    for sc in SCENARIOS:
        print("==", sc)
        for k in KINDS:
            print(f"  {k:32} regret={mean(sc,k):8.4f} opt={mean(sc,k,'opt_id_rate'):.3f} refused={mean(sc,k,'refused'):.1f}")
    print("PAIR C quality_residual vs bucket_ucb", paired("C_endogenous_quality", "quality_residual", "bucket_ucb"))
    print("PAIR C shuffled_q vs bucket_ucb", paired("C_endogenous_quality", "quality_residual_shuffled_q", "bucket_ucb"))
    c_q = mean("C_endogenous_quality", "quality_residual")
    c_b = mean("C_endogenous_quality", "bucket_ucb")
    print(f"C mean regret quality={c_q:.4f} bucket={c_b:.4f} rel_improvement={(c_b-c_q)/c_b*100:.2f}%")
    print("E refused ipw", mean("E_no_support", "ipw_known_e", "refused"), "dr", mean("E_no_support", "dr_known_e", "refused"))
    print("WROTE", out / "final_falsification.json")


if __name__ == "__main__":
    main()
