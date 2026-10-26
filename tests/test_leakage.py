"""Leakage tests: hidden goals and evaluator internals are inaccessible to the Agent."""
import json

import pytest

from agentfotagent.environments.tool_world import (
    ALL_TOOLS,
    HiddenGoalAccessError,
    ToolWorld,
    _SealedGoal,
)
from agentfotagent.interfaces import Action
from agentfotagent.tasks.generators import generate_task
from agentfotagent.tasks.manifests import task_to_manifest_entry

from conftest import make_genome
from agentfotagent.runtime.mock_backend import run_episode


def _all_goal_strings(task) -> set:
    """Collect every string value that appears inside the hidden goal."""
    blob = json.dumps(task.hidden_goal, sort_keys=True, default=str)
    strings = set()

    def walk(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                strings.add(str(k))
                walk(v)
        elif isinstance(obj, list):
            for v in obj:
                walk(v)
        else:
            strings.add(str(obj))

    walk(task.hidden_goal)
    strings.discard("")
    return strings


def test_observation_never_contains_hidden_goal():
    for family, split in [("key_crate", "train"), ("dial_set", "train"), ("relay_route", "held_out")]:
        task = generate_task(family, 1, split)
        env = ToolWorld()
        obs = env.reset(task)
        goal_blob = json.dumps(task.hidden_goal, sort_keys=True, default=str)

        # Public view must not contain the serialized goal.
        assert goal_blob not in json.dumps(obs.content, sort_keys=True, default=str)

        # Sensitive goal-only fields must not appear as observation keys/values.
        sensitive = {"lock_key", "required_unlock_key", "targets", "code", "frequency", "formula", "note_digits"}
        obs_keys = set(obs.content.keys())
        assert not (sensitive & obs_keys), f"observation leaked goal keys: {sensitive & obs_keys}"

        # Gauges/offsets for dial_set are not the hidden targets.
        if family == "dial_set":
            assert "targets" not in obs.content
            assert set(obs.content.get("dials", {})) == set(task.hidden_goal["targets"])


def test_tools_never_expose_hidden_goal():
    task = generate_task("key_crate", 1, "train")
    env = ToolWorld()
    env.reset(task)
    goal = task.hidden_goal

    # Every read-only tool result must not contain lock_key / required keys.
    results = []
    results.append(env.step(Action("list_objects", {})).info)
    results.append(env.step(Action("inspect", {"object_id": "crate"})).info)
    results.append(env.step(Action("verify_state", {})).info)

    for info in results:
        text = json.dumps(info, sort_keys=True, default=str)
        assert "lock_key" not in text
        assert goal.get("required_unlock_key") not in text or "coin" not in text


def test_inspect_crate_does_not_reveal_lock_key():
    task = generate_task("key_crate", 1, "train")
    env = ToolWorld()
    env.reset(task)
    env.step(Action("move", {"location": "vault"}))
    res = env.step(Action("inspect", {"object_id": "crate"}))
    assert res.info["valid"] is True
    attrs = res.info["result"]
    assert "lock_key" not in attrs
    assert task.hidden_goal["required_unlock_key"] not in json.dumps(attrs)


def test_dial_tools_do_not_leak_targets():
    task = generate_task("dial_set", 1, "train")
    env = ToolWorld()
    env.reset(task)
    targets = task.hidden_goal["targets"]
    offsets = task.setup["offsets"]
    gauges = task.setup["gauges"]

    card = env.step(Action("read_offset_card", {}))
    assert card.info["result"]["offsets"] == offsets
    assert card.info["result"] != targets

    for dial, target in targets.items():
        g = env.step(Action("read_gauge", {"dial": dial}))
        assert g.info["result"]["gauge"] == gauges[dial]
        # gauge equals (target+offset)%4 — target itself is not returned.
        assert g.info["result"].get("target") is None


def test_sealed_goal_blocks_accidental_access():
    goal = _SealedGoal(goal={"type": "secret"})
    with pytest.raises(HiddenGoalAccessError):
        goal.unlock()
    # Explicit environment scoring path is the only unlock.
    assert goal.force_unlock()["type"] == "secret"


def test_public_manifest_omits_hidden_goal():
    task = generate_task("relay_route", 1, "held_out")
    entry = task_to_manifest_entry(task, include_hidden=False)
    assert "hidden_goal" not in entry
    assert "setup" not in entry
    text = json.dumps(entry, sort_keys=True, default=str)
    assert task.hidden_goal.get("code") not in text


def test_full_manifest_is_evaluation_side_only():
    """Full manifests include hidden goals but are not part of the runtime API."""
    task = generate_task("relay_route", 1, "held_out")
    entry = task_to_manifest_entry(task, include_hidden=True)
    assert "hidden_goal" in entry
    # Runtime receives PublicTask only — documented by the PublicTask fields.
    pub = task.public
    assert not hasattr(pub, "hidden_goal")
    assert not hasattr(pub, "setup")


def test_mock_episode_trace_has_no_hidden_goal_payload():
    task = generate_task("key_crate", 1, "train")
    g = make_genome()
    _, trace, _ = run_episode(task, g, seed=1)
    blob = json.dumps(trace.to_dict(), sort_keys=True, default=str)
    # lock_key must not appear in the agent-facing trace steps.
    for step in trace.steps:
        assert "lock_key" not in json.dumps(step, sort_keys=True, default=str)
        assert "hidden_goal" not in json.dumps(step, sort_keys=True, default=str)
