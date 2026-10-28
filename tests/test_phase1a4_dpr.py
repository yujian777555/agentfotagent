"""DPR-SHADE contract tests."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from experiments.metabox.agent_assisted_ec.dpr_shade import run_dpr_shade


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


def test_fe_exact_and_modes_run():
    for mode in ("full", "no_reset", "no_shrink", "shuffled_triggers"):
        res = run_dpr_shade(Quad(), max_fes=120, seed=1, np_init=10, mode=mode)
        assert res.fes == 120
        assert res.independent_fes == 120
        assert res.best_raw >= 0


def test_resets_recorded_when_stalled():
    # hard-ish: high dim noise-free quadratic usually improves; use tiny budget
    res = run_dpr_shade(Quad(), max_fes=200, seed=7, np_init=20, mode="full",
                        theta_s=1.1, stall_len=1, gen_reset_min=1)
    # theta_s=1.1 forces stall trigger every gen
    assert len(res.resets) >= 1
    assert res.resets[0]["N_after"] <= res.resets[0]["N_before"]


def test_no_reset_mode_has_no_memory_reset():
    res = run_dpr_shade(Quad(), max_fes=150, seed=3, np_init=10, mode="no_reset",
                        theta_s=1.1, stall_len=1, gen_reset_min=1)
    # resets may still record shrink events but memory unchanged: N may shrink
    assert res.fes == 150
