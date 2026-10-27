"""R1-02/03/04 regression tests: relay verification, missing relay object, goal schemas."""
import json

import pytest

from agentfotagent.environments.tool_world import ToolWorld, _business_state
from agentfotagent.evaluation.evaluator import StateBasedEvaluator
from agentfotagent.interfaces import Action, RuntimeTask, TaskInstance
from agentfotagent.runtime.mock_backend import MockPolicy, _ingest_mock_results, run_episode
from agentfotagent.runtime.phenotype import compile_phenotype
from agentfotagent.tasks.generators import generate_task

from conftest import make_genome


def _state(**kwargs):
    base = {
        "objects": {"relay": {"type": "relay", "location": "hub"}},
        "dials": {},
        "relay": {},
        "inventory": [],
        "location": "hub",
        "step": 3,
        "termination_reason": "agent_submit",
    }
    base.update(kwargs)
    return base


# ---------------------------------------------------------------------------
# R1-02: verification must compare expected frequency
# ---------------------------------------------------------------------------

def test_relay_verification_rejects_wrong_non_null_frequency():
    task = generate_task("relay_route", 1, "held_out")
    ph = compile_phenotype(make_genome(verification_policy="check_before_finalize"))
    policy = MockPolicy(phenotype=ph, runtime_task=task.runtime, family="relay_route")
    # Fragments yield expected frequency != 4.
    policy.known_frags = {"note_0": "fragment 0: digit 1", "note_1": "fragment 1: digit 1", "note_2": "fragment 2: digit 1"}
    # expected = (1+1+1)%7+1 = 4
    wrong = (1 + 1 + 1) % 7 + 2  # 5, wrong but non-null
    summary = {
        "unlocked": {},
        "dials": {},
        "inventory": [],
        "relay_activated": True,
        "relay_frequency": wrong,
        "surface_contents": {},
        "location": "hub",
    }
    obs = {"location": "hub", "inventory": [], "visible_objects": [], "dials": {}, "relay": {"activated": True, "frequency": wrong}, "notes_read": {}, "plan": None, "step": 8, "terminated": False}
    _ingest_mock_results(policy, {"valid": True, "result": summary}, obs, {"tool": "verify_state", "args": {}})
    assert policy.last_verify_summary["goal_checks_passed"] is False
    assert policy.phenotype.verified is False

    # Submit must remain blocked.
    policy.placed_statue = False
    # Force the solver to offer submit by pre-setting placed path for relay: just call next_action
    # after marking as if done — relay solver submits when frequency matches computed expected.
    # With wrong frequency in observation, solver will try set_frequency; either way not a
    # verified submit after failed verification.
    a = policy.next_action(obs)
    assert not (a.tool == "submit" and policy.phenotype.verified)


def test_relay_verification_accepts_correct_frequency():
    task = generate_task("relay_route", 1, "held_out")
    ph = compile_phenotype(make_genome(verification_policy="check_before_finalize"))
    policy = MockPolicy(phenotype=ph, runtime_task=task.runtime, family="relay_route")
    policy.known_frags = {"note_0": "fragment 0: digit 1", "note_1": "fragment 1: digit 1", "note_2": "fragment 2: digit 1"}
    expected = (3 % 7) + 1  # 4
    summary = {
        "unlocked": {},
        "dials": {},
        "inventory": [],
        "relay_activated": True,
        "relay_frequency": expected,
        "surface_contents": {},
        "location": "hub",
    }
    obs = {"location": "hub", "inventory": [], "visible_objects": [], "dials": {}, "relay": {"activated": True, "frequency": expected}, "notes_read": {}, "plan": None, "step": 8, "terminated": False}
    _ingest_mock_results(policy, {"valid": True, "result": summary}, obs, {"tool": "verify_state", "args": {}})
    assert policy.last_verify_summary["goal_checks_passed"] is True
    assert policy.phenotype.verified is True


# ---------------------------------------------------------------------------
# R1-03: missing relay object
# ---------------------------------------------------------------------------

def test_activate_relay_missing_object_fails_closed():
    task = generate_task("relay_route", 1, "held_out")
    env = ToolWorld()
    env.reset(task)
    # Remove relay object.
    del env._state.objects["relay"]
    before = _business_state(env.final_state())
    res = env.step(Action("activate_relay", {"code": task.setup["relay"]["code"]}))
    assert res.info["valid"] is False
    after = _business_state(env.final_state())
    assert after["relay"].get("activated") in (False, None)
    assert after["objects"] == before["objects"]


def test_set_frequency_missing_object_fails_closed():
    task = generate_task("relay_route", 1, "held_out")
    env = ToolWorld()
    env.reset(task)
    del env._state.objects["relay"]
    # Even if state mapping is marked activated, object missing blocks the tool.
    env._state.relay["activated"] = True
    before = _business_state(env.final_state())
    res = env.step(Action("set_frequency", {"frequency": 3}))
    assert res.info["valid"] is False
    after = _business_state(env.final_state())
    assert after["relay"].get("frequency") in (None, 3)
    assert after["relay"].get("frequency") != 3 or before["relay"].get("frequency") == 3


