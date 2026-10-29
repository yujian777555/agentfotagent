"""Phase-1A-8 Stage B gate: A0 must be bitwise identical to canonical L-SHADE."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.metabox.agent_assisted_ec.lshade_canonical import run_lshade_canonical  # noqa: E402
from experiments.metabox.agent_assisted_ec.lshade_factorial import run_lshade_factorial  # noqa: E402


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


class TestA0Equivalence:
    @pytest.mark.parametrize("seed", [11, 22, 33])
    def test_a0_bitwise(self, seed):
        p1, p2 = SphereStub(), SphereStub()
        r_ref = run_lshade_canonical(p1, max_fes=1200, seed=seed, n_init=30, n_min=4)
        r_a0 = run_lshade_factorial(
            p2, max_fes=1200, seed=seed, use_archive=True, repair_method="clip",
            n_init=30, n_min=4,
        )
        assert r_ref.raw_curve == r_a0.raw_curve
        assert r_ref.n_history == r_a0.n_history
        assert r_ref.best_raw == r_a0.best_raw
        assert r_ref.fes == r_a0.fes

    def test_a0_real_function(self):
        from experiments.metabox.adapter import load_function
        h1, h2 = load_function(1), load_function(1)
        r_ref = run_lshade_canonical(h1._problem, max_fes=500, seed=11, n_init=100, n_min=4)
        r_a0 = run_lshade_factorial(
            h2._problem, max_fes=500, seed=11, use_archive=True, repair_method="clip",
            n_init=100, n_min=4,
        )
        assert r_ref.raw_curve == r_a0.raw_curve
        assert r_ref.best_raw == r_a0.best_raw

    def test_arms_run_and_fe_exact(self):
        for arm_kwargs in [
            {"use_archive": True, "repair_method": "clip"},
            {"use_archive": False, "repair_method": "clip"},
            {"use_archive": True, "repair_method": "parent_midpoint"},
            {"use_archive": False, "repair_method": "parent_midpoint"},
        ]:
            p = SphereStub()
            r = run_lshade_factorial(p, max_fes=800, seed=5, n_init=25, n_min=4, **arm_kwargs)
            assert r.fe_exact
            assert r.fes == 800
            assert r.independent_fes == 800

    def test_no_archive_empty_donor(self):
        """With use_archive=False, archive should stay empty."""
        p = SphereStub()
        r = run_lshade_factorial(p, max_fes=600, seed=3, use_archive=False, repair_method="clip", n_init=20, n_min=4)
        assert r.total_archive_r2 == 0
        assert r.total_pop_r2 > 0

    def test_midpoint_differs_from_clip(self):
        """Parent-midpoint repair must produce different results from clipping."""
        p1, p2 = SphereStub(dim=8), SphereStub(dim=8)
        r_clip = run_lshade_factorial(p1, max_fes=800, seed=7, use_archive=True, repair_method="clip", n_init=25, n_min=4)
        r_mid = run_lshade_factorial(p2, max_fes=800, seed=7, use_archive=True, repair_method="parent_midpoint", n_init=25, n_min=4)
        assert r_clip.raw_curve != r_mid.raw_curve
