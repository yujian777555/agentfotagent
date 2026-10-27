"""P0-R1-Corrective tests: FE identity, live controller state, metrics, fail-closed actions.

Synthetic-function unit tests prove controller logic only. Real MetaBox
integration tests are kept alongside and must not be treated as science.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from experiments.metabox.controller_dsl import (
    ControllerValidationError,
    compile_controller,
    fixed_controller_a,
    fixed_controller_b,
    validate_controller_spec,
)
from experiments.metabox.controlled_de import (
    ControlledDEResult,
    _features,
    run_controlled_de,
)


# ---------------------------------------------------------------------------
# Synthetic deterministic problem (logic unit tests only — NOT scientific evidence)
# ---------------------------------------------------------------------------

class SyntheticQuadratic:
    """minimize ||x||^2 over [-100,100]^dim. optimum=0 known for regret metric."""

    def __init__(self, dim: int = 5):
        self.dim = dim
        self.lb = -100.0
        self.ub = 100.0
        self.optimum = 0.0

    def reset(self):
        self.T1 = 0

    def eval(self, x):
        arr = np.asarray(x, dtype=np.float64).reshape(-1)
        return float(np.dot(arr, arr))


class SyntheticNoOptimum(SyntheticQuadratic):
    def __init__(self, dim: int = 5):
        super().__init__(dim)
        self.optimum = None


# ---------------------------------------------------------------------------
# Controller semantics
# ---------------------------------------------------------------------------

def test_first_generation_state_is_initialized():
    p = SyntheticQuadratic()
    ctrl = compile_controller(fixed_controller_a())
    res = run_controlled_de(p, ctrl, max_fes=40, seed=1, np_size=10)
    s0 = res.action_events[0]["state"]
    assert s0["generation"] == 0.0
    assert s0["success_fraction"] == 0.0  # no previous generation
    assert s0["budget_fraction"] > 0.0


def test_next_generation_success_fraction_matches_previous():
    p = SyntheticQuadratic()
    ctrl = compile_controller(fixed_controller_a())
    res = run_controlled_de(p, ctrl, max_fes=80, seed=2, np_size=10)
    assert len(res.action_events) >= 2
    gen0 = res.action_events[0]
    gen1 = res.action_events[1]
    assert gen1["state"]["success_fraction"] == pytest.approx(gen0["success_fraction_this_gen"])
    # And it is a real successes/attempted value
    assert gen0["attempted"] > 0
    assert gen0["success_fraction_this_gen"] == pytest.approx(
        gen0["successes"] / gen0["attempted"]
    )


def test_success_fraction_not_hardcoded_zero_after_gen0():
    p = SyntheticQuadratic()
    ctrl = compile_controller(fixed_controller_a())
    res = run_controlled_de(p, ctrl, max_fes=120, seed=3, np_size=10)
    # After the first generation, state must carry the previous real fraction
    # (may be 0.0 only if literally no successes — assert the field is wired).
    assert "success_fraction" in res.action_events[1]["state"]
    assert res.action_events[1]["state"]["success_fraction"] == pytest.approx(
        res.action_events[0]["success_fraction_this_gen"]
    )


def test_stagnation_rule_actually_fires_and_F_changes():
    """Must observe BOTH F=0.5 (initial) and F=0.8 (post-stagnation)."""
    # Use a controller that always increases F after stagnation >= 2 generations.
    spec = {
        "schema_version": "aes-controller-dsl-v2",
        "controller_id": "stag_switch",
        "initial_action": {"action": "set_F", "params": {"value": 0.5}},
        "rules": [
            {
                "when": {"stagnation_steps": {"op": ">=", "value": 2.0}},
                "then": {"action": "set_F", "params": {"value": 0.8}},
            }
        ],
    }
    ctrl = compile_controller(spec)
    p = SyntheticQuadratic()
    # Plateau-friendly: tiny budget so improvement stalls quickly
    res = run_controlled_de(p, ctrl, max_fes=200, seed=7, np_size=15)

    f_used = [e["F_used"] for e in res.action_events]
    assert 0.5 in f_used, "initial F must be applied"
    assert 0.8 in f_used, "stagnation rule must fire and apply F=0.8"

    # The firing event must itself satisfy the rule condition.
    fire = next(e for e in res.action_events if e["effect"].get("F") == 0.8)
    assert fire["state"]["stagnation_steps"] >= 2.0
    assert fire["action"]["action"] == "set_F"
    assert fire["action"]["params"]["value"] == 0.8
    assert fire["effect"]["F"] == 0.8
    assert fire["F_used"] == 0.8


def test_state_change_selects_different_action():
    ctrl = compile_controller(fixed_controller_a())
    s0 = {
        "generation": 0.0,
        "improvement_rate": 0.0,
        "stagnation_steps": 0.0,
        "population_diversity": 1.0,
        "success_fraction": 0.0,
        "budget_fraction": 0.0,
    }
    s1 = dict(s0, stagnation_steps=10.0, budget_fraction=0.9)
    a0 = ctrl.select_action(s0)
    a1 = ctrl.select_action(s1)
    assert a0 != a1


def test_applied_F_CR_match_controller_actions():
    spec = {
        "schema_version": "aes-controller-dsl-v2",
        "controller_id": "const_f",
        "initial_action": {"action": "set_F", "params": {"value": 0.9}},
        "rules": [],
    }
    ctrl = compile_controller(spec)
    p = SyntheticQuadratic()
    res = run_controlled_de(p, ctrl, max_fes=100, seed=5, np_size=10)
    assert res.applied_F_history[0] == 0.9
    for i, ev in enumerate(res.action_events):
        assert ev["F_used"] == res.applied_F_history[i]
        assert ev["CR_used"] == res.applied_CR_history[i]
        if ev["effect"].get("applied") == "set_F":
            assert ev["F_used"] == ev["effect"]["F"] == ev["action"]["params"]["value"]


def test_controller_state_has_no_hidden_optimum():
    p = SyntheticQuadratic()
    ctrl = compile_controller(fixed_controller_a())
    res = run_controlled_de(p, ctrl, max_fes=60, seed=11, np_size=10)
    for ev in res.action_events:
        assert set(ev["state"].keys()) == {
            "generation",
            "improvement_rate",
            "stagnation_steps",
            "population_diversity",
            "success_fraction",
            "budget_fraction",
        }
        assert "optimum" not in ev["state"]
        blob = str(ev["state"])
        assert "test" not in blob.lower()


def test_seed_reproducible_states_actions_results():
    ctrl = compile_controller(fixed_controller_a())
    p1, p2 = SyntheticQuadratic(), SyntheticQuadratic()
    r1 = run_controlled_de(p1, ctrl, max_fes=100, seed=21, np_size=10)
    r2 = run_controlled_de(p2, ctrl, max_fes=100, seed=21, np_size=10)
    assert r1.cost_curve == r2.cost_curve
    assert r1.action_events == r2.action_events
    assert r1.independent_fes == r2.independent_fes
    assert r1.best_raw_objective == r2.best_raw_objective


# ---------------------------------------------------------------------------
# FE accounting
# ---------------------------------------------------------------------------

def test_fe_exact_budget_and_independent_match():
    p = SyntheticQuadratic()
    ctrl = compile_controller(fixed_controller_a())
    res = run_controlled_de(p, ctrl, max_fes=100, seed=4, np_size=10)
    assert res.fes == 100
    assert res.independent_fes == 100
    assert res.init_fes == 10
    assert res.max_fes == 100


def test_budget_below_population_rejected():
    p = SyntheticQuadratic()
    ctrl = compile_controller(fixed_controller_a())
    with pytest.raises(ValueError):
        run_controlled_de(p, ctrl, max_fes=5, seed=1, np_size=10)


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def test_regret_metric_when_optimum_known():
    p = SyntheticQuadratic()
    ctrl = compile_controller(fixed_controller_a())
    res = run_controlled_de(p, ctrl, max_fes=80, seed=8, np_size=10)
    assert res.primary_metric == "regret"
    assert res.regret_curve is not None
    assert res.best_regret == pytest.approx(res.best_raw_objective - 0.0)
    assert res.cost_curve[0] >= 0.0


def test_raw_objective_when_optimum_unknown():
    p = SyntheticNoOptimum()
    ctrl = compile_controller(fixed_controller_a())
    res = run_controlled_de(p, ctrl, max_fes=80, seed=9, np_size=10)
    assert res.primary_metric == "raw_objective"
    assert res.regret_curve is None
    assert res.best_regret is None


# ---------------------------------------------------------------------------
# Fail-closed unsupported actions
# ---------------------------------------------------------------------------

def test_controlled_de_rejects_restart():
    p = SyntheticQuadratic()
    spec = {
        "schema_version": "aes-controller-dsl-v2",
        "controller_id": "bad",
        "initial_action": {"action": "restart", "params": {"max_fraction": 0.1}},
        "rules": [],
    }
    ctrl = compile_controller(spec)
    with pytest.raises(RuntimeError, match="restart"):
        run_controlled_de(p, ctrl, max_fes=40, seed=1, np_size=10)


def test_controlled_de_rejects_mutation_strategy():
    p = SyntheticQuadratic()
    spec = {
        "schema_version": "aes-controller-dsl-v2",
        "controller_id": "bad2",
        "initial_action": {"action": "set_mutation_strategy", "params": {"strategy": "best/1/bin"}},
        "rules": [],
    }
    ctrl = compile_controller(spec)
    with pytest.raises(RuntimeError, match="mutation"):
        run_controlled_de(p, ctrl, max_fes=40, seed=1, np_size=10)


# ---------------------------------------------------------------------------
# Feature definitions
# ---------------------------------------------------------------------------

def test_features_success_fraction_is_previous_generation():
    f0 = _features(
        generation=0,
        best_history=[10.0],
        diversity=1.0,
        prev_success_fraction=0.0,
        budget_fraction=0.1,
    )
    assert f0["success_fraction"] == 0.0
    f1 = _features(
        generation=1,
        best_history=[10.0, 9.0],
        diversity=1.0,
        prev_success_fraction=0.375,
        budget_fraction=0.2,
    )
    assert f1["success_fraction"] == 0.375
    assert f1["stagnation_steps"] == 0.0
    f2 = _features(
        generation=2,
        best_history=[10.0, 9.0, 9.0],
        diversity=1.0,
        prev_success_fraction=0.1,
        budget_fraction=0.3,
    )
    assert f2["stagnation_steps"] == 1.0
