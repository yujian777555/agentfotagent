"""Controller DSL schema tests (no MetaBox required)."""
from __future__ import annotations

import pytest

from experiments.metabox.controller_dsl import (
    ControllerValidationError,
    compile_controller,
    fixed_controller_a,
    fixed_controller_b,
    validate_controller_spec,
)


def test_fixed_controllers_are_legal():
    for spec in (fixed_controller_a(), fixed_controller_b()):
        c = compile_controller(spec)
        assert c.controller_hash
        assert c.controller_id == spec["controller_id"]


def test_unknown_field_rejected():
    spec = fixed_controller_a()
    spec["extra"] = 1
    with pytest.raises(ControllerValidationError, match="unknown"):
        validate_controller_spec(spec)


def test_unknown_action_rejected():
    spec = fixed_controller_a()
    spec["initial_action"] = {"action": "exec_python", "params": {}}
    with pytest.raises(ControllerValidationError):
        validate_controller_spec(spec)


def test_unknown_state_feature_rejected():
    spec = fixed_controller_a()
    spec["rules"] = [
        {"when": {"hidden_optimum": {"op": "<", "value": 1.0}}, "then": {"action": "noop", "params": {}}}
    ]
    with pytest.raises(ControllerValidationError, match="unknown"):
        validate_controller_spec(spec)


def test_out_of_range_F_rejected():
    spec = fixed_controller_a()
    spec["initial_action"] = {"action": "set_F_range", "params": {"low": 5.0, "high": 9.0}}
    with pytest.raises(ControllerValidationError):
        validate_controller_spec(spec)


def test_bool_param_rejected():
    spec = fixed_controller_a()
    spec["initial_action"] = {"action": "set_F_range", "params": {"low": True, "high": 0.5}}
    with pytest.raises(ControllerValidationError):
        validate_controller_spec(spec)


def test_restart_fraction_capped():
    spec = fixed_controller_a()
    spec["initial_action"] = {"action": "restart", "params": {"max_fraction": 0.9}}
    with pytest.raises(ControllerValidationError):
        validate_controller_spec(spec)


def test_rule_matches_state():
    c = compile_controller(fixed_controller_a())
    action0 = c.select_action(
        {
            "improvement_rate": 0.0,
            "stagnation_steps": 0.0,
            "population_diversity": 1.0,
            "success_fraction": 0.0,
            "budget_fraction": 0.0,
        }
    )
    assert action0["action"] == "set_F_range"
    action1 = c.select_action(
        {
            "improvement_rate": 0.0,
            "stagnation_steps": 40.0,
            "population_diversity": 1.0,
            "success_fraction": 0.0,
            "budget_fraction": 0.1,
        }
    )
    assert action1["action"] == "set_mutation_strategy"


def test_missing_state_feature_raises():
    c = compile_controller(fixed_controller_a())
    with pytest.raises(ControllerValidationError):
        c.select_action({"improvement_rate": 0.0})
