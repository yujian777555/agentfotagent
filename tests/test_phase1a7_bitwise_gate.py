"""Phase-1A-7 blocking gate: diagnostic runner must be bitwise-identical.

Compares lshade_canonical_diag.run_lshade_canonical_diag against
lshade_canonical.run_lshade_canonical on:
- raw_curve (exact float equality element-wise)
- benchmark_cost_curve
- n_history
- final best_raw
- fes / independent_fes

Also validates diagnostic-log integrity (no NaN, indices legal, etc.).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.metabox.agent_assisted_ec.lshade_canonical import (  # noqa: E402
    run_lshade_canonical,
)
from experiments.metabox.agent_assisted_ec.lshade_canonical_diag import (  # noqa: E402
    DIAGNOSTIC_DEFINITIONS,
    run_lshade_canonical_diag,
)


class SphereStub:
    def __init__(self, dim: int = 6, bias: float = 10.0):
        self.dim = dim
        self.lb = -5.0
        self.ub = 5.0
        self.optimum = bias
        self.reset()

    def reset(self):
        self.n_evals = 0

    def eval(self, x):
        arr = np.asarray(x, dtype=np.float64).reshape(-1)
        self.n_evals += 1
        return float(np.sum(arr ** 2) + self.optimum)


class TestBitwiseIdentity:
    """Blocking gate: diagnostic path must not alter search trajectory."""

    @pytest.mark.parametrize("seed", [11, 22, 33])
    @pytest.mark.parametrize("budget", [500, 1200])
    def test_raw_curve_bitwise(self, seed, budget):
        p1 = SphereStub()
        p2 = SphereStub()
        r_ref = run_lshade_canonical(p1, max_fes=budget, seed=seed, n_init=30, n_min=4)
        r_diag = run_lshade_canonical_diag(p2, max_fes=budget, seed=seed, n_init=30, n_min=4)

        assert r_ref.raw_curve == r_diag.raw_curve, (
            f"raw_curve diverged at seed={seed} budget={budget}"
        )
        assert r_ref.n_history == r_diag.n_history
        assert r_ref.best_raw == r_diag.best_raw
        assert r_ref.fes == r_diag.fes
        assert r_ref.independent_fes == r_diag.independent_fes

    @pytest.mark.parametrize("seed", [11, 22])
    def test_benchmark_cost_curve_bitwise(self, seed):
        p1 = SphereStub()
        p2 = SphereStub()
        r_ref = run_lshade_canonical(p1, max_fes=800, seed=seed, n_init=25, n_min=4)
        r_diag = run_lshade_canonical_diag(p2, max_fes=800, seed=seed, n_init=25, n_min=4)
        assert r_ref.benchmark_cost_curve == r_diag.benchmark_cost_curve

    def test_real_function_bitwise(self):
        """Bitwise identity on a real BBOB function (F1)."""
        from experiments.metabox.adapter import load_function

        h1 = load_function(1)
        h2 = load_function(1)
        r_ref = run_lshade_canonical(h1._problem, max_fes=500, seed=11, n_init=100, n_min=4)
        r_diag = run_lshade_canonical_diag(h2._problem, max_fes=500, seed=11, n_init=100, n_min=4)
        assert r_ref.raw_curve == r_diag.raw_curve
        assert r_ref.n_history == r_diag.n_history
        assert r_ref.best_raw == r_diag.best_raw


class TestDiagnosticLogIntegrity:
    def test_log_covers_all_generations(self):
        p = SphereStub()
        r = run_lshade_canonical_diag(p, max_fes=1000, seed=7, n_init=25, n_min=4)
        # n_history has init entry + one per generation
        assert len(r.gen_logs) == len(r.n_history) - 1

    def test_log_fields_complete(self):
        p = SphereStub()
        r = run_lshade_canonical_diag(p, max_fes=600, seed=3, n_init=20, n_min=4)
        required = {
            "fe", "gen", "N", "best", "median", "worst", "diversity",
            "successes", "attempts", "success_rate",
            "success_F", "success_CR", "success_df",
            "M_F_before", "M_F_after", "M_CR_before", "M_CR_after",
            "memory_slot", "archive_size", "n_success_candidates",
            "pbest_ok", "r_index_ok", "improvement", "stall_gen",
        }
        for lg in r.gen_logs:
            assert required.issubset(lg.keys()), f"missing fields: {required - lg.keys()}"

    def test_all_definitions_present(self):
        keys_in_logs = {
            "fe", "gen", "N", "best", "median", "worst", "diversity",
            "successes", "attempts", "success_rate",
            "success_F", "success_CR", "success_df",
            "M_F_before", "M_F_after", "M_CR_before", "M_CR_after",
            "memory_slot", "archive_size", "n_success_candidates",
            "pbest_ok", "r_index_ok", "improvement", "stall_gen",
        }
        assert keys_in_logs == set(DIAGNOSTIC_DEFINITIONS.keys())

    def test_no_nan_in_logs(self):
        p = SphereStub()
        r = run_lshade_canonical_diag(p, max_fes=1500, seed=5, n_init=30, n_min=4)
        for lg in r.gen_logs:
            for k in ("best", "median", "worst", "diversity", "success_rate", "improvement"):
                v = lg[k]
                assert np.isfinite(v), f"non-finite {k}={v} at gen={lg['gen']}"

    def test_index_validity_flags(self):
        p = SphereStub()
        r = run_lshade_canonical_diag(p, max_fes=1500, seed=5, n_init=30, n_min=4)
        for lg in r.gen_logs:
            assert lg["pbest_ok"] is True
            assert lg["r_index_ok"] is True

    def test_fe_monotonic_in_logs(self):
        p = SphereStub()
        r = run_lshade_canonical_diag(p, max_fes=1200, seed=9, n_init=25, n_min=4)
        fes = [lg["fe"] for lg in r.gen_logs]
        for a, b in zip(fes, fes[1:]):
            assert b >= a

    def test_success_rate_bounds(self):
        p = SphereStub()
        r = run_lshade_canonical_diag(p, max_fes=1200, seed=9, n_init=25, n_min=4)
        for lg in r.gen_logs:
            assert 0.0 <= lg["success_rate"] <= 1.0
            assert 0 <= lg["successes"] <= lg["attempts"]

    def test_memory_slot_range(self):
        p = SphereStub()
        r = run_lshade_canonical_diag(p, max_fes=1500, seed=13, n_init=30, n_min=4)
        for lg in r.gen_logs:
            assert lg["memory_slot"] == -1 or 0 <= lg["memory_slot"] < 5

    def test_diversity_nonnegative(self):
        p = SphereStub()
        r = run_lshade_canonical_diag(p, max_fes=1000, seed=17, n_init=25, n_min=4)
        for lg in r.gen_logs:
            assert lg["diversity"] >= 0.0

    def test_stall_counter_consistency(self):
        p = SphereStub()
        r = run_lshade_canonical_diag(p, max_fes=1500, seed=21, n_init=30, n_min=4)
        expected_stall = 0
        for lg in r.gen_logs:
            if lg["improvement"] <= 0:
                expected_stall += 1
            else:
                expected_stall = 0
            assert lg["stall_gen"] == expected_stall

    def test_fe_exact(self):
        p = SphereStub()
        r = run_lshade_canonical_diag(p, max_fes=900, seed=2, n_init=20, n_min=4)
        assert r.fe_exact
        assert r.fes == 900
        assert r.independent_fes == 900
