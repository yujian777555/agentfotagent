"""F5 regression: evaluator must fail closed on malformed goal/state structures."""
import pytest

from agentfotagent.evaluation.evaluator import StateBasedEvaluator
from agentfotagent.tasks.generators import generate_task

from conftest import make_genome


def _state(**kwargs):
    base = {
        "objects": {},
        "dials": {},
        "relay": {},
        "inventory": [],
        "location": "hall",
        "step": 3,
        "termination_reason": "agent_submit",
    }
    base.update(kwargs)
    return base


def test_key_crate_missing_crate_fails_closed():
    task = generate_task("key_crate", 1, "train")
    state = _state(
        objects={"statue": {"location": "pedestal"}},  # no crate record
    )
    assert StateBasedEvaluator().evaluate(task, state, []).success is False


def test_key_crate_missing_target_object_fails_closed():
    task = generate_task("key_crate", 1, "train")
    state = _state(
        objects={"crate": {"unlocked": True, "locked": False}},
    )
    assert StateBasedEvaluator().evaluate(task, state, []).success is False


def test_key_crate_unlock_flag_missing_fails_closed():
    task = generate_task("key_crate", 1, "train")
    state = _state(
        objects={
            "statue": {"location": "pedestal"},
            "crate": {"locked": False},  # unlocked key absent
        },
    )
    assert StateBasedEvaluator().evaluate(task, state, []).success is False


def test_key_crate_unlock_false_fails_closed():
    task = generate_task("key_crate", 1, "train")
    state = _state(
        objects={
            "statue": {"location": "pedestal"},
            "crate": {"unlocked": False, "locked": True},
        },
    )
    assert StateBasedEvaluator().evaluate(task, state, []).success is False


def test_key_crate_missing_objects_map_fails_closed():
    task = generate_task("key_crate", 1, "train")
    state = _state(objects=None)
    assert StateBasedEvaluator().evaluate(task, state, []).success is False


def test_dial_set_empty_targets_fail_closed():
    task = generate_task("dial_set", 1, "train")
    # Corrupt the goal with an empty target map.
    corrupted = generate_task("dial_set", 1, "train")
    object.__setattr__(corrupted, "hidden_goal", {"type": "dial_set", "targets": {}})
    state = _state(dials={"alpha": 0, "beta": 0, "gamma": 0})
    assert StateBasedEvaluator().evaluate(corrupted, state, []).success is False


def test_dial_set_missing_dial_fails_closed():
    task = generate_task("dial_set", 1, "train")
    targets = dict(task.hidden_goal["targets"])
    state = _state(dials={"alpha": targets["alpha"]})  # beta/gamma missing
    assert StateBasedEvaluator().evaluate(task, state, []).success is False


def test_dial_set_malformed_value_fails_closed():
    task = generate_task("dial_set", 1, "train")
    targets = dict(task.hidden_goal["targets"])
    dials = dict(targets)
    dials["alpha"] = "3"  # wrong type
    state = _state(dials=dials)
    assert StateBasedEvaluator().evaluate(task, state, []).success is False


def test_dial_set_missing_dials_map_fails_closed():
    task = generate_task("dial_set", 1, "train")
    state = _state(dials=None)
    assert StateBasedEvaluator().evaluate(task, state, []).success is False


def test_relay_missing_relay_fails_closed():
    task = generate_task("relay_route", 1, "held_out")
    state = _state(relay=None)
    assert StateBasedEvaluator().evaluate(task, state, []).success is False


def test_relay_malformed_frequency_fails_closed():
    task = generate_task("relay_route", 1, "held_out")
    freq = task.hidden_goal["frequency"]
    state = _state(relay={"activated": True, "frequency": str(freq)})
    assert StateBasedEvaluator().evaluate(task, state, []).success is False


def test_relay_not_activated_fails_closed():
    task = generate_task("relay_route", 1, "held_out")
    freq = task.hidden_goal["frequency"]
    state = _state(relay={"activated": False, "frequency": freq})
    assert StateBasedEvaluator().evaluate(task, state, []).success is False


def test_unknown_goal_type_fails_closed():
    task = generate_task("dial_set", 1, "train")
    object.__setattr__(task, "hidden_goal", {"type": "no_such_type", "targets": {}})
    assert StateBasedEvaluator().evaluate(task, _state(), []).success is False


def test_empty_goal_fails_closed():
    task = generate_task("dial_set", 1, "train")
    object.__setattr__(task, "hidden_goal", {})
    assert StateBasedEvaluator().evaluate(task, _state(), []).success is False


def test_non_mapping_state_fails_closed():
    task = generate_task("dial_set", 1, "train")
    assert StateBasedEvaluator().evaluate(task, None, []).success is False  # type: ignore[arg-type]


def test_happy_paths_still_pass():
    # key_crate
    t1 = generate_task("key_crate", 2, "train")
    crate_loc = t1.setup["objects"]["crate"]["location"]
    ped_loc = t1.setup["objects"]["pedestal"]["location"]
    s1 = _state(
        location=ped_loc,
        objects={
            "statue": {"type": "artifact", "location": "pedestal"},
            "crate": {"type": "crate", "unlocked": True, "locked": False, "location": crate_loc},
            "pedestal": {"type": "surface", "location": ped_loc},
        },
    )
    assert StateBasedEvaluator().evaluate(t1, s1, []).success is True

    # dial_set
    t2 = generate_task("dial_set", 2, "train")
    s2 = _state(dials=dict(t2.hidden_goal["targets"]))
    assert StateBasedEvaluator().evaluate(t2, s2, []).success is True

    # relay (requires a valid relay object plus relay state)
    t3 = generate_task("relay_route", 2, "held_out")
    s3 = _state(
        objects={"relay": {"type": "relay", "location": "hub"}},
        relay={"activated": True, "frequency": t3.hidden_goal["frequency"]},
    )
    assert StateBasedEvaluator().evaluate(t3, s3, []).success is True
