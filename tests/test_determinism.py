"""Determinism tests: seeds reproduce tasks and environment transitions."""
import copy

from agentfotagent.environments.tool_world import ToolWorld
from agentfotagent.interfaces import Action
from agentfotagent.tasks.generators import generate_split_manifests, generate_task

from conftest import action_list, episode, make_genome


def test_same_seed_same_task_content_hash():
    a = generate_task("key_crate", 7, "train")
    b = generate_task("key_crate", 7, "train")
    assert a.content_hash == b.content_hash
    assert a.hidden_goal == b.hidden_goal
    assert a.setup == b.setup


def test_different_seed_different_task():
    a = generate_task("key_crate", 7, "train")
    b = generate_task("key_crate", 8, "train")
    assert a.content_hash != b.content_hash


def test_split_manifests_reproducible():
    s1 = generate_split_manifests([1, 2], [3], [4])
    s2 = generate_split_manifests([1, 2], [3], [4])
    for key in ("train", "dev", "held_out"):
        h1 = [t.content_hash for t in s1[key]]
        h2 = [t.content_hash for t in s2[key]]
        assert h1 == h2


def test_environment_transitions_deterministic():
    task = generate_task("dial_set", 3, "train")
    script = [
        Action("read_offset_card", {}),
        Action("read_gauge", {"dial": "alpha"}),
        Action("read_gauge", {"dial": "beta"}),
        Action("set_dial", {"dial": "alpha", "value": 1}),
    ]

    def run_once():
        env = ToolWorld()
        env.reset(task)
        snaps = []
        for act in script:
            res = env.step(act)
            snaps.append(
                (
                    res.info.get("valid"),
                    res.info.get("result"),
                    env.final_state()["dials"].copy(),
                    res.observation.content["location"],
                )
            )
        return snaps

    assert run_once() == run_once()


def test_reset_restores_initial_state():
    task = generate_task("key_crate", 5, "train")
    env = ToolWorld()
    obs1 = env.reset(task)
    env.step(Action("move", {"location": "storage"}))
    env.step(Action("take", {"object_id": "coin_a"}))
    obs2 = env.reset(task)
    assert obs2.content == obs1.content
    assert env.final_state()["inventory"] == []


def test_mock_episode_reproducible():
    g = make_genome(planning_mode="plan_first", verification_policy="check_before_finalize")
    task = generate_task("key_crate", 2, "train")
    ok1, tr1, p1 = episode(g, "key_crate", "train", 2)
    ok2, tr2, p2 = episode(g, "key_crate", "train", 2)
    assert ok1 == ok2
    assert action_list(tr1) == action_list(tr2)
    assert tr1.final_state == tr2.final_state
