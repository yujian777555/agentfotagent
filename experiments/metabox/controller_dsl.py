"""Typed controller DSL for MetaBox optimization runs.

No arbitrary Python execution. Controllers are JSON-serializable objects with a
closed schema, deterministic compilation and bounded parameters.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple


DSL_VERSION = "aes-controller-dsl-v1"

ALLOWED_STATE_FEATURES = frozenset(
    {
        "improvement_rate",
        "stagnation_steps",
        "population_diversity",
        "success_fraction",
        "budget_fraction",
    }
)

ALLOWED_ACTIONS = frozenset(
    {
        "set_mutation_strategy",
        "set_F_range",
        "set_CR_range",
        "restart",
        "noop",
    }
)

ALLOWED_MUTATION_STRATEGIES = frozenset(
    {"rand/1/bin", "best/1/bin", "current-to-best/1/bin", "rand/2/bin"}
)

# Bounded parameter ranges (closed).
F_RANGE_BOUNDS = (0.1, 1.0)
CR_RANGE_BOUNDS = (0.0, 1.0)
RESTART_MAX_FRACTION = 0.25


class ControllerValidationError(ValueError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise ControllerValidationError(msg)


def validate_controller_spec(spec: Mapping[str, Any]) -> Dict[str, Any]:
    """Validate and canonicalize a controller spec. Fail closed on any issue."""
    if not isinstance(spec, Mapping):
        raise ControllerValidationError("spec must be a mapping")
    allowed_keys = {"schema_version", "controller_id", "initial_action", "rules"}
    unknown = set(spec) - allowed_keys
    _require(not unknown, f"unknown spec fields: {sorted(unknown)}")
    _require(spec.get("schema_version") == DSL_VERSION, "schema_version mismatch")
    _require(isinstance(spec.get("controller_id"), str) and spec["controller_id"], "controller_id required")

    initial = spec.get("initial_action")
    _require(isinstance(initial, Mapping), "initial_action required")
    _canonicalize_action(initial, path="initial_action")

    rules = spec.get("rules")
    _require(isinstance(rules, list), "rules must be a list")
    for i, rule in enumerate(rules):
        _validate_rule(rule, path=f"rules[{i}]")

    # Deterministic canonical form.
    canonical = {
        "schema_version": DSL_VERSION,
        "controller_id": spec["controller_id"],
        "initial_action": _canonicalize_action(initial, path="initial_action"),
        "rules": [_canonicalize_rule(r) for r in rules],
    }
    return canonical


def _validate_rule(rule: Any, path: str) -> None:
    _require(isinstance(rule, Mapping), f"{path} must be a mapping")
    allowed = {"when", "then"}
    unknown = set(rule) - allowed
    _require(not unknown, f"{path} unknown fields: {sorted(unknown)}")
    when = rule.get("when")
    _require(isinstance(when, Mapping), f"{path}.when required")
    unknown_when = set(when) - ALLOWED_STATE_FEATURES
    _require(not unknown_when, f"{path}.when unknown features: {sorted(unknown_when)}")
    for feat, cond in when.items():
        _require(isinstance(cond, Mapping), f"{path}.when.{feat} must be mapping")
        unknown_cond = set(cond) - {"op", "value"}
        _require(not unknown_cond, f"{path}.when.{feat} unknown: {sorted(unknown_cond)}")
        _require(cond.get("op") in {"<", "<=", ">", ">=", "=="}, f"{path}.when.{feat}.op invalid")
        val = cond.get("value")
        _require(isinstance(val, (int, float)) and not isinstance(val, bool), f"{path}.when.{feat}.value must be number")
    then = rule.get("then")
    _require(isinstance(then, Mapping), f"{path}.then required")
    _canonicalize_action(then, path=f"{path}.then")


def _canonicalize_action(action: Mapping[str, Any], path: str) -> Dict[str, Any]:
    _require(isinstance(action, Mapping), f"{path} must be mapping")
    allowed = {"action", "params"}
    unknown = set(action) - allowed
    _require(not unknown, f"{path} unknown fields: {sorted(unknown)}")
    name = action.get("action")
    _require(name in ALLOWED_ACTIONS, f"{path}.action invalid: {name!r}")
    params = action.get("params") or {}
    _require(isinstance(params, Mapping), f"{path}.params must be mapping")

    if name == "set_mutation_strategy":
        unknown_p = set(params) - {"strategy"}
        _require(not unknown_p, f"{path}.params unknown: {sorted(unknown_p)}")
        strat = params.get("strategy")
        _require(strat in ALLOWED_MUTATION_STRATEGIES, f"{path}.params.strategy invalid: {strat!r}")
        out_params = {"strategy": strat}
    elif name == "set_F_range":
        unknown_p = set(params) - {"low", "high"}
        _require(not unknown_p, f"{path}.params unknown: {sorted(unknown_p)}")
        low, high = params.get("low"), params.get("high")
        for v in (low, high):
            _require(isinstance(v, (int, float)) and not isinstance(v, bool), f"{path}.params values must be numbers")
        lo = float(low)
        hi = float(high)
        _require(lo <= hi, f"{path}.params low>high")
        _require(F_RANGE_BOUNDS[0] <= lo <= F_RANGE_BOUNDS[1], f"{path}.params.low out of range")
        _require(F_RANGE_BOUNDS[0] <= hi <= F_RANGE_BOUNDS[1], f"{path}.params.high out of range")
        out_params = {"low": lo, "high": hi}
    elif name == "set_CR_range":
        unknown_p = set(params) - {"low", "high"}
        _require(not unknown_p, f"{path}.params unknown: {sorted(unknown_p)}")
        low, high = params.get("low"), params.get("high")
        for v in (low, high):
            _require(isinstance(v, (int, float)) and not isinstance(v, bool), f"{path}.params values must be numbers")
        lo = float(low)
        hi = float(high)
        _require(lo <= hi, f"{path}.params low>high")
        _require(CR_RANGE_BOUNDS[0] <= lo <= CR_RANGE_BOUNDS[1], f"{path}.params.low out of range")
        _require(CR_RANGE_BOUNDS[0] <= hi <= CR_RANGE_BOUNDS[1], f"{path}.params.high out of range")
        out_params = {"low": lo, "high": hi}
    elif name == "restart":
        unknown_p = set(params) - {"max_fraction"}
        _require(not unknown_p, f"{path}.params unknown: {sorted(unknown_p)}")
        frac = params.get("max_fraction", RESTART_MAX_FRACTION)
        _require(isinstance(frac, (int, float)) and not isinstance(frac, bool), f"{path}.params.max_fraction must be number")
        _require(0.0 < float(frac) <= RESTART_MAX_FRACTION, f"{path}.params.max_fraction out of range")
        out_params = {"max_fraction": float(frac)}
    else:
        _require(not params, f"{path}.params must be empty for {name}")
        out_params = {}
    return {"action": name, "params": out_params}


def _canonicalize_rule(rule: Mapping[str, Any]) -> Dict[str, Any]:
    when = {k: {"op": rule["when"][k]["op"], "value": float(rule["when"][k]["value"])} for k in sorted(rule["when"])}
    then = _canonicalize_action(rule["then"], path="then")
    return {"when": when, "then": then}


@dataclass
class CompiledController:
    controller_id: str
    spec: Dict[str, Any]
    controller_hash: str

    def select_action(self, state: Mapping[str, Any]) -> Dict[str, Any]:
        for rule in self.spec["rules"]:
            when = rule["when"]
            if all(_cond_ok(state, feat, cond) for feat, cond in when.items()):
                return dict(rule["then"])
        return dict(self.spec["initial_action"])


def _cond_ok(state: Mapping[str, Any], feat: str, cond: Mapping[str, Any]) -> bool:
    if feat not in state:
        raise ControllerValidationError(f"unknown state feature: {feat}")
    val = state[feat]
    if not isinstance(val, (int, float)) or isinstance(val, bool):
        raise ControllerValidationError(f"state feature {feat} must be numeric")
    op = cond["op"]
    thr = float(cond["value"])
    v = float(val)
    if op == "<":
        return v < thr
    if op == "<=":
        return v <= thr
    if op == ">":
        return v > thr
    if op == ">=":
        return v >= thr
    return v == thr


def compile_controller(spec: Mapping[str, Any]) -> CompiledController:
    canonical = validate_controller_spec(spec)
    blob = json.dumps(canonical, sort_keys=True, separators=(",", ":"))
    h = hashlib.sha256(blob.encode("utf-8")).hexdigest()
    return CompiledController(
        controller_id=canonical["controller_id"],
        spec=canonical,
        controller_hash=h,
    )


def fixed_controller_a() -> Dict[str, Any]:
    """Legal fixed controller: classic DE defaults (moderate F/CR)."""
    return {
        "schema_version": DSL_VERSION,
        "controller_id": "fixed_classic_de",
        "initial_action": {"action": "set_F_range", "params": {"low": 0.4, "high": 0.6}},
        "rules": [
            {
                "when": {"stagnation_steps": {"op": ">=", "value": 25.0}},
                "then": {"action": "set_mutation_strategy", "params": {"strategy": "rand/1/bin"}},
            },
            {
                "when": {"budget_fraction": {"op": ">=", "value": 0.75}},
                "then": {"action": "set_CR_range", "params": {"low": 0.1, "high": 0.5}},
            },
        ],
    }


def fixed_controller_b() -> Dict[str, Any]:
    """Legal fixed controller: exploration-leaning DE (high F, high CR)."""
    return {
        "schema_version": DSL_VERSION,
        "controller_id": "fixed_explore_de",
        "initial_action": {"action": "set_F_range", "params": {"low": 0.8, "high": 1.0}},
        "rules": [
            {
                "when": {"stagnation_steps": {"op": ">=", "value": 30.0}},
                "then": {"action": "restart", "params": {"max_fraction": 0.1}},
            },
            {
                "when": {"population_diversity": {"op": "<", "value": 0.05}},
                "then": {"action": "set_CR_range", "params": {"low": 0.7, "high": 1.0}},
            },
        ],
    }
