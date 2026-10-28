"""Phase-1A-3N: endogenous-assignment synthetic battery for operator credit estimators.

Frozen config. NOT real optimization performance. Tests estimator decisions
against known true rewards under logged propensities.
"""
from __future__ import annotations

import json
import math
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]

# Frozen parameters (do not tune after seeing results)
HORIZON = 600
N_OPS = 3
SEEDS = [11, 22, 33, 44, 55, 66, 77, 88, 99, 110]
BETA = 1.0
DR_CLIP = 10.0
MIN_SUPPORT = 8
EPSILON = 0.1  # propensity floor for logging policy


# ---------------------------------------------------------------------------
# True reward model
# ---------------------------------------------------------------------------

def true_mean(scenario: str, op: int, b: int, q: float, t: int) -> float:
    if scenario == "A_no_confounding":
        return [0.35, 0.25, 0.15][op]
    if scenario == "B_state_difficulty":
        return ([0.30, 0.28, 0.20][op] if b == 0 else [0.12, 0.22, 0.10][op])
    if scenario == "C_endogenous_quality":
        # baseline reward grows with quality; ops differ slightly
        return 0.10 + 0.60 * q + [0.05, 0.02, 0.00][op]
    if scenario == "D_near_tie":
        return [0.300, 0.302, 0.298][op]
    if scenario == "E_no_support":
        return [0.35, 0.25, 0.15][op]
    if scenario == "F_drift":
        return ([0.35, 0.25, 0.15][op] if t < 300 else [0.15, 0.25, 0.35][op])
    raise ValueError(scenario)


# ---------------------------------------------------------------------------
# Logging policy: records true propensity e_t(a|x)
# ---------------------------------------------------------------------------

@dataclass
class LogPolicy:
    scenario: str
    rng: random.Random

    def propensity(self, b: int, q: float, t: int) -> Dict[int, float]:
        """True assignment probabilities (endogenous in C/E)."""
        if self.scenario == "C_endogenous_quality":
            # high-quality targets get op0 more often (endogenous to q)
            w0 = 0.70 if q > 0.5 else 0.15
            w1 = 0.20 if q > 0.5 else 0.55
            w2 = 1.0 - w0 - w1
            raw = np.array([w0, w1, w2], dtype=float)
        elif self.scenario == "E_no_support":
            # op2 never chosen in bucket 1
            raw = np.array([0.6, 0.4, 0.0]) if b == 1 else np.array([0.4, 0.3, 0.3])
        else:
            raw = np.array([0.4, 0.35, 0.25])
        # epsilon floor keeps propensities bounded away from 0 except E_no_support zero cell
        raw = raw / raw.sum()
        out = {}
        zero = raw < 1e-12
        n_zero = int(zero.sum())
        if n_zero:
            rem = 1.0 - self._eps() * (len(raw) - n_zero)
            for i, w in enumerate(raw):
                out[i] = 0.0 if zero[i] else max(self._eps(), float(w) * rem / max(1e-12, raw[~zero].sum()))
        else:
            for i, w in enumerate(raw):
                out[i] = float(self._eps() + (1.0 - len(raw) * self._eps()) * w)
        s = sum(out.values())
        return {k: v / s for k, v in out.items()}

    def _eps(self) -> float:
        return EPSILON if self.scenario != "E_no_support" else 0.0

    def draw(self, b: int, q: float, t: int) -> Tuple[int, float]:
        e = self.propensity(b, q, t)
        ops = sorted(e)
        p = [e[a] for a in ops]
        a = int(self.rng.choices(ops, weights=p, k=1)[0])
        return a, e[a]


# ---------------------------------------------------------------------------
# Estimators
# ---------------------------------------------------------------------------

@dataclass
class Stat:
    n: int = 0
    mean: float = 0.0

    def update(self, x: float, w: float = 1.0) -> None:
        self.n += w
        self.mean += w * (x - self.mean) / self.n


