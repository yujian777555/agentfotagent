"""Mechanism DSL for Agent-proposed DE improvements (Phase-1A-2).

A mechanism = trigger conditions over public search state + operator/recovery
interventions + parameter policy + scope + fail-closed validation.
No arbitrary code execution.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple


MECH_DSL_VERSION = "aes-mech-dsl-v1"

ALLOWED_FEATURES = (
    "stagnation_steps",
    "success_fraction",
    "population_diversity",
    "improvement_rate",
    "budget_fraction",
)

ALLOWED_OPS = ("rand/1/bin", "current-to-best/1/bin", "rand/2/bin", "best/1/bin")
ALLOWED_ACTIONS = ("set_operator", "set_F", "set_CR", "inject_diversity", "noop")

F_BOUNDS = (0.1, 1.0)
CR_BOUNDS = (0.0, 1.0)


class MechanismValidationError(ValueError):
    pass


def _req(cond: bool, msg: str) -> None:
    if not cond:
        raise MechanismValidationError(msg)


def validate_mechanism(spec: Mapping[str, Any]) -> Dict[str, Any]:
    _req(isinstance(spec, Mapping), "spec must be mapping")
    allowed = {"schema_version", "mechanism_id", "description", "rules", "default"}
    unknown = set(spec) - allowed
    _req(not unknown, f"unknown spec fields: {sorted(unknown)}")
    _req(spec.get("schema_version") == MECH_DSL_VERSION, "bad schema_version")
    _req(isinstance(spec.get("mechanism_id"), str) and spec["mechanism_id"], "mechanism_id required")
    rules = spec.get("rules")
    _req(isinstance(rules, list) and rules, "rules must be a non-empty list")
    for i, r in enumerate(rules):
        _validate_rule(r, f"rules[{i}]")
    default = spec.get("default")
    _req(isinstance(default, Mapping), "default action required")
    _canonical_action(default, "default")
    return {
        "schema_version": MECH_DSL_VERSION,
        "mechanism_id": spec["mechanism_id"],
        "description": str(spec.get("description") or ""),
        "rules": [_canon_rule(r) for r in rules],
        "default": _canonical_action(default, "default"),
    }


def _validate_rule(rule: Any, path: str) -> None:
    _req(isinstance(rule, Mapping), f"{path} must be mapping")
    unknown = set(rule) - {"when", "then"}
    _req(not unknown, f"{path} unknown: {sorted(unknown)}")
    when = rule.get("when")
    _req(isinstance(when, Mapping) and when, f"{path}.when required")
    for feat, cond in when.items():
        _req(feat in ALLOWED_FEATURES, f"{path}.when unknown feature {feat}")
        _req(isinstance(cond, Mapping), f"{path}.when.{feat} mapping")
        _req(set(cond) <= {"op", "value"}, f"{path}.when.{feat} keys")
        _req(cond.get("op") in {"<", "<=", ">", ">=", "=="}, f"{path}.when.{feat}.op")
        v = cond.get("value")
        _req(isinstance(v, (int, float)) and not isinstance(v, bool), f"{path}.when.{feat}.value")
    _canonical_action(rule.get("then"), f"{path}.then")


def _canonical_action(action: Mapping[str, Any], path: str) -> Dict[str, Any]:
    _req(isinstance(action, Mapping), f"{path} must be mapping")
    unknown = set(action) - {"action", "params"}
    _req(not unknown, f"{path} unknown: {sorted(unknown)}")
    name = action.get("action")
    _req(name in ALLOWED_ACTIONS, f"{path}.action invalid {name!r}")
    params = action.get("params") or {}
    _req(isinstance(params, Mapping), f"{path}.params mapping")
    if name == "set_operator":
        _req(set(params) <= {"operator"}, f"{path}.params")
        op = params.get("operator")
        _req(op in ALLOWED_OPS, f"{path}.params.operator {op!r}")
        return {"action": name, "params": {"operator": op}}
    if name == "set_F":
        _req(set(params) <= {"value"}, f"{path}.params")
        v = float(params.get("value"))
        _req(F_BOUNDS[0] <= v <= F_BOUNDS[1], f"{path}.params.value")
        return {"action": name, "params": {"value": v}}
    if name == "set_CR":
        _req(set(params) <= {"value"}, f"{path}.params")
        v = float(params.get("value"))
        _req(CR_BOUNDS[0] <= v <= CR_BOUNDS[1], f"{path}.params.value")
        return {"action": name, "params": {"value": v}}
    if name == "inject_diversity":
        return {"action": name, "params": {}}
    _req(not params, f"{path}.params must be empty for noop")
    return {"action": name, "params": {}}


def _canon_rule(rule: Mapping[str, Any]) -> Dict[str, Any]:
    when = {k: {"op": rule["when"][k]["op"], "value": float(rule["when"][k]["value"])} for k in sorted(rule["when"])}
    return {"when": when, "then": _canonical_action(rule["then"], "then")}


@dataclass
class CompiledMechanism:
    mechanism_id: str
    spec: Dict[str, Any]
    mech_hash: str

    def select(self, state: Mapping[str, Any]) -> Dict[str, Any]:
        for rule in self.spec["rules"]:
            ok = True
            for feat, cond in rule["when"].items():
                v = float(state.get(feat, 0) or 0)
                thr = float(cond["value"])
                op = cond["op"]
                if op == "<" and not v < thr:
                    ok = False
                elif op == "<=" and not v <= thr:
                    ok = False
                elif op == ">" and not v > thr:
                    ok = False
                elif op == ">=" and not v >= thr:
                    ok = False
                elif op == "==" and not v == thr:
                    ok = False
            if ok:
                return dict(rule["then"])
        return dict(self.spec["default"])


def compile_mechanism(spec: Mapping[str, Any]) -> CompiledMechanism:
    canon = validate_mechanism(spec)
    blob = json.dumps(canon, sort_keys=True, separators=(",", ":"))
    h = hashlib.sha256(blob.encode()).hexdigest()
    return CompiledMechanism(mechanism_id=canon["mechanism_id"], spec=canon, mech_hash=h)


def heuristic_stagnation_mechanism() -> Dict[str, Any]:
    """Deterministic baseline: switch to exploration when stagnating."""
    return {
        "schema_version": MECH_DSL_VERSION,
        "mechanism_id": "heuristic_stag_explore",
        "description": "on stagnation switch to rand/2/bin with high F; else classic",
        "rules": [
            {"when": {"stagnation_steps": {"op": ">=", "value": 5.0}},
             "then": {"action": "set_operator", "params": {"operator": "rand/2/bin"}}},
            {"when": {"stagnation_steps": {"op": ">=", "value": 5.0}},
             "then": {"action": "set_F", "params": {"value": 0.9}}},
            {"when": {"success_fraction": {"op": "<=", "value": 0.05}},
             "then": {"action": "set_operator", "params": {"operator": "current-to-best/1/bin"}}},
        ],
        "default": {"action": "set_operator", "params": {"operator": "rand/1/bin"}},
    }
