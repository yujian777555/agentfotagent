"""Split isolation, cache isolation and fail-closed error tests."""
import pytest

from agentfotagent.environments.tool_world import ToolWorld
from agentfotagent.evaluation.evaluator import StateBasedEvaluator
from agentfotagent.evaluation.provenance import config_hash
from agentfotagent.interfaces import Action
from agentfotagent.runtime.cache import CacheIsolationError, EvaluationCache, make_cache_key
from agentfotagent.runtime.mock_backend import run_episode
from agentfotagent.tasks.generators import FAMILY_SPLITS, generate_split_manifests, generate_task

from conftest import make_genome


def test_family_split_isolation(splits):
    train_fams = {t.family for t in splits["train"]}
    dev_fams = {t.family for t in splits["dev"]}
    held_fams = {t.family for t in splits["held_out"]}

    assert train_fams
    assert dev_fams
    assert held_fams
    # Held-out families are disjoint from train+dev (family-level holdout).
    assert held_fams.isdisjoint(train_fams | dev_fams)
    assert FAMILY_SPLITS["relay_route"] == ("held_out",)
    assert "relay_route" in held_fams
    assert "relay_route" not in train_fams | dev_fams


def test_task_ids_disjoint_across_splits(splits):
    ids = {}
    for name, tasks in splits.items():
        ids[name] = {t.task_id for t in tasks}
    assert ids["train"].isdisjoint(ids["dev"])
    assert ids["train"].isdisjoint(ids["held_out"])
    assert ids["dev"].isdisjoint(ids["held_out"])


def test_generate_task_rejects_wrong_split():
    with pytest.raises(ValueError):
        generate_task("relay_route", 1, "train")
    with pytest.raises(ValueError):
        generate_task("key_crate", 1, "held_out")


def test_cache_key_includes_split_and_content():
    base = dict(
        task_id="t1",
        task_content_hash="h1",
        split="train",
        genome_hash="g1",
        backend_id="mock-engineering-v2",
        config_hash="c1",
        environment_version="aes-tool-world-v2",
        evaluator_version="aes-evaluator-v2",
    )
    k_train = make_cache_key(**base)
    k_dev = make_cache_key(**{**base, "split": "dev"})
    k_other_task = make_cache_key(**{**base, "task_id": "t2", "task_content_hash": "h2"})
    k_other_genome = make_cache_key(**{**base, "genome_hash": "g2"})
    k_other_backend = make_cache_key(**{**base, "backend_id": "other"})
    k_other_config = make_cache_key(**{**base, "config_hash": "c2"})

    assert len({k_train, k_dev, k_other_task, k_other_genome, k_other_backend, k_other_config}) == 6


def test_held_out_cannot_reuse_dev_cache_entries():
    cache = EvaluationCache()
    task_train = generate_task("key_crate", 1, "train")
    task_held = generate_task("relay_route", 1, "held_out")

    key_train = make_cache_key(
        task_id=task_train.task_id,
        task_content_hash=task_train.content_hash,
        split="train",
        genome_hash="g",
        backend_id="b",
        config_hash="c",
        environment_version="v",
        evaluator_version="e",
    )
    from agentfotagent.interfaces import EpisodeResult

    result = EpisodeResult(
        task_id=task_train.task_id,
        genome_hash="g",
        success=True,
        steps=1,
        invalid_actions=0,
        repeated_states=0,
        termination_reason="agent_submit",
        final_state_hash="x",
    )
    cache.put(key_train, result, meta={"split": "train"})

    # Same key cannot be requested as held-out without isolation error.
    with pytest.raises(CacheIsolationError):
        cache.get(key_train, expected_split="held_out")

    # A held-out task gets a different key and a miss.
    key_held = make_cache_key(
        task_id=task_held.task_id,
        task_content_hash=task_held.content_hash,
        split="held_out",
        genome_hash="g",
        backend_id="b",
        config_hash="c",
        environment_version="v",
        evaluator_version="e",
    )
    assert cache.get(key_held, expected_split="held_out") is None


def test_invalid_action_does_not_mutate_world_state():
    task = generate_task("key_crate", 1, "train")
    env = ToolWorld()
    env.reset(task)
    before = env.final_state()
    res = env.step(Action("unlock", {"object_id": "crate", "key_id": "coin_z"}))
    assert res.info["valid"] is False
    after = env.final_state()
    assert after["objects"] == before["objects"]
    assert after["inventory"] == before["inventory"]
    assert after["location"] == before["location"]
    assert after["step"] == before["step"] + 1  # step still counts


def test_unknown_tool_fails_closed():
    task = generate_task("dial_set", 1, "train")
    env = ToolWorld()
    env.reset(task)
    res = env.step(Action("hack_the_planet", {}))
    assert res.info["valid"] is False
    assert res.terminated is False


def test_backend_error_fails_closed_and_not_success():
    task = generate_task("dial_set", 1, "train")
    g = make_genome()

    class Boom:
        def propose(self, observation, context):
            raise RuntimeError("backend exploded")

    from agentfotagent.environments.tool_world import ToolWorld as TW
    from agentfotagent.evaluation.evaluator import StateBasedEvaluator as EV
    from agentfotagent.evaluation.provenance import EpisodeTrace
    from agentfotagent.genome.schema import genome_hash

    env = TW()
    ev = EV(genome_hash=genome_hash(g))
    env.reset(task)
    trace = EpisodeTrace(
        task_id=task.task_id,
        split=task.split,
        genome_hash=genome_hash(g),
        backend_id="boom",
        seed=0,
    )
    try:
        Boom().propose({}, {})
    except Exception:
        final_state = env.final_state()
        result = ev.evaluate(task, final_state, trace.steps)
        assert result.success is False


def test_missing_output_fails_closed():
    task = generate_task("dial_set", 1, "train")
    # Backend returns an action without required args → invalid action, no success.
    env = ToolWorld()
    env.reset(task)
    res = env.step(Action("set_dial", {"dial": "alpha"}))  # missing value
    assert res.info["valid"] is False
    result = StateBasedEvaluator().evaluate(task, env.final_state(), [])
    # Not a success: dials untouched.
    assert result.success is False


def test_max_steps_termination_not_silently_successful():
    task = generate_task("key_crate", 1, "train")
    env = ToolWorld()
    env.reset(task)
    # Burn steps with no-ops that fail.
    for _ in range(task.runtime.max_steps):
        if env.final_state()["terminated"]:
            break
        env.step(Action("list_objects", {}))
    assert env.final_state()["termination_reason"] == "max_steps"
    result = StateBasedEvaluator().evaluate(task, env.final_state(), [])
    assert result.success is False
