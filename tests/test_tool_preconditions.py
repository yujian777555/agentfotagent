"""F1 regression: tool-world preconditions must prevent remote state changes.

A state-changing action must not mutate business state when a locality or
state precondition fails. Unlock must be local; contents release at the
container; place must be local; dial/relay tools must be local.
"""
from agentfotagent.environments.tool_world import ToolWorld, _business_state
from agentfotagent.interfaces import Action
from agentfotagent.tasks.generators import generate_task

from conftest import make_genome
from agentfotagent.runtime.mock_backend import run_episode


def _reset(family, split, seed):
    task = generate_task(family, seed, split)
    env = ToolWorld()
    env.reset(task)
    return task, env


def _biz(env):
    return _business_state(env.final_state())


def test_remote_unlock_rejected_no_mutation():
    task, env = _reset("key_crate", "train", 1)
    env.step(Action("move", {"location": "storage"}))
    # Take a coin in storage, then try to unlock the crate in vault from here.
    visible = env.current_public_view["visible_objects"]
    coin = [o for o in visible if str(o).startswith("coin")][0]
    env.step(Action("take", {"object_id": coin}))
    before = _biz(env)
    res = env.step(Action("unlock", {"object_id": "crate", "key_id": coin}))
    assert res.info["valid"] is False
    assert "not here" in res.info.get("error", "")
    after = _biz(env)
    assert after["objects"] == before["objects"]
    assert after["inventory"] == before["inventory"]
    assert env.final_state()["objects"]["crate"]["unlocked"] is False


def test_unlock_releases_contents_at_container_location():
    """Correct-key unlock places statue at the crate's location (vault), not the caller's."""
    task = generate_task("key_crate", 1, "train")
    key_id = task.hidden_goal["required_unlock_key"]
    key_room = task.setup["objects"][key_id]["location"]
    env = ToolWorld()
    env.reset(task)
    env.step(Action("move", {"location": key_room}))
    env.step(Action("take", {"object_id": key_id}))
    env.step(Action("move", {"location": "vault"}))
    res = env.step(Action("unlock", {"object_id": "crate", "key_id": key_id}))
    assert res.info["valid"] is True
    statue = env.final_state()["objects"]["statue"]
    assert statue["location"] == "vault"
    assert statue.get("concealed") is False
    assert statue.get("inside") is None


def test_remote_place_rejected_no_mutation():
    task, env = _reset("key_crate", "train", 1)
    key_id = task.hidden_goal["required_unlock_key"]
    key_room = task.setup["objects"][key_id]["location"]
    env.step(Action("move", {"location": key_room}))
    env.step(Action("take", {"object_id": key_id}))
    before = _biz(env)
    # Pedestal is in hall; agent is not at hall.
    res = env.step(Action("place", {"object_id": key_id, "location": "pedestal"}))
    assert res.info["valid"] is False
    assert "not in range" in res.info.get("error", "")
    after = _biz(env)
    assert after["objects"] == before["objects"]
    assert key_id in after["inventory"]


def test_place_requires_destination_local():
    task, env = _reset("key_crate", "train", 1)
    key_id = task.hidden_goal["required_unlock_key"]
    key_room = task.setup["objects"][key_id]["location"]
    env.step(Action("move", {"location": key_room}))
    env.step(Action("take", {"object_id": key_id}))
    env.step(Action("move", {"location": "hall"}))
    res = env.step(Action("place", {"object_id": key_id, "location": "pedestal"}))
    assert res.info["valid"] is True
    assert env.final_state()["objects"][key_id]["location"] == "pedestal"


def test_remote_set_dial_rejected():
    task, env = _reset("dial_set", "train", 1)
    # dial_set starts at console; move is only console, so fabricate departure is impossible.
    # Use a key_crate world then attempt dial — unknown dial already fails.
    # Direct locality: call set_dial after forcibly changing location via move to another room.
    # dial_set has a single location, so instead construct env on key_crate and attempt dial tools.
    task2, env2 = _reset("key_crate", "train", 1)
    env2.step(Action("move", {"location": "storage"}))
    before = _biz(env2)
    res = env2.step(Action("set_dial", {"dial": "alpha", "value": 1}))
    assert res.info["valid"] is False
    after = _biz(env2)
    assert after["dials"] == before["dials"]


