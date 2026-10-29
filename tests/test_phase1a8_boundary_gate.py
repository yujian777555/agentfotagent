"""Phase-1A-8 Stage A blocking gate: boundary-diag must be bitwise identical.

Compares lshade_boundary_diag.run_lshade_boundary_diag against
lshade_canonical.run_lshade_canonical on raw_curve, benchmark_cost_curve,
n_history, best_raw, FE counts.

Also validates boundary-event log integrity.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.metabox.agent_assisted_ec.lshade_canonical import run_lshade_canonical  # noqa: E402
from experiments.metabox.agent_assisted_ec.lshade_boundary_diag import (  # noqa: E402
    BOUNDARY_DEFINITIONS,
    run_lshade_boundary_diag,
)


class SphereStub:
    def __init__(self, dim=6, bias=10.0):
        self.dim = dim
        self.lb = -5.0
        self.ub = 5.0
        self.optimum = bias
        self.reset()

    def reset(self):
        pass

    def eval(self, x):
        arr = np.asarray(x, dtype=np.float64).reshape(-1)
        return float(np.sum(arr ** 2) + self.optimum)


class TestBoundaryBitwiseIdentity:
    @pytest.mark.parametrize("seed", [11, 22, 33])
    def test_raw_curve_bitwise(self, seed):
        p1, p2 = SphereStub(), SphereStub()
        r_ref = run_lshade_canonical(p1, max_fes=1200, seed=seed, n_init=30, n_min=4)
        r_diag = run_lshade_boundary_diag(p2, max_fes=1200, seed=seed, n_init=30, n_min=4)
        assert r_ref.raw_curve == r_diag.raw_curve
        assert r_ref.n_history == r_diag.n_history
        assert r_ref.best_raw == r_diag.best_raw
        assert r_ref.fes == r_diag.fes

    @pytest.mark.parametrize("seed", [11, 22])
    def test_benchmark_cost_bitwise(self, seed):
        p1, p2 = SphereStub(), SphereStub()
        r_ref = run_lshade_canonical(p1, max_fes=800, seed=seed, n_init=25, n_min=4)
        r_diag = run_lshade_boundary_diag(p2, max_fes=800, seed=seed, n_init=25, n_min=4)
        assert r_ref.benchmark_cost_curve == r_diag.benchmark_cost_curve

    def test_real_function_bitwise(self):
        from experiments.metabox.adapter import load_function
        h1, h2 = load_function(1), load_function(1)
        r_ref = run_lshade_canonical(h1._problem, max_fes=500, seed=11, n_init=100, n_min=4)
        r_diag = run_lshade_boundary_diag(h2._problem, max_fes=500, seed=11, n_init=100, n_min=4)
        assert r_ref.raw_curve == r_diag.raw_curve
        assert r_ref.best_raw == r_diag.best_raw


class TestBoundaryLogIntegrity:
    def test_all_definitions_present(self):
        p = SphereStub()
        r = run_lshade_boundary_diag(p, max_fes=800, seed=5, n_init=25, n_min=4)
        keys = set(r.gen_logs[0].keys())
        assert keys == set(BOUNDARY_DEFINITIONS.keys())

    def test_no_nan(self):
        p = SphereStub()
        r = run_lshade_boundary_diag(p, max_fes=1500, seed=7, n_init=30, n_min=4)
        for lg in r.gen_logs:
            for k in ("oob_trial_frac", "oob_coord_frac", "mean_repair_L2", "archive_r2_frac"):
                assert np.isfinite(lg[k])

    def test_oob_counts_consistent(self):
        p = SphereStub()
        r = run_lshade_boundary_diag(p, max_fes=1500, seed=7, n_init=30, n_min=4)
        for lg in r.gen_logs:
            assert lg["n_oob_trials"] <= lg["n_trials"]
            assert 0.0 <= lg["oob_trial_frac"] <= 1.0
            assert lg["n_archive_r2"] + lg["n_pop_r2"] <= lg["n_trials"]

    def test_repair_cosine_range(self):
        p = SphereStub()
        r = run_lshade_boundary_diag(p, max_fes=1500, seed=13, n_init=30, n_min=4)
        for lg in r.gen_logs:
            if lg["mean_repair_cosine"] != 0.0:
                assert -1.01 <= lg["mean_repair_cosine"] <= 1.01

    def test_fe_exact(self):
        p = SphereStub()
        r = run_lshade_boundary_diag(p, max_fes=900, seed=2, n_init=20, n_min=4)
        assert r.fe_exact
        assert r.fes == 900
