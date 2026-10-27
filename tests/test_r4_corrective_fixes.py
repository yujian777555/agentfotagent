"""R4 regression tests: strict success type, score schema, key_crate locations, probe harness."""
from __future__ import annotations

import json

import pytest

from agentfotagent.evaluation.evaluator import StateBasedEvaluator
from agentfotagent.evaluation.provenance import (
    ReconstructionError,
    compare_score_fields,
    reconstruct_from_artifacts,
    validate_score_record_schema,
)
from agentfotagent.evolution.harness import BaselineHarness
from agentfotagent.evolution.random_search import RandomSearch
from agentfotagent.genome.schema import GenomeSpace
from agentfotagent.interfaces import EpisodeResult
from agentfotagent.runtime.mock_backend import run_episode
from agentfotagent.tasks.generators import generate_task

import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "probe_mod", Path(__file__).resolve().parent / "probe_r2_counterexamples.py"
)
probe_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(probe_mod)


def _make_artifact(budget=1):
    tasks = [generate_task("dial_set", 1, "train")]
    task_map = {t.task_id: t for t in tasks}
    space = GenomeSpace()
    harness = BaselineHarness(tasks=tasks, space=space, config={"protocol": "r4"})
    art = json.loads(json.dumps(harness.run_and_collect(RandomSearch(space, seed=1), budget), default=str))
    return task_map, art


def _valid_result() -> EpisodeResult:
    return EpisodeResult(
        task_id="t1",
        genome_hash="g1",
        success=True,
        steps=2,
        invalid_actions=0,
        repeated_states=0,
        termination_reason="agent_submit",
        final_state_hash="h1",
    )


# ---------------------------------------------------------------------------
# R4-01: success must be real bool
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("bad", [0, 1, "true", "false", None, [], {}, 2.5])
def test_non_bool_success_rejected(bad):
    rec = {
        "task_id": "t1",
        "genome_hash": "g1",
        "success": bad,
        "steps": 2,
        "invalid_actions": 0,
        "repeated_states": 0,
        "termination_reason": "agent_submit",
        "final_state_hash": "h1",
    }
    with pytest.raises(ReconstructionError):
        validate_score_record_schema(rec)


def test_bool_success_accepted():
    for flag in (True, False):
        rec = {
            "task_id": "t1",
            "genome_hash": "g1",
            "success": flag,
            "steps": 2,
            "invalid_actions": 0,
            "repeated_states": 0,
            "termination_reason": "agent_submit",
            "final_state_hash": "h1",
        }
        validate_score_record_schema(rec)
        result = _valid_result()
        result = EpisodeResult(
            task_id="t1",
            genome_hash="g1",
            success=flag,
            steps=2,
            invalid_actions=0,
            repeated_states=0,
            termination_reason="agent_submit",
            final_state_hash="h1",
        )
        compare_score_fields(rec, result)


def test_integer_success_in_artifact_rejected():
    task_map, art = _make_artifact()
    art["manifest"]["scores"][0]["success"] = 1
    with pytest.raises(ReconstructionError):
        reconstruct_from_artifacts(art, task_map, StateBasedEvaluator())


# ---------------------------------------------------------------------------
# R4-02: closed score schema
# ---------------------------------------------------------------------------

def test_unknown_score_field_rejected():
    rec = {
        "task_id": "t1",
        "genome_hash": "g1",
        "success": True,
        "steps": 2,
        "invalid_actions": 0,
        "repeated_states": 0,
        "termination_reason": "agent_submit",
        "final_state_hash": "h1",
        "unvalidated_metric": 999999,
    }
    with pytest.raises(ReconstructionError, match="unknown"):
        validate_score_record_schema(rec)


def test_unknown_field_in_artifact_rejected():
    task_map, art = _make_artifact()
    art["manifest"]["scores"][0]["unvalidated_metric"] = 999999
    with pytest.raises(ReconstructionError):
        reconstruct_from_artifacts(art, task_map, StateBasedEvaluator())


def test_missing_identity_field_rejected():
    rec = {
        "task_id": "t1",
        "success": True,
        "steps": 2,
        "invalid_actions": 0,
        "repeated_states": 0,
        "termination_reason": "agent_submit",
        "final_state_hash": "h1",
    }
    with pytest.raises(ReconstructionError, match="missing"):
        validate_score_record_schema(rec)