class Estimator:
    name = "base"

    def on_decision(self, b: int, q: float, t: int) -> int:
        raise NotImplementedError

    def on_outcome(self, op: int, b: int, q: float, r: float, e: float, t: int) -> None:
        raise NotImplementedError


class RandomEst(Estimator):
    name = "random"

    def __init__(self, seed: int):
        self.rng = random.Random(seed)

    def on_decision(self, b, q, t):
        return self.rng.randrange(N_OPS)

    def on_outcome(self, op, b, q, r, e, t):
        return


class OracleEst(Estimator):
    name = "oracle"

    def __init__(self, scenario: str):
        self.scenario = scenario

    def on_decision(self, b, q, t):
        return max(range(N_OPS), key=lambda a: true_mean(self.scenario, a, b, q, t))

    def on_outcome(self, op, b, q, r, e, t):
        return


class RawUCB(Estimator):
    name = "raw_ucb"

    def __init__(self):
        self.s = {a: Stat() for a in range(N_OPS)}
        self.n = 0

    def on_decision(self, b, q, t):
        self.n += 1
        for a in range(N_OPS):
            if self.s[a].n == 0:
                return a
        return max(range(N_OPS), key=lambda a: self.s[a].mean + BETA * math.sqrt(math.log(self.n) / self.s[a].n))

    def on_outcome(self, op, b, q, r, e, t):
        self.s[op].update(r)


class BucketUCB(Estimator):
    name = "bucket_ucb"

    def __init__(self):
        self.s = {(b, a): Stat() for b in (0, 1) for a in range(N_OPS)}
        self.n = {b: 0 for b in (0, 1)}

    def on_decision(self, b, q, t):
        self.n[b] += 1
        for a in range(N_OPS):
            if self.s[(b, a)].n == 0:
                return a
        return max(
            range(N_OPS),
            key=lambda a: self.s[(b, a)].mean + BETA * math.sqrt(math.log(self.n[b]) / self.s[(b, a)].n),
        )

    def on_outcome(self, op, b, q, r, e, t):
        self.s[(b, op)].update(r)


class QualityResidualUCB(Estimator):
    """C: residualize reward on quality within bucket, then UCB on residuals."""

    name = "quality_residual"

    def __init__(self):
        self.s = {(b, a): Stat() for b in (0, 1) for a in range(N_OPS)}
        self.n = {b: 0 for b in (0, 1)}
        self.buf = {b: [] for b in (0, 1)}  # (q, r) for baseline model

    def _g(self, b: int, q: float) -> float:
        buf = self.buf[b]
        if len(buf) < 5:
            return 0.0
        qs = np.array([x[0] for x in buf])
        rs = np.array([x[1] for x in buf])
        # least squares r ~ a + b q
        A = np.vstack([np.ones_like(qs), qs]).T
        coef, *_ = np.linalg.lstsq(A, rs, rcond=None)
        return float(coef[0] + coef[1] * q)

    def on_decision(self, b, q, t):
        self.n[b] += 1
        for a in range(N_OPS):
            if self.s[(b, a)].n == 0:
                return a
        return max(
            range(N_OPS),
            key=lambda a: self.s[(b, a)].mean + BETA * math.sqrt(math.log(self.n[b]) / self.s[(b, a)].n),
        )

    def on_outcome(self, op, b, q, r, e, t):
        resid = r - self._g(b, q)
        self.s[(b, op)].update(resid)
        self.buf[b].append((q, r))
        if len(self.buf[b]) > 200:
            self.buf[b].pop(0)


