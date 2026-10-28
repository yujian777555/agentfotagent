"""Phase-1A-4R2 contract tests: exact-count matching."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from experiments.metabox.agent_assisted_ec.dpr_shade_v2 import run_dpr_shade_like
from experiments.metabox.agent_assisted_ec.run_phase1a4r2_pilot import (
    COOLDOWN_FE,
    exact_fe_schedule,
)


class Quad:
    dim = 5
    lb = -20.0
    ub = 20.0
    optimum = 0.0

    def reset(self):
        pass

    def eval(self, x):
        x = np.asarray(x).reshape(-1)
        return float(np.dot(x, x))


def test_exact_schedule_has_k_thresholds():
    for k in (0, 1, 5, 14):
        sched = exact_fe_schedule(k, seed=7, max_fes=500)
        assert len(sched) == k
        assert all(50 <= s <= 490 for s in sched)
        assert all(b - a >= COOLDOWN_FE for a, b in zip(sched, sched[1:]))


def test_exact_schedule_impossible_returns_empty():
    # k larger than available slots must return [] (MATCH IMPOSSIBLE)
    sched = exact_fe_schedule(100, seed=1, max_fes=500)
    assert sched == []


def test_random_arm_fires_exactly_k_times():
    # schedule 3 interventions; expect exactly 3 fires
    sched = exact_fe_schedule(3, seed=5, max_fes=400)
    assert len(sched) == 3
    res = run_dpr_shade_like(
        Quad(), max_fes=400, seed=5, np_init=15,
        use_M=False, use_N=True, use_I=True,
        trigger_mode="matched_fe", trigger_fe_schedule=sched,
        gen_reset_min=1,
    )
    fired = sum(1 for e in res.events if e.get("fired"))
    assert fired == 3, f"expected exactly 3 fires, got {fired}"
    assert res.fes == 400
    assert res.independent_fes == 400


def test_random_schedule_no_state_fields_used():
    # schedule generation must not read stall/div
    sched = exact_fe_schedule(2, seed=9, max_fes=500)
    assert all(isinstance(s, int) for s in sched)
    # FE values only — no state dependence
    sched2 = exact_fe_schedule(2, seed=9, max_fes=500)
    assert sched == sched2  # deterministic given seed