def test_wrong_identity_type_rejected():
    rec = {
        "task_id": "",
        "genome_hash": "g1",
        "success": True,
        "steps": 2,
        "invalid_actions": 0,
        "repeated_states": 0,
        "termination_reason": "agent_submit",
        "final_state_hash": "h1",
    }
    with pytest.raises(ReconstructionError):
        validate_score_record_schema(rec)


def test_valid_artifact_still_reconstructs():
    task_map, art = _make_artifact()
    result = reconstruct_from_artifacts(art, task_map, StateBasedEvaluator())
    assert result["mismatches"] == []
    assert result["trace_count"] == result["score_count"]


# ---------------------------------------------------------------------------
# R4-03: key_crate locations from task setup
# ---------------------------------------------------------------------------

def _key_crate_good_state(task):
    setup_objs = task.setup["objects"]
    return {
        "objects": {
            "statue": {"type": "artifact", "location": "pedestal"},
            "crate": {
                "type": "crate",
                "unlocked": True,
                "location": setup_objs["crate"]["location"],
            },
            "pedestal": {
                "type": "surface",
                "location": setup_objs["pedestal"]["location"],
            },
        },
        "dials": {},
        "relay": {},
        "inventory": [],
        "location": setup_objs["pedestal"]["location"],
        "step": 5,
        "termination_reason": "agent_submit",
    }


def test_key_crate_missing_crate_location_fails():
    task = generate_task("key_crate", 1, "train")
    state = _key_crate_good_state(task)
    del state["objects"]["crate"]["location"]
    assert StateBasedEvaluator().evaluate(task, state, []).success is False


def test_key_crate_missing_surface_location_fails():
    task = generate_task("key_crate", 1, "train")
    state = _key_crate_good_state(task)
    del state["objects"]["pedestal"]["location"]
    assert StateBasedEvaluator().evaluate(task, state, []).success is False


def test_key_crate_wrong_type_location_fails():
    task = generate_task("key_crate", 1, "train")
    state = _key_crate_good_state(task)
    state["objects"]["crate"]["location"] = 123
    assert StateBasedEvaluator().evaluate(task, state, []).success is False


def test_key_crate_unknown_location_fails():
    task = generate_task("key_crate", 1, "train")
    state = _key_crate_good_state(task)
    state["objects"]["crate"]["location"] = "not-a-room"
    assert StateBasedEvaluator().evaluate(task, state, []).success is False


def test_key_crate_location_inconsistent_with_setup_fails():
    task = generate_task("key_crate", 1, "train")
    state = _key_crate_good_state(task)
    expected = task.setup["objects"]["crate"]["location"]
    other = "storage" if expected != "storage" else "corridor"
    state["objects"]["crate"]["location"] = other
    assert StateBasedEvaluator().evaluate(task, state, []).success is False


def test_key_crate_statue_not_on_surface_fails():
    task = generate_task("key_crate", 1, "train")
    state = _key_crate_good_state(task)
    state["objects"]["statue"]["location"] = "vault"
    assert StateBasedEvaluator().evaluate(task, state, []).success is False


def test_key_crate_valid_setup_state_succeeds():
    task = generate_task("key_crate", 1, "train")
    assert StateBasedEvaluator().evaluate(task, _key_crate_good_state(task), []).success is True


def test_key_crate_real_episode_succeeds():
    task = generate_task("key_crate", 2, "train")
    ok, tr, payload = run_episode(task, {"planning_mode": "direct"}, seed=2)
    assert ok is True
    assert StateBasedEvaluator().evaluate(task, payload["final_state"], tr.steps).success is True


# ---------------------------------------------------------------------------
# R4-04: probe harness detects vulnerable acceptance
# ---------------------------------------------------------------------------

def test_probe_all_true_on_current_code():
    for name, fn in probe_mod.ALL_PROBES:
        passed, detail = fn()
        assert passed, f"{name} unexpectedly failed: {detail}"


def test_probe_detects_vulnerable_acceptance_stub():
    """A stub that accepts malware must be reported FAIL, not PASS."""

    def vulnerable_relay_probe():
        return False, "malformed relay goal ACCEPTED"

    failures = probe_mod.run_probes([("vuln", vulnerable_relay_probe)])
    assert failures == 1


def test_probe_detects_unexpected_exception_as_fail():
    def boom():
        raise RuntimeError("totally unexpected")

    failures = probe_mod.run_probes([("boom", boom)])
    assert failures == 1


def test_probe_success_type_and_schema_helpers():
    assert probe_mod.probe_r4_01_success_type()[0] is True
    assert probe_mod.probe_r4_02_unknown_field()[0] is True
    assert probe_mod.probe_r4_03_locations()[0] is True
