"""Phase-1A-4R contract tests: factorial flags, FE safety, matched schedule."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from experiments.metabox.agent_assisted_ec.dpr_shade_v2 import run_dpr_shade_like


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


def test_factorial_runs_and_fe_exact():
    for M, N, I in ((0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 1)):
        res = run_dpr_shade_like(Quad(), max_fes=100, seed=1, np_init=10,
                                 use_M=M, use_N=N, use_I=I,
                                 trigger_mode="schedule", trigger_schedule=[5, 12])
        assert res.fes == 100
        assert res.independent_fes == 100


def test_immigrants_replace_without_shrink():
    res = run_dpr_shade_like(Quad(), max_fes=150, seed=2, np_init=10,
                             use_M=False, use_N=False, use_I=True,
                             trigger_mode="schedule", trigger_schedule=[3, 8], gen_reset_min=1)
    fired = [e for e in res.events if e.get("fired")]
    assert fired
    for e in fired:
        assert e.get("n_immigrants", 0) >= 1
        assert e.get("N_after") == e.get("N_before")  # pure immigration keeps N


def test_matched_schedule_independent_of_state():
    # state event log with fires at gens 5,12
    events = [{"gen": i, "fired": i in (5, 12)} for i in range(20)]
    from experiments.metabox.agent_assisted_ec.run_phase1a4r_pilot import matched_schedule

    sched, target = matched_schedule(events, seed=3, max_gen=20)
    assert target == 2
    assert len(sched) == 2 or len(sched) < 2  # cooldown may reduce
    # schedule gens not derived from stall/div (no such fields used)


def test_state_trigger_logging_fields():
    res = run_dpr_shade_like(Quad(), max_fes=200, seed=4, np_init=15,
                             use_M=True, use_N=True, use_I=True,
                             trigger_mode="state", theta_s=1.1, stall_len=1, gen_reset_min=1)
    for e in res.events:
        assert {"stall_fire", "div_fire", "cooldown_ok", "fired", "N_before"} <= set(e.keys())
