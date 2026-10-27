"""F3 / R1-01 regression: model-facing payload excludes evaluation-side metadata.

Checks inspect the exact serialized backend payload string values, including
opaque runtime_id contents — not only field names. Family names, split labels
and seed encodings must not appear anywhere in the payload.
"""
import json
import re

from agentfotagent.interfaces import RuntimeTask
from agentfotagent.runtime.mock_backend import MockBackend, MockPolicy, run_episode
from agentfotagent.runtime.phenotype import compile_phenotype
from agentfotagent.tasks.generators import FAMILIES, generate_task

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
    "task_id",
}

FAMILY_TOKENS = tuple(FAMILIES)  # key_crate, dial_set, relay_route
SPLIT_TOKENS = ("train", "dev", "held_out", "held-out")


def _payload_blob(task, seed=None):
    """Run one episode and return the exact serialized backend payload."""
    g = make_genome()
    ok, trace, payload = run_episode(task, g, seed=seed if seed is not None else task.seed)
    assert "backend_payload" in payload
    return payload["backend_payload"]


def _assert_no_leakage(blob: str, task) -> None:
    lower = blob.lower()
    for key in SENSITIVE_KEYS:
        assert f'"{key}"' not in blob, f"payload leaked key name {key}"

    for fam in FAMILY_TOKENS:
        assert fam not in lower, f"payload leaked family token {fam!r}"
    for split in SPLIT_TOKENS:
        assert split not in lower, f"payload leaked split token {split!r}"

    # Seed encodings: explicit seedNNN pattern or /seed1 style from eval ids.
    assert not re.search(r"seed[_-]?\d+", lower), f"payload leaked seed encoding: {blob}"
    # The evaluation-side task_id string itself must not appear.
    assert task.task_id not in blob, "payload leaked evaluation task_id"
    assert task.content_hash not in blob, "payload leaked content_hash"
    assert task.generator_version not in blob, "payload leaked generator_version"


def test_runtime_task_payload_shape():
    task = generate_task("key_crate", 1, "train")
    payload = task.runtime.to_payload()
    assert set(payload.keys()) == {"runtime_id", "description", "max_steps"}
    for key in SENSITIVE_KEYS:
        assert key not in payload


def test_opaque_runtime_id_encodes_nothing_readable():
    for fam, split, seed in [
        ("key_crate", "train", 1),
        ("dial_set", "dev", 11),
        ("relay_route", "held_out", 21),
    ]:
        task = generate_task(fam, seed, split)
        rid = task.runtime.runtime_id
        assert rid.startswith("rt_")
        # Opaque: hex digest, no family/split text or structured seed encoding.
        assert re.fullmatch(r"rt_[0-9a-f]{16}", rid), rid
        assert fam not in rid
        assert split not in rid
        assert f"seed{seed}" not in rid
        assert f"seed{seed:06d}" not in rid
        # Distinct from evaluation-side id which does encode metadata.
        assert rid != task.task_id
        assert task.task_id.startswith(fam)  # eval id still encodes metadata


def test_backend_payload_string_values_do_not_leak():
    for fam, split, seed in [
        ("key_crate", "train", 1),
        ("dial_set", "train", 1),
        ("relay_route", "held_out", 1),
    ]:
        task = generate_task(fam, seed, split)
        backend_payload = _payload_blob(task)
        blob = json.dumps(backend_payload, sort_keys=True, default=str)
        _assert_no_leakage(blob, task)
        # Also check each observed step's backend-visible object.
        context = backend_payload["context"]
        assert set(context.keys()) <= {"runtime_id", "description", "max_steps"}


def test_seed_value_not_in_payload_even_for_small_seeds():
    """Previously the test permitted small seeds; now every seed is checked."""
    task = generate_task("relay_route", 1, "held_out")
    backend_payload = _payload_blob(task)
    blob = json.dumps(backend_payload, sort_keys=True, default=str)
    # Direct seed field
    assert '"seed"' not in blob
    # String forms of the seed value as an id fragment
    assert f"seed{task.seed}" not in blob.lower()
    assert f"seed{task.seed:06d}" not in blob.lower()
    assert "/seed" not in blob.lower()
    _assert_no_leakage(blob, task)


def test_serialized_full_run_payload_has_no_eval_ids():
    task = generate_task("key_crate", 2, "train")
    g = make_genome()
    ok, trace, payload = run_episode(task, g, seed=2)
    # Trace is evaluation-side and may carry eval ids; backend payload must not.
    blob = json.dumps(payload.get("backend_payload"), sort_keys=True, default=str)
    _assert_no_leakage(blob, task)
    # Full artifact includes traces (eval side) — those keep task_id for reconstruction.
    assert trace.task_id == task.task_id


def test_runtime_task_has_no_eval_metadata_fields():
    rt = RuntimeTask(runtime_id="rt_abc", description="d", max_steps=3)
    assert not hasattr(rt, "seed")
    assert not hasattr(rt, "generator_version")
    assert not hasattr(rt, "content_hash")
    assert not hasattr(rt, "hidden_goal")
    assert not hasattr(rt, "split")
    assert not hasattr(rt, "family")
    assert not hasattr(rt, "task_id")


def test_runtime_ids_are_stable_across_regeneration():
    a = generate_task("dial_set", 3, "train")
    b = generate_task("dial_set", 3, "train")
    assert a.runtime.runtime_id == b.runtime.runtime_id
    assert a.content_hash == b.content_hash
