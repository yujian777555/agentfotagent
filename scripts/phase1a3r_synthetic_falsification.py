"""Phase-1A-3R synthetic falsification: credit estimators under known reward models.

NOT real optimization performance. Tests decision logic only.
Scenarios A-E per protocol. Fixed seeds, frozen parameters.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[2]

# Frozen parameters
HORIZON = 400
N_OPS = 3
N_BUCKETS = 2  # easy / hard states
BETA = 1.0
SEEDS = [11, 22, 33, 44, 55]
DECAY_HALF_LIFE = 200.0  # decisions; used only in drift scenario


# ---------------------------------------------------------------------------
# Ground-truth reward models (unknown to algorithms)
# ---------------------------------------------------------------------------

def true_mean(scenario: str, op: int, bucket: int, quality: float, t: int) -> float:
    """Expected reward for pulling arm `op` in context."""
    if scenario == "A_no_confounding":
        return [0.35, 0.25, 0.15][op]
    if scenario == "B_state_difficulty":
        # hard bucket (1) lowers all rewards; best op differs by bucket
        base = [0.30, 0.28, 0.20][op] if bucket == 0 else [0.12, 0.22, 0.10][op]
        return base
    if scenario == "C_quality_confounding":
        # observed reward scales with parent quality; raw means mix quality
        intrinsic = [0.30, 0.28, 0.10][op]
        return intrinsic + 0.5 * quality
    if scenario == "D_near_tie":
        return [0.300, 0.302, 0.298][op]
    if scenario == "E_drift":
        # best op switches at t=200
        if t < 200:
            return [0.35, 0.25, 0.15][op]
        return [0.15, 0.25, 0.35][op]
    raise ValueError(scenario)


def draw_reward(scenario, op, bucket, quality, t, rng: np.random.RandomState) -> float:
    mu = true_mean(scenario, op, bucket, quality, t)
    noise = 0.08 if scenario != "D_near_tie" else 0.12
    return float(mu + rng.randn() * noise)


# ---------------------------------------------------------------------------
# Estimators / policies
# ---------------------------------------------------------------------------

@dataclass
class ArmStat:
    n: int = 0
    mean: float = 0.0
    m2: float = 0.0

    def update(self, x: float) -> None:
        self.n += 1
        d = x - self.mean
        self.mean += d / self.n
        self.m2 += d * (x - self.mean)

    @property
    def var(self) -> float:
        return self.m2 / self.n if self.n > 1 else 1e-6


class Policy:
    name = "base"

    def select(self, bucket: int, t: int, quality: float) -> int:
        raise NotImplementedError

    def update(self, op: int, bucket: int, reward: float, quality: float, t: int) -> None:
        raise NotImplementedError


class RandomPolicy(Policy):
    name = "random"

    def __init__(self, seed: int):
        self.rng = random.Random(seed)

    def select(self, bucket, t, quality):
        return self.rng.randrange(N_OPS)

    def update(self, op, bucket, reward, quality, t):
        return


class OraclePolicy(Policy):
    name = "oracle"

    def __init__(self, scenario: str):
        self.scenario = scenario

    def select(self, bucket, t, quality):
        # argmax true mean (quality known to oracle for C)
        return max(range(N_OPS), key=lambda a: true_mean(self.scenario, a, bucket, quality, t))

    def update(self, op, bucket, reward, quality, t):
        return


class UCBPolicy(Policy):
    """Raw-reward UCB (global, no buckets)."""

    name = "raw_ucb"

    def __init__(self):
        self.stats = {a: ArmStat() for a in range(N_OPS)}
        self.total = 0

    def select(self, bucket, t, quality):
        self.total += 1
        for a in range(N_OPS):
            if self.stats[a].n == 0:
                return a
        return max(
            range(N_OPS),
            key=lambda a: self.stats[a].mean + BETA * math.sqrt(math.log(self.total) / self.stats[a].n),
        )

    def update(self, op, bucket, reward, quality, t):
        self.stats[op].update(reward)


class BucketUCB(Policy):
    """State-conditioned UCB on raw rewards (this IS the defensible core)."""

    name = "bucket_ucb"

    def __init__(self):
        self.stats = {(b, a): ArmStat() for b in range(N_BUCKETS) for a in range(N_OPS)}
        self.n_bucket = {b: 0 for b in range(N_BUCKETS)}

    def select(self, bucket, t, quality):
        self.n_bucket[bucket] += 1
        for a in range(N_OPS):
            if self.stats[(bucket, a)].n == 0:
                return a
        return max(
            range(N_OPS),
            key=lambda a: self.stats[(bucket, a)].mean
            + BETA * math.sqrt(math.log(self.n_bucket[bucket]) / self.stats[(bucket, a)].n),
        )

    def update(self, op, bucket, reward, quality, t):
        self.stats[(bucket, op)].update(reward)


class BucketBaselineUCB(Policy):
    """CC-SOC current formula: mean(r|a,b) - mean(r|·,b) + UCB.

    Expect: decision-equivalent to BucketUCB (constant per bucket).
    """

    name = "bucket_baseline_ucb"

    def __init__(self):
        self.stats = {(b, a): ArmStat() for b in range(N_BUCKETS) for a in range(N_OPS)}
        self.bucket_stat = {b: ArmStat() for b in range(N_BUCKETS)}
        self.n_bucket = {b: 0 for b in range(N_BUCKETS)}

    def select(self, bucket, t, quality):
        self.n_bucket[bucket] += 1
        for a in range(N_OPS):
            if self.stats[(bucket, a)].n == 0:
                return a
        const = self.bucket_stat[bucket].mean
        return max(
            range(N_OPS),
            key=lambda a: self.stats[(bucket, a)].mean - const
            + BETA * math.sqrt(math.log(self.n_bucket[bucket]) / self.stats[(bucket, a)].n),
        )

    def update(self, op, bucket, reward, quality, t):
        self.stats[(bucket, op)].update(reward)
        self.bucket_stat[bucket].update(reward)


class QualityAdjustedUCB(Policy):
    """Corrected CC-SOC: residual reward r' = r - g(quality, bucket).

    g is a running linear estimate E[r|quality,bucket] fit on all data in b.
    Addresses individual-quality confounding (Scenario C) that bucketing alone
    cannot remove. Then UCB on residual means.
    """

    name = "ccsoc_quality_adjusted"

    def __init__(self):
        self.stats = {(b, a): ArmStat() for b in range(N_BUCKETS) for a in range(N_OPS)}
        self.n_bucket = {b: 0 for b in range(N_BUCKETS)}
        # online running mean of reward and quality per bucket (1-d residualization)
        self.sum_r = {b: 0.0 for b in range(N_BUCKETS)}
        self.sum_q = {b: 0.0 for b in range(N_BUCKETS)}
        self.sum_qq = {b: 0.0 for b in range(N_BUCKETS)}
        self.sum_rq = {b: 0.0 for b in range(N_BUCKETS)}
        self.cnt = {b: 0 for b in range(N_BUCKETS)}

    def _g_hat(self, bucket: int, quality: float) -> float:
        n = self.cnt[bucket]
        if n < 5:
            return 0.0
        # least-squares slope of r on quality
        num = self.sum_rq[bucket] - self.sum_r[bucket] * self.sum_q[bucket] / n
        den = self.sum_qq[bucket] - self.sum_q[bucket] ** 2 / n
        if abs(den) < 1e-9:
            return self.sum_r[bucket] / n
        slope = num / den
        intercept = self.sum_r[bucket] / n - slope * self.sum_q[bucket] / n
        return intercept + slope * quality

    def select(self, bucket, t, quality):
        self.n_bucket[bucket] += 1
        for a in range(N_OPS):
            if self.stats[(bucket, a)].n == 0:
                return a
        return max(
            range(N_OPS),
            key=lambda a: self.stats[(bucket, a)].mean
            + BETA * math.sqrt(math.log(self.n_bucket[bucket]) / self.stats[(bucket, a)].n),
        )

    def update(self, op, bucket, reward, quality, t):
        resid = reward - self._g_hat(bucket, quality)
        self.stats[(bucket, op)].update(resid)
        n = self.cnt[bucket] + 1
        self.sum_r[bucket] += reward
        self.sum_q[bucket] += quality
        self.sum_qq[bucket] += quality * quality
        self.sum_rq[bucket] += reward * quality
        self.cnt[bucket] = n


# ---------------------------------------------------------------------------
# Evaluation loop
# ---------------------------------------------------------------------------

def run_one(scenario: str, policy: Policy, seed: int) -> Dict[str, Any]:
    rng = np.random.RandomState(seed)
    true_opts = []
    picks = []
    for t in range(HORIZON):
        bucket = int(rng.rand() < 0.5)  # context arrives exogenously
        quality = float(rng.uniform(0, 1))
        best = max(range(N_OPS), key=lambda a: true_mean(scenario, a, bucket, quality, t))
        true_opts.append((bucket, best))
        op = policy.select(bucket, t, quality)
        picks.append(op)
        r = draw_reward(scenario, op, bucket, quality, t, rng)
        policy.update(op, bucket, r, quality, t)

    oracle_regret = 0.0
    correct = 0
    for t, (op) in enumerate(picks):
        bucket, best = true_opts[t]
        quality = 0.5  # regret against mean-optimal at median quality for comparability
        mu_best = true_mean(scenario, best, bucket, quality, t)
        mu_act = true_mean(scenario, op, bucket, quality, t)
        oracle_regret += max(0.0, mu_best - mu_act)
        if op == best:
            correct += 1

    # switch rate
    switches = sum(1 for i in range(1, len(picks)) if picks[i] != picks[i - 1])
    # coverage
    cover = {(b, a): 0 for b in range(N_BUCKETS) for a in range(N_OPS)}
    for t, op in enumerate(picks):
        cover[(true_opts[t][0], op)] += 1
    return {
        "scenario": scenario,
        "policy": policy.name,
        "seed": seed,
        "regret": oracle_regret,
        "opt_id_rate": correct / HORIZON,
        "switches": switches,
        "coverage": {f"b{b}_a{a}": cover[(b, a)] for b in range(N_BUCKETS) for a in range(N_OPS)},
    }


def make_policy(name: str, seed: int, scenario: str) -> Policy:
    if name == "random":
        return RandomPolicy(seed)
    if name == "oracle":
        return OraclePolicy(scenario)
    if name == "raw_ucb":
        return UCBPolicy()
    if name == "bucket_ucb":
        return BucketUCB()
    if name == "bucket_baseline_ucb":
        return BucketBaselineUCB()
    if name == "ccsoc_quality_adjusted":
        return QualityAdjustedUCB()
    raise ValueError(name)


SCENARIOS = [
    "A_no_confounding",
    "B_state_difficulty",
    "C_quality_confounding",
    "D_near_tie",
    "E_drift",
]
POLICIES = [
    "random",
    "oracle",
    "raw_ucb",
    "bucket_ucb",
    "bucket_baseline_ucb",
    "ccsoc_quality_adjusted",
]


def main() -> None:
    rows = []
    for scenario in SCENARIOS:
        for pname in POLICIES:
            for seed in SEEDS:
                p = make_policy(pname, seed, scenario)
                rows.append(run_one(scenario, p, seed))
    # equivalence check: bucket_baseline_ucb vs bucket_ucb regret difference
    equiv = []
    for scenario in SCENARIOS:
        for seed in SEEDS:
            r1 = next(r["regret"] for r in rows if r["scenario"] == scenario and r["policy"] == "bucket_ucb" and r["seed"] == seed)
            r2 = next(r["regret"] for r in rows if r["scenario"] == scenario and r["policy"] == "bucket_baseline_ucb" and r["seed"] == seed)
            equiv.append(abs(r1 - r2))
    max_diff = max(equiv)
    mean_diff = sum(equiv) / len(equiv)

    summary = {
        "hypothesis": "bucket-baseline subtraction is decision-equivalent to bucket UCB (constant per bucket)",
        "max_regret_diff_bucket_vs_baseline": max_diff,
        "mean_regret_diff": mean_diff,
        "equivalent_if_diff_tiny": max_diff < 1e-9,
        "rows": rows,
        "params": {"horizon": HORIZON, "beta": BETA, "seeds": SEEDS, "n_ops": N_OPS, "n_buckets": N_BUCKETS},
    }
    out = ROOT / "results" / "phase1a3r"
    out.mkdir(parents=True, exist_ok=True)
    (out / "synthetic_falsification.json").write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    print("max diff bucket_ucb vs bucket_baseline_ucb:", max_diff)
    # per-scenario means
    for scenario in SCENARIOS:
        print("==", scenario)
        for pname in POLICIES:
            vals = [r["regret"] for r in rows if r["scenario"] == scenario and r["policy"] == pname]
            opts = [r["opt_id_rate"] for r in rows if r["scenario"] == scenario and r["policy"] == pname]
            print(f"  {pname:24} regret={sum(vals)/len(vals):.4f} opt_id={sum(opts)/len(opts):.3f}")
    print("WROTE", out / "synthetic_falsification.json")


if __name__ == "__main__":
    main()
