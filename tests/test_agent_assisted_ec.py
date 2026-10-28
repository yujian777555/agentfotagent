"""Mechanism DSL and multi-operator DE tests (Phase-1A-2)."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from experiments.metabox.agent_assisted_ec.mechanism_dsl import (
    MechanismValidationError,
    compile_mechanism,
    heuristic_stagnation_mechanism,
    validate_mechanism,
)
from experiments.metabox.agent_assisted_ec.multi_de import run_multi_de


class Quad:
    dim = 5
    lb = -50.0
    ub = 50.0
    optimum = 0.0

    def reset(self):
        pass

    def eval(self, x):
        return float(np.dot(np.asarray(x).reshape(-1), np.asarray(x).reshape(-1)))


def test_heuristic_mechanism_valid():
    spec = heuristic_stagnation_mechanism()
    m = compile_mechanism(spec)
    assert m.mech_hash
    a = m.select({"stagnation_steps": 6, "success_fraction": 0.3, "population_diversity": 1,
                  "improvement_rate": 0, "budget_fraction": 0.2})
    # first matching rule (stagnation>=5) fires set_operator rand/2
    assert a["action"] == "set_operator"


def test_default_when_no_rule_matches():
    spec = heuristic_stagnation_mechanism()
    m = compile_mechanism(spec)
    a = m.select({"stagnation_steps": 0, "success_fraction": 0.5, "population_diversity": 1,
                  "improvement_rate": 0.1, "budget_fraction": 0.1})
    assert a["action"] == "set_operator"
    assert a["params"]["operator"] == "rand/1/bin"


def test_illegal_action_rejected():
    spec = heuristic_stagnation_mechanism()
    spec = dict(spec, default={"action": "exec", "params": {}})
    with pytest.raises(MechanismValidationError):
        validate_mechanism(spec)


def test_illegal_operator_rejected():
    spec = heuristic_stagnation_mechanism()
    spec["rules"] = [{"when": {"stagnation_steps": {"op": ">=", "value": 1}},
                      "then": {"action": "set_operator", "params": {"operator": "pso"}}}]
    with pytest.raises(MechanismValidationError):
        validate_mechanism(spec)


def test_unknown_feature_rejected():
    spec = heuristic_stagnation_mechanism()
    spec["rules"] = [{"when": {"optimum": {"op": "<", "value": 1}},
                      "then": {"action": "noop", "params": {}}}]
    with pytest.raises(MechanismValidationError):
        validate_mechanism(spec)


def test_multi_de_all_operators_run():
    for op in ("rand/1/bin", "current-to-best/1/bin", "rand/2/bin", "best/1/bin"):
        spec = {
            "schema_version": "aes-mech-dsl-v1",
            "mechanism_id": f"op_{op}",
            "description": "",
            "rules": [{"when": {"stagnation_steps": {"op": ">=", "value": 999}},
                       "then": {"action": "noop", "params": {}}}],
            "default": {"action": "set_operator", "params": {"operator": op}},
        }
        res = run_multi_de(Quad(), compile_mechanism(spec), max_fes=80, seed=1, np_size=10)
        assert res.fes == res.independent_fes == 80
        assert res.action_events[0]["operator"] == op


def test_inject_diversity_and_fe_exact():
    spec = {
        "schema_version": "aes-mech-dsl-v1",
        "mechanism_id": "div",
        "description": "",
        "rules": [{"when": {"stagnation_steps": {"op": ">=", "value": 0.0}},
                   "then": {"action": "inject_diversity", "params": {}}}],
        "default": {"action": "noop", "params": {}},
    }
    res = run_multi_de(Quad(), compile_mechanism(spec), max_fes=60, seed=2, np_size=10)
    assert res.fes == 60
    assert any(e["effect"].get("resampled") for e in res.action_events)