class IPWEst(Estimator):
    """D: inverse-propensity weighted means with clipping and support checks."""

    name = "ipw"

    def __init__(self):
        self.s = {(b, a): Stat() for b in (0, 1) for a in range(N_OPS)}
        self.n = {b: 0 for b in (0, 1)}
        self.clips = 0
        self.support = {(b, a): True for b in (0, 1) for a in range(N_OPS)}

    def on_decision(self, b, q, t):
        self.n[b] += 1
        supported = [a for a in range(N_OPS) if self.support[(b, a)]]
        if not supported:
            return -1  # UNIDENTIFIABLE
        for a in supported:
            if self.s[(b, a)].n == 0:
                return a
        return max(
            supported,
            key=lambda a: self.s[(b, a)].mean
            + BETA * math.sqrt(math.log(max(2, self.n[b])) / self.s[(b, a)].n),
        )

    def on_outcome(self, op, b, q, r, e, t):
        if e <= 1e-12:
            self.support[(b, op)] = False  # zero propensity → never identifiable
            return
        w = 1.0 / e
        if w > DR_CLIP:
            w = DR_CLIP
            self.clips += 1
        self.s[(b, op)].update(r, w)


class DREst(Estimator):
    """E: doubly robust with cross-fitted outcome model + logged propensity."""

    name = "dr"

    def __init__(self):
        self.s = {(b, a): Stat() for b in (0, 1) for a in range(N_OPS)}
        self.n = {b: 0 for b in (0, 1)}
        self.data: List[Tuple[int, int, float, float, float]] = []  # b,op,q,r,e
        self.clips = 0
        self.support = {(b, a): True for b in (0, 1) for a in range(N_OPS)}

    def _m_hat(self, b: int, a: int, q: float, exclude_idx: set) -> float:
        pts = [(i, row) for i, row in enumerate(self.data) if row[0] == b and row[1] == a and i not in exclude_idx]
        if len(pts) < 4:
            return 0.0
        qs = np.array([row[2] for _, row in pts])
        rs = np.array([row[3] for _, row in pts])
        A = np.vstack([np.ones_like(qs), qs]).T
        coef, *_ = np.linalg.lstsq(A, rs, rcond=None)
        return float(coef[0] + coef[1] * q)

    def on_decision(self, b, q, t):
        self.n[b] += 1
        supported = [a for a in range(N_OPS) if self.support[(b, a)]]
        if not supported:
            return -1
        for a in supported:
            if self.s[(b, a)].n == 0:
                return a
        return max(
            supported,
            key=lambda a: self.s[(b, a)].mean
            + BETA * math.sqrt(math.log(max(2, self.n[b])) / self.s[(b, a)].n),
        )

    def on_outcome(self, op, b, q, r, e, t):
        idx = len(self.data)
        self.data.append((b, op, q, r, e))
        if e <= 1e-12:
            self.support[(b, op)] = False
            return
        # cross-fit: leave-one-out outcome model
        m = self._m_hat(b, op, q, exclude_idx={idx})
        w = 1.0 / e
        if w > DR_CLIP:
            w = DR_CLIP
            self.clips += 1
        dr_val = m + w * (r - m)
        self.s[(b, op)].update(dr_val)


# ---------------------------------------------------------------------------
# Experiment
# ---------------------------------------------------------------------------

def run_one(scenario: str, est: Estimator, seed: int) -> Dict[str, Any]:
    rng = random.Random(seed)
    np_rng = np.random.RandomState(seed)
    log = LogPolicy(scenario, rng)
    picks = []
    for t in range(HORIZON):
        b = int(np_rng.rand() < 0.5)
        q = float(np_rng.uniform(0, 1))
        a = est.on_decision(b, q, t)
        if a < 0:
            picks.append(-1)
            continue
        # NOTE: in the bandit design the estimator chooses a; logging policy
        # propensity is the *recorded* probability of that action under the
        # behavior policy. We evaluate estimator choice against truth, while
        # training uses logged propensities from a behavior policy.
        # For simplicity of this falsification battery we let the estimator
        # choose and record the behavior propensity of that choice under log.
        e = log.propensity(b, q, t)[a]
        mu = true_mean(scenario, a, b, q, t)
        r = float(mu + np_rng.randn() * 0.08)
        picks.append(a)
        est.on_outcome(a, b, q, r, e, t)

    regret = 0.0
    correct = 0
    identifiable = 0
    for t, a in enumerate(picks):
        b = int(np_rng2_helper(seed, t) < 0.5)  # not used; recompute below
    # recompute evaluation using same RNG stream is messy; instead score during loop
    return {"picks": picks}


