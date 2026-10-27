"""F3 regression: model-facing payload excludes evaluation-side metadata.

The exact object serialized to a backend must not contain seed, generator
version, content hash, split labels or hidden goals.
"""
import json

from agentfotagent.interfaces import RuntimeTask
from agentfotagent.runtime.mock_backend import MockBackend, MockPolicy, run_episode
from agentfotagent.runtime.phenotype import compile_phenotype
from agentfotagent.tasks.generators import generate_task

from conftest import make_genome


SENSITIVE_KEYS = {
    "seed",
    "generator_version",
    "content_hash",
    "hidden_goal",
    "split",
    "setup",
    "family",
    "lock_key",
    "targets",
    "required_unlock_key",
}


def test_runtime_task_payload_shape():
    task = generate_task("key_crate", 1, "train")
    payload = task.runtime.to_payload()
    assert set(payload.keys()) == {"task_id", "description", "max_steps"}
    for key in SENSITIVE_KEYS:
        assert key not in payload


def test_backend_payload_excludes_evaluation_metadata():
    task = generate_task("relay_route", 1, "held_out")
    g = make_genome()
    ok, trace, payload = run_episode(task, g, seed=1)

    backend_payload = payload.get("backend_payload")
    assert backend_payload is not None
    blob = json.dumps(backend_payload, sort_keys=True, default=str)

    # Keys must not appear.
    for key in SENSITIVE_KEYS:
        assert f'"{key}"' not in blob, f"backend payload leaked {key}"

    # Values of evaluation metadata must not appear.
    assert str(task.seed) not in blob or task.seed < 10  # small ints may collide in text
    assert task.content_hash not in blob
    assert task.generator_version not in blob
    code = task.hidden_goal.get("code")
    if code:
        assert str(code) not in blob

    # Context only carries runtime fields.
    context = backend_payload["context"]
    assert set(context.keys()) <= {"task_id", "description", "max_steps"}


def test_public_observation_and_context_are_all_backend_sees():
    task = generate_task("dial_set", 1, "train")
    ph = compile_phenotype(make_genome())
    policy = MockPolicy(phenotype=ph, runtime_task=task.runtime, family="dial_set")
    backend = MockBackend(policy)

    class SpyEnv:
        pass

    from agentfotagent.environments.tool_world import ToolWorld

    env = ToolWorld()
    obs = env.reset(task)
    runtime_context = task.runtime.to_payload()
    action = backend.propose(
        type("O", (), {"content": obs.content})(), runtime_context
    )
    assert backend.last_payload is not None
    blob = json.dumps(backend.last_payload, sort_keys=True, default=str)
    assert task.content_hash not in blob
    assert "hidden_goal" not in blob
    assert task.runtime.description in blob  # instruction is visible
    assert action.tool in {
        "make_plan",
        "read_offset_card",
        "read_gauge",
        "set_dial",
        "submit",
        "move",
        "list_objects",
        "inspect",
        "take",
        "place",
        "unlock",
        "verify_state",
        "read_note",
        "activate_relay",
        "set_frequency",
    }


def test_runtime_task_has_no_seed_or_hash_fields():
    rt = RuntimeTask(task_id="t", description="d", max_steps=3)
    assert not hasattr(rt, "seed")
    assert not hasattr(rt, "generator_version")
    assert not hasattr(rt, "content_hash")
    assert not hasattr(rt, "hidden_goal")
    assert not hasattr(rt, "split")
    assert not hasattr(rt, "family")
