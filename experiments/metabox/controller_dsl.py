"""Typed controller DSL v2 for MetaBox optimization runs.

P0-R1-01: actions are scalar (``set_F`` / ``set_CR``) — range-sounding names were
removed because official DE consumes scalars. ``restart`` / ``set_mutation_strategy``
are valid in the DSL for the controlled optimizer, but the official DE runner
rejects them at runtime (P0-R1-03).
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Dict, Mapping


DSL_VERSION = "aes-controller-dsl-v2"

ALLOWED_STATE_FEATURES = frozenset(
    {
        "improvement_rate",
        "stagnation_steps",
        "population_diversity",
        "success_fraction",
        "budget_fraction",
        "generation",
    }
)

ALLOWED_ACTIONS = frozenset(
    {
        "set_F",
        "set_CR",
        "set_mutation_strategy",
        "restart",
        "noop",
    }
)

ALLOWED_MUTATION_STRATEGIES = frozenset(
    {"rand/1/bin", "best/1/bin", "current-to-best/1/bin", "rand/2/bin"}
)

F_BOUNDS = (0.1, 1.0)
CR_BOUNDS = (0.0, 1.0)
RESTART_MAX_FRACTION = 0.25


class ControllerValidationError(ValueError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise ControllerValidationError(msg)


def validate_controller_spec(spec: Mapping[str, Any]) -> Dict[str, Any]:
    if not isinstance(spec, Mapping):
        raise ControllerValidationError("spec must be a mapping")
    allowed_keys = {"schema_version", "controller_id", "initial_action", "rules"}
    unknown = set(spec) - allowed_keys
    _require(not unknown, f"unknown spec fields: {sorted(unknown)}")
    _require(spec.get("schema_version") == DSL_VERSION, f"schema_version must be {DSL_VERSION}")
    _require(isinstance(spec.get("controller_id"), str) and spec["controller_id"], "controller_id required")

    initial = spec.get("initial_action")
    _require(isinstance(initial, Mapping), "initial_action required")
    _canonicalize_action(initial, path="initial_action")

    rules = spec.get("rules")
    _require(isinstance(rules, list), "rules must be a list")
    for i, rule in enumerate(rules):
        _validate_rule(rule, path=f"rules[{i}]")

    return {
        "schema_version": DSL_VERSION,
        "controller_id": spec["controller_id"],
        "initial_action": _canonicalize_action(initial, path="initial_action"),
        "rules": [_canonicalize_rule(r) for r in rules],
    }


def _validate_rule(rule: Any, path: str) -> None:
    _require(isinstance(rule, Mapping), f"{path} must be a mapping")
    unknown = set(rule) - {"when", "then"}
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
    unknown = set(action) - {"action", "params"}
    _require(not unknown, f"{path} unknown fields: {sorted(unknown)}")
    name = action.get("action")
    _require(name in ALLOWED_ACTIONS, f"{path}.action invalid: {name!r}")
    params = action.get("params") or {}
    _require(isinstance(params, Mapping), f"{path}.params must be mapping")

    if name in {"set_F", "set_CR"}:
        unknown_p = set(params) - {"value"}
        _require(not unknown_p, f"{path}.params unknown: {sorted(unknown_p)}")
        val = params.get("value")
        _require(isinstance(val, (int, float)) and not isinstance(val, bool), f"{path}.params.value must be number")
        bounds = F_BOUNDS if name == "set_F" else CR_BOUNDS
        v = float(val)
        _require(bounds[0] <= v <= bounds[1], f"{path}.params.value out of range {bounds}")
        return {"action": name, "params": {"value": v}}
    if name == "set_mutation_strategy":
        unknown_p = set(params) - {"strategy"}
        _require(not unknown_p, f"{path}.params unknown: {sorted(unknown_p)}")
        strat = params.get("strategy")
        _require(strat in ALLOWED_MUTATION_STRATEGIES, f"{path}.params.strategy invalid: {strat!r}")
        return {"action": name, "params": {"strategy": strat}}
    if name == "restart":
        unknown_p = set(params) - {"max_fraction"}
        _require(not unknown_p, f"{path}.params unknown: {sorted(unknown_p)}")
        frac = params.get("max_fraction", RESTART_MAX_FRACTION)
        _require(isinstance(frac, (int, float)) and not isinstance(frac, bool), f"{path}.params.max_fraction must be number")
        _require(0.0 < float(frac) <= RESTART_MAX_FRACTION, f"{path}.params.max_fraction out of range")
        return {"action": name, "params": {"max_fraction": float(frac)}}
    _require(not params, f"{path}.params must be empty for {name}")
    return {"action": name, "params": {}}


def _canonicalize_rule(rule: Mapping[str, Any]) -> Dict[str, Any]:
    when = {k: {"op": rule["when"][k]["op"], "value": float(rule["when"][k]["value"])} for k in sorted(rule["when"])}
    return {"when": when, "then": _canonicalize_action(rule["then"], path="then")}


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
    return CompiledController(controller_id=canonical["controller_id"], spec=canonical, controller_hash=h)


def fixed_controller_a() -> Dict[str, Any]:
    """Classic DE-like controller: moderate F, high CR."""
    return {
        "schema_version": DSL_VERSION,
        "controller_id": "fixed_classic_de",
        "initial_action": {"action": "set_F", "params": {"value": 0.5}},
        "rules": [
            {
                "when": {"stagnation_steps": {"op": ">=", "value": 10.0}},
                "then": {"action": "set_F", "params": {"value": 0.8}},
            },
            {
                "when": {"budget_fraction": {"op": ">=", "value": 0.8}},
                "then": {"action": "set_CR", "params": {"value": 0.2}},
            },
        ],
    }


def fixed_controller_b() -> Dict[str, Any]:
    """Exploration-leaning controller: high F from the start."""
    return {
        "schema_version": DSL_VERSION,
        "controller_id": "fixed_explore_de",
        "initial_action": {"action": "set_F", "params": {"value": 0.9}},
        "rules": [
            {
                "when": {"stagnation_steps": {"op": ">=", "value": 15.0}},
                "then": {"action": "set_CR", "params": {"value": 0.9}},
            },
            {
                "when": {
                    "improvement_rate": {"op": "<", "value": 0.001},
                    "budget_fraction": {"op": ">=", "value": 0.1},
                },
                "then": {"action": "set_F", "params": {"value": 1.0}},
            },
        ],
    }