def np_rng2_helper(seed, t):
    return 0.0


def run_one_scored(scenario: str, est: Estimator, seed: int) -> Dict[str, Any]:
    rng = random.Random(seed)
    np_rng = np.random.RandomState(seed)
    log = LogPolicy(scenario, rng)
    regret = 0.0
    correct = 0
    refused = 0
    picks = []
    for t in range(HORIZON):
        b = int(np_rng.rand() < 0.5)
        q = float(np_rng.uniform(0, 1))
        a = est.on_decision(b, q, t)
        if a < 0:
            refused += 1
            picks.append(-1)
            continue
        e = log.propensity(b, q, t)[a]
        mu = true_mean(scenario, a, b, q, t)
        best_a = max(range(N_OPS), key=lambda x: true_mean(scenario, x, b, q, t))
        mu_best = true_mean(scenario, best_a, b, q, t)
        regret += max(0.0, mu_best - mu)
        if a == best_a:
            correct += 1
        r = float(mu + np_rng.randn() * 0.08)
        picks.append(a)
        est.on_outcome(a, b, q, r, e, t)
    switches = sum(1 for i in range(1, len(picks)) if picks[i] != picks[i - 1] and picks[i] >= 0 and picks[i - 1] >= 0)
    return {
        "scenario": scenario,
        "estimator": est.name,
        "seed": seed,
        "regret": regret,
        "opt_id_rate": correct / HORIZON,
        "refused": refused,
        "switches": switches,
        "clips": getattr(est, "clips", 0),
    }


def make_est(name: str, seed: int, scenario: str) -> Estimator:
    return {
        "random": lambda: RandomEst(seed),
        "oracle": lambda: OracleEst(scenario),
        "raw_ucb": RawUCB,
        "bucket_ucb": BucketUCB,
        "quality_residual": QualityResidualUCB,
        "ipw": IPWEst,
        "dr": DREst,
    }[name]()


SCENARIOS = [
    "A_no_confounding",
    "B_state_difficulty",
    "C_endogenous_quality",
    "D_near_tie",
    "E_no_support",
    "F_drift",
]
ESTIMATORS = ["random", "oracle", "raw_ucb", "bucket_ucb", "quality_residual", "ipw", "dr"]


def main() -> None:
    rows = []
    for scenario in SCENARIOS:
        for ename in ESTIMATORS:
            for seed in SEEDS:
                rows.append(run_one_scored(scenario, make_est(ename, seed, scenario), seed))

    out = ROOT / "results" / "phase1a3n"
    out.mkdir(parents=True, exist_ok=True)
    payload = {
        "params": {"horizon": HORIZON, "beta": BETA, "seeds": SEEDS, "eps": EPSILON, "clip": DR_CLIP},
        "rows": rows,
    }
    (out / "endogenous_battery.json").write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")

    def mean(key, scenario, est):
        vals = [r[key] for r in rows if r["scenario"] == scenario and r["estimator"] == est]
        return sum(vals) / len(vals)

    print(f"{'scenario':24} {'estimator':20} regret  opt_id refused")
    for scenario in SCENARIOS:
        for est in ESTIMATORS:
            print(f"{scenario:24} {est:20} {mean('regret',scenario,est):7.4f}  {mean('opt_id_rate',scenario,est):.3f}  {mean('refused',scenario,est):.1f}")
    # key comparison C: quality_residual / dr vs bucket_ucb
    for scenario in ["C_endogenous_quality", "B_state_difficulty", "E_no_support", "F_drift"]:
        print("PAIR", scenario, "bucket_ucb", mean("regret", scenario, "bucket_ucb"),
              "quality_residual", mean("regret", scenario, "quality_residual"),
              "dr", mean("regret", scenario, "dr"),
              "ipw", mean("regret", scenario, "ipw"))
    print("WROTE", out / "endogenous_battery.json")


if __name__ == "__main__":
    main()
