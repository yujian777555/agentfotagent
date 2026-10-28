"""L-SHADE reimplementation contract tests."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from experiments.metabox.agent_assisted_ec.lshade_reimpl import run_lshade


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


def test_lshade_fe_exact():
    res = run_lshade(Quad(), max_fes=500, seed=1, n_init=20)
    assert res.fes == 500
    assert res.independent_fes == 500
    assert res.algorithm_id == "lshade-reimpl"


def test_lshade_linear_population_reduces():
    res = run_lshade(Quad(), max_fes=400, seed=2, n_init=50, n_min=4)
    assert res.n_history[0] == 50
    assert res.n_history[-1] <= 50
    assert min(res.n_history) >= 4


def test_intervention_replay_exact_fires():
    ivs = [{"fe": 150, "do_N": True, "do_I": True}, {"fe": 300, "do_N": True, "do_I": True}]
    res = run_lshade(Quad(), max_fes=400, seed=3, n_init=20, interventions=ivs)
    assert len(res.events) == 2
    assert all(e["n_immigrants"] >= 1 for e in res.events)
    assert res.fes == 400


def test_effective_shrink_flag():
    ivs = [{"fe": 50, "do_N": True, "do_I": False}]
    res = run_lshade(Quad(), max_fes=300, seed=4, n_init=20, n_min=100, interventions=ivs)
    # N cannot shrink below n_min=100 > 20? n_init=20 already < n_min, so shrink no-op
    assert res.events[0]["effective_shrink"] is False