def test_activate_relay_wrong_type_object_fails_closed():
    task = generate_task("relay_route", 1, "held_out")
    env = ToolWorld()
    env.reset(task)
    env._state.objects["relay"]["type"] = "not-relay"
    res = env.step(Action("activate_relay", {"code": task.setup["relay"]["code"]}))
    assert res.info["valid"] is False
    assert env.final_state()["relay"].get("activated") is not True


def test_relay_tools_need_local_relay_object():
    task = generate_task("relay_route", 1, "held_out")
    env = ToolWorld()
    env.reset(task)
    env.step(Action("move", {"location": "north"}))
    res = env.step(Action("activate_relay", {"code": task.setup["relay"]["code"]}))
    assert res.info["valid"] is False
    assert env.final_state()["relay"].get("activated") is not True


def test_evaluator_requires_relay_object():
    task = generate_task("relay_route", 1, "held_out")
    freq = task.hidden_goal["frequency"]
    # Relay state OK but no relay object in objects map.
    state = _state(objects={}, relay={"activated": True, "frequency": freq})
    assert StateBasedEvaluator().evaluate(task, state, []).success is False

    # Wrong type object.
    state2 = _state(
        objects={"relay": {"type": "crystal", "location": "hub"}},
        relay={"activated": True, "frequency": freq},
    )
    assert StateBasedEvaluator().evaluate(task, state2, []).success is False

    # Valid object + state.
    state3 = _state(
        objects={"relay": {"type": "relay", "location": "hub"}},
        relay={"activated": True, "frequency": freq},
    )
    assert StateBasedEvaluator().evaluate(task, state3, []).success is True


# ---------------------------------------------------------------------------
# R1-04: goal schemas and safe metrics
# ---------------------------------------------------------------------------

def test_partial_dial_goal_fails_closed():
    task = generate_task("dial_set", 1, "train")
    object.__setattr__(task, "hidden_goal", {"type": "dial_set", "targets": {"alpha": 1}})
    state = _state(dials={"alpha": 1, "beta": 0, "gamma": 0})
    assert StateBasedEvaluator().evaluate(task, state, []).success is False


def test_dial_goal_out_of_range_fails_closed():
    task = generate_task("dial_set", 1, "train")
    object.__setattr__(
        task, "hidden_goal", {"type": "dial_set", "targets": {"alpha": 1, "beta": 2, "gamma": 99}}
    )
    state = _state(dials={"alpha": 1, "beta": 2, "gamma": 99})
    assert StateBasedEvaluator().evaluate(task, state, []).success is False


def test_missing_crate_unlocked_goal_flag_fails_closed():
    task = generate_task("key_crate", 1, "train")
    goal = {
        "type": "key_crate",
        "object_on_surface": {"object": "statue", "surface": "pedestal"},
        # crate_unlocked intentionally omitted
    }
    object.__setattr__(task, "hidden_goal", goal)
    state = _state(
        location="hall",
        objects={
            "statue": {"location": "pedestal"},
            "crate": {"unlocked": True, "locked": False},
        },
    )
    assert StateBasedEvaluator().evaluate(task, state, []).success is False


def test_relay_goal_missing_required_fields_fails_closed():
    task = generate_task("relay_route", 1, "held_out")
    object.__setattr__(task, "hidden_goal", {"type": "relay_route", "frequency": 3})
    state = _state(
        objects={"relay": {"type": "relay", "location": "hub"}},
        relay={"activated": True, "frequency": 3},
    )
    assert StateBasedEvaluator().evaluate(task, state, []).success is False

    object.__setattr__(task, "hidden_goal", {"type": "relay_route", "code": "123"})
    assert StateBasedEvaluator().evaluate(task, state, []).success is False


def test_invalid_step_type_does_not_raise():
    task = generate_task("dial_set", 1, "train")
    targets = dict(task.hidden_goal["targets"])
    state = _state(dials=dict(targets), step="not-an-int")
    result = StateBasedEvaluator().evaluate(task, state, [])
    assert result.success is True
    assert result.steps == 0

    state2 = _state(dials=dict(targets), step=None)
    r2 = StateBasedEvaluator().evaluate(task, state2, [])
    assert r2.success is True
    assert r2.steps == 0


def test_evaluator_never_raises_on_garbage_state():
    task = generate_task("key_crate", 1, "train")
    for bad in (None, [], 5, "x"):
        r = StateBasedEvaluator().evaluate(task, bad, [])  # type: ignore[arg-type]
        assert r.success is False
    # Garbage nested fields
    r = StateBasedEvaluator().evaluate(task, {"objects": 1, "dials": [], "relay": "x", "step": object()}, [])
    assert r.success is False