def test_set_dial_locality_with_two_location_task():
    """dial tools must fail when the agent is not at dial_location."""
    task = generate_task("dial_set", 1, "train")
    # Force a non-console location by injecting a movable room into setup copy.
    setup = dict(task.setup)
    setup["locations"] = ["console", "hall"]
    setup["start_location"] = "hall"
    setup["dial_location"] = "console"
    from agentfotagent.interfaces import TaskInstance, RuntimeTask

    task2 = TaskInstance(
        runtime=RuntimeTask(
            runtime_id=task.runtime.runtime_id,
            description=task.runtime.description,
            max_steps=task.runtime.max_steps,
        ),
        family=task.family,
        split=task.split,
        hidden_goal=dict(task.hidden_goal),
        setup=setup,
        seed=task.seed,
        generator_version=task.generator_version,
        content_hash="locality-test",
        task_id=task.task_id,
    )
    env = ToolWorld()
    env.reset(task2)
    assert env.current_public_view["location"] == "hall"
    before = _biz(env)
    res = env.step(Action("set_dial", {"dial": "alpha", "value": 2}))
    assert res.info["valid"] is False
    assert "not in range" in res.info.get("error", "")
    assert _biz(env)["dials"] == before["dials"]

    res2 = env.step(Action("read_gauge", {"dial": "alpha"}))
    assert res2.info["valid"] is False
    res3 = env.step(Action("read_offset_card", {}))
    assert res3.info["valid"] is False

    # Moving to the console unlocks dial tools.
    env.step(Action("move", {"location": "console"}))
    res4 = env.step(Action("set_dial", {"dial": "alpha", "value": 2}))
    assert res4.info["valid"] is True


def test_remote_relay_activation_rejected():
    task, env = _reset("relay_route", "held_out", 1)
    code = task.setup["relay"]["code"]
    env.step(Action("move", {"location": "north"}))
    before = _biz(env)
    res = env.step(Action("activate_relay", {"code": code}))
    assert res.info["valid"] is False
    assert "relay" in res.info.get("error", "")
    assert _biz(env)["relay"]["activated"] is not True

    res2 = env.step(Action("set_frequency", {"frequency": 3}))
    assert res2.info["valid"] is False
    assert _biz(env)["relay"]["frequency"] == before["relay"]["frequency"]


def test_relay_tools_work_at_hub():
    task, env = _reset("relay_route", "held_out", 1)
    code = task.setup["relay"]["code"]
    # Already at hub.
    res = env.step(Action("activate_relay", {"code": code}))
    assert res.info["valid"] is True
    freq = task.hidden_goal["frequency"]
    res2 = env.step(Action("set_frequency", {"frequency": freq}))
    assert res2.info["valid"] is True


def test_failed_actions_do_not_mutate_business_state():
    task, env = _reset("key_crate", "train", 2)
    env.step(Action("move", {"location": "vault"}))
    before = _biz(env)
    for bad in (
        Action("take", {"object_id": "nope"}),
        Action("unlock", {"object_id": "crate", "key_id": "nope"}),
        Action("place", {"object_id": "statue", "location": "hall"}),
        Action("hack", {}),
        Action("set_dial", {"dial": "alpha", "value": 1}),
    ):
        res = env.step(bad)
        assert res.info["valid"] is False
        assert _biz(env) == before


def test_mock_policy_still_solves_after_locality_enforcement():
    """Locality rules must not make valid tasks unsolvable."""
    g = make_genome(
        planning_mode="plan_first",
        memory_policy="bounded_episodic",
        verification_policy="check_before_finalize",
        tool_selection_policy="state_conditioned",
    )
    for fam, split, seed in [
        ("key_crate", "train", 1),
        ("key_crate", "train", 2),
        ("dial_set", "train", 1),
        ("relay_route", "held_out", 1),
    ]:
        ok, tr, _ = run_episode(generate_task(fam, seed, split), g, seed=seed)
        assert ok, f"{fam}/{seed} must remain solvable under locality rules"
