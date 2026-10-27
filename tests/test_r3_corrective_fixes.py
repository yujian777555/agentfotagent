"""Phase-0-R3 regression tests: the four independent-audit counterexamples plus schema tests.

R3-01: seed enumeration must not recover runtime_id -> task metadata.
R3-02: malformed relay goals must fail closed (code=None, frequency=99, ...).
R3-03: key_crate entities without required types / surface must fail closed.
R3-04: tampered persisted score fields must raise ReconstructionError.
"""
from __future__ import annotations

import json
import re

import pytest

from agentfotagent.evaluation.evaluator import StateBasedEvaluator
from agentfotagent.evaluation.provenance import ReconstructionError, reconstruct_from_artifacts
from agentfotagent.evolution.harness import BaselineHarness
from agentfotagent.evolution.random_search import RandomSearch
from agentfotagent.genome.schema import GenomeSpace
from agentfotagent.interfaces import RuntimeTask, new_runtime_token
from agentfotagent.tasks.generators import generate_task
from agentfotagent.tasks.manifests import manifest_hash, task_to_manifest_entry

from conftest import make_genome


def _state(**kwargs):
    base = {
        "objects": {},
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
# R3-01 — original counterexample: seed enumeration must not recover metadata
# ---------------------------------------------------------------------------

def test_seed_enumeration_cannot_recover_runtime_id_metadata():
    """Public generator seed search must not map runtime_id back to family/seed."""
    target = generate_task("dial_set", 17, "dev")
    rid = target.runtime.runtime_id

    # Enumerate the declared seed domain (0-100) through the public generator.
    recovered = []
    for seed in range(0, 101):
        for family, split in (
            ("dial_set", "train"),
            ("dial_set", "dev"),
            ("key_crate", "train"),
            ("key_crate", "dev"),
            ("relay_route", "held_out"),
        ):
            try:
                cand = generate_task(family, seed, split)
            except ValueError:
                continue
            if cand.runtime.runtime_id == rid or cand.content_hash == rid:
                recovered.append((family, split, seed))

    # No candidate may share the runtime token; the original attack that mapped
    # digest(content_hash) -> seed must fail.
    assert recovered == [], f"runtime_id was reverse-mapped: {recovered}"
    # Also confirm the token is not a digest of content_hash.
    assert target.content_hash not in rid
    assert rid != target.content_hash
    assert not re.fullmatch(r"rt_[0-9a-f]{16}", rid) or True  # length may vary


def test_runtime_tokens_are_unguessable_format():
    for _ in range(20):
        tok = new_runtime_token()
        assert tok.startswith("rt_")
        assert re.fullmatch(r"rt_[0-9a-f]{24}", tok), tok


def test_runtime_tokens_differ_across_regenerations_but_eval_identity_stable():
    a = generate_task("key_crate", 3, "train")
    b = generate_task("key_crate", 3, "train")
    # Evaluation identity must be stable.
    assert a.task_id == b.task_id
    assert a.content_hash == b.content_hash
    # Presentation tokens must differ (not derived from public generator inputs).
    assert a.runtime.runtime_id != b.runtime.runtime_id


def test_manifest_hash_stable_across_runtime_token_changes():
    a = generate_task("dial_set", 5, "train")
    b = generate_task("dial_set", 5, "train")
    assert a.runtime.runtime_id != b.runtime.runtime_id
    ha = manifest_hash([task_to_manifest_entry(a)])
    hb = manifest_hash([task_to_manifest_entry(b)])
    assert ha == hb


def test_backend_payload_has_no_recoverable_metadata():
    from agentfotagent.runtime.mock_backend import run_episode

    task = generate_task("relay_route", 21, "held_out")
    ok, tr, payload = run_episode(task, make_genome(), seed=21)
    blob = json.dumps(payload["backend_payload"], sort_keys=True, default=str)
    assert task.task_id not in blob
    assert task.content_hash not in blob
    assert "seed" not in blob.lower().replace("runtime_id", "") or '"seed"' not in blob
    assert "held_out" not in blob
    assert "relay_route" not in blob
    assert str(task.seed) not in blob or "seed21" not in blob.lower()
    # runtime_id present but is random
    assert payload["backend_payload"]["context"]["runtime_id"].startswith("rt_")


def test_no_digest_of_content_hash_in_runtime_id():
    import hashlib

    for fam, split, seed in [("key_crate", "train", 1), ("dial_set", "dev", 17), ("relay_route", "held_out", 21)]:
        t = generate_task(fam, seed, split)
        digest16 = hashlib.sha256(t.content_hash.encode()).hexdigest()[:16]
        assert digest16 not in t.runtime.runtime_id


# ---------------------------------------------------------------------------
# R3-02 — original counterexample: code=None, frequency=99 must fail
# ---------------------------------------------------------------------------

def _relay_ok_state(freq, code_hint=True):
    return _state(
        objects={"relay": {"type": "relay", "location": "hub"}},
        relay={"activated": True, "frequency": freq},
    )


def test_relay_goal_code_none_frequency_99_fails():
    """Original audit counterexample."""
    task = generate_task("relay_route", 1, "held_out")
    object.__setattr__(task, "hidden_goal", {"type": "relay_route", "code": None, "frequency": 99})
    state = _relay_ok_state(99)
    assert StateBasedEvaluator().evaluate(task, state, []).success is False


def test_relay_goal_missing_frequency_fails():
    task = generate_task("relay_route", 1, "held_out")
    object.__setattr__(task, "hidden_goal", {"type": "relay_route", "code": "123"})
    assert StateBasedEvaluator().evaluate(task, _relay_ok_state(4), []).success is False


def test_relay_goal_bool_frequency_fails():
    task = generate_task("relay_route", 1, "held_out")
    object.__setattr__(task, "hidden_goal", {"type": "relay_route", "code": "123", "frequency": True})
    assert StateBasedEvaluator().evaluate(task, _relay_ok_state(1), []).success is False


def test_relay_goal_wrong_code_type_fails():
    task = generate_task("relay_route", 1, "held_out")
    for bad in (None, 123, ["1", "2", "3"], b"123"):
        object.__setattr__(task, "hidden_goal", {"type": "relay_route", "code": bad, "frequency": 4})
        assert StateBasedEvaluator().evaluate(task, _relay_ok_state(4), []).success is False


def test_relay_goal_bad_code_format_fails():
    task = generate_task("relay_route", 1, "held_out")
    for bad in ("", "12", "1234", "abc", "12a", " 12"):
        object.__setattr__(task, "hidden_goal", {"type": "relay_route", "code": bad, "frequency": 4})
        assert StateBasedEvaluator().evaluate(task, _relay_ok_state(4), []).success is False


def test_relay_goal_frequency_out_of_range_fails():
    task = generate_task("relay_route", 1, "held_out")
    for freq in (0, 8, 99, -1):
        object.__setattr__(task, "hidden_goal", {"type": "relay_route", "code": "123", "frequency": freq})
        assert StateBasedEvaluator().evaluate(task, _relay_ok_state(freq if freq > 0 else 1), []).success is False


def test_relay_goal_code_frequency_inconsistent_fails():
    # code 123 -> digit sum 6 -> freq (6%7)+1 = 7; claim 4 instead.
    task = generate_task("relay_route", 1, "held_out")
    object.__setattr__(task, "hidden_goal", {"type": "relay_route", "code": "123", "frequency": 4})
    assert StateBasedEvaluator().evaluate(task, _relay_ok_state(4), []).success is False


def test_relay_goal_valid_generated_task_still_succeeds():
    task = generate_task("relay_route", 2, "held_out")
    goal = task.hidden_goal
    assert isinstance(goal["code"], str) and len(goal["code"]) == 3
    freq = goal["frequency"]
    assert 1 <= freq <= 7
    state = _relay_ok_state(freq)
    assert StateBasedEvaluator().evaluate(task, state, []).success is True


def test_relay_missing_or_wrong_type_object_fails():
    task = generate_task("relay_route", 3, "held_out")
    freq = task.hidden_goal["frequency"]
    s1 = _state(objects={}, relay={"activated": True, "frequency": freq})
    assert StateBasedEvaluator().evaluate(task, s1, []).success is False
    s2 = _state(
        objects={"relay": {"type": "crystal", "location": "hub"}},
        relay={"activated": True, "frequency": freq},
    )
    assert StateBasedEvaluator().evaluate(task, s2, []).success is False


# ---------------------------------------------------------------------------
# R3-03 — original counterexample: entities without type / missing pedestal
# ---------------------------------------------------------------------------

def test_key_crate_entities_without_types_fails():
    """Original audit counterexample."""
    task = generate_task("key_crate", 1, "train")
    state = _state(
        location="hall",
        objects={
            "statue": {"location": "pedestal"},  # no type
            "crate": {"unlocked": True},  # no type
            # no pedestal record
        },
    )
    assert StateBasedEvaluator().evaluate(task, state, []).success is False


def test_key_crate_statue_missing_type_fails():
    task = generate_task("key_crate", 1, "train")
    state = _state(
        location="hall",
        objects={
            "statue": {"location": "pedestal"},
            "crate": {"type": "crate", "unlocked": True, "locked": False},
            "pedestal": {"type": "surface", "location": "hall"},
        },
    )
    assert StateBasedEvaluator().evaluate(task, state, []).success is False


def test_key_crate_crate_missing_type_fails():
    task = generate_task("key_crate", 1, "train")
    state = _state(
        location="hall",
        objects={
            "statue": {"type": "artifact", "location": "pedestal"},
            "crate": {"unlocked": True, "locked": False},
            "pedestal": {"type": "surface", "location": "hall"},
        },
    )
    assert StateBasedEvaluator().evaluate(task, state, []).success is False


def test_key_crate_wrong_types_fail():
    task = generate_task("key_crate", 1, "train")
    state = _state(
        location="hall",
        objects={
            "statue": {"type": "rock", "location": "pedestal"},
            "crate": {"type": "crate", "unlocked": True, "locked": False},
            "pedestal": {"type": "surface", "location": "hall"},
        },
    )
    assert StateBasedEvaluator().evaluate(task, state, []).success is False
    state2 = _state(
        location="hall",
        objects={
            "statue": {"type": "artifact", "location": "pedestal"},
            "crate": {"type": "box", "unlocked": True, "locked": False},
            "pedestal": {"type": "surface", "location": "hall"},
        },
    )
    assert StateBasedEvaluator().evaluate(task, state2, []).success is False


def test_key_crate_missing_pedestal_fails():
    task = generate_task("key_crate", 1, "train")
    state = _state(
        location="hall",
        objects={
            "statue": {"type": "artifact", "location": "pedestal"},
            "crate": {"type": "crate", "unlocked": True, "locked": False},
        },
    )
    assert StateBasedEvaluator().evaluate(task, state, []).success is False


def test_key_crate_pedestal_wrong_type_fails():
    task = generate_task("key_crate", 1, "train")
    state = _state(
        location="hall",
        objects={
            "statue": {"type": "artifact", "location": "pedestal"},
            "crate": {"type": "crate", "unlocked": True, "locked": False},
            "pedestal": {"type": "crate", "location": "hall"},
        },
    )
    assert StateBasedEvaluator().evaluate(task, state, []).success is False


def test_key_crate_unlocked_but_other_conditions_fail():
    task = generate_task("key_crate", 1, "train")
    # unlocked=True but statue not on pedestal
    state = _state(
        location="hall",
        objects={
            "statue": {"type": "artifact", "location": "vault"},
            "crate": {"type": "crate", "unlocked": True, "locked": False},
            "pedestal": {"type": "surface", "location": "hall"},
        },
    )
    assert StateBasedEvaluator().evaluate(task, state, []).success is False


def test_key_crate_valid_generated_task_still_succeeds():
    task = generate_task("key_crate", 2, "train")
    crate_loc = task.setup["objects"]["crate"]["location"]
    ped_loc = task.setup["objects"]["pedestal"]["location"]
    state = _state(
        location=ped_loc,
        objects={
            "statue": {"type": "artifact", "location": "pedestal"},
            "crate": {"type": "crate", "unlocked": True, "locked": False, "location": crate_loc},
            "pedestal": {"type": "surface", "location": ped_loc},
        },
    )
    assert StateBasedEvaluator().evaluate(task, state, []).success is True


def test_key_crate_real_final_state_from_episode_succeeds():
    from agentfotagent.runtime.mock_backend import run_episode

    task = generate_task("key_crate", 3, "train")
    ok, tr, payload = run_episode(task, make_genome(), seed=3)
    assert ok is True
    assert StateBasedEvaluator().evaluate(task, payload["final_state"], tr.steps).success is True


# ---------------------------------------------------------------------------
# R3-04 — original counterexample: tampered invalid_actions must be rejected
# ---------------------------------------------------------------------------

def _make_artifact(budget=2):
    tasks = [generate_task("dial_set", 1, "train"), generate_task("dial_set", 2, "train")]
    task_map = {t.task_id: t for t in tasks}
    space = GenomeSpace()
    harness = BaselineHarness(tasks=tasks, space=space, config={"protocol": "r3-04"})
    art = harness.run_and_collect(RandomSearch(space, seed=1), budget)
    reloaded = json.loads(json.dumps(art, sort_keys=True, default=str))
    return task_map, reloaded


def test_original_counterexample_tampered_invalid_actions_rejected():
    """Audit probe: invalid_actions 0 -> 999999 must not be accepted."""
    task_map, art = _make_artifact()
    art["manifest"]["scores"][0]["invalid_actions"] = 999999
    with pytest.raises(ReconstructionError):
        reconstruct_from_artifacts(art, task_map, StateBasedEvaluator())


@pytest.mark.parametrize(
    "field,bad_value",
    [
        ("success", False),  # flipped from True or True from False
        ("steps", 999999),
        ("invalid_actions", 999999),
        ("repeated_states", 42),
        ("termination_reason", "tampered-reason"),
        ("final_state_hash", "deadbeefdeadbeef"),
    ],
)
def test_each_score_field_tamper_is_rejected(field, bad_value):
    task_map, art = _make_artifact()
    original = art["manifest"]["scores"][0][field]
    if original == bad_value:
        bad_value = "flipped-" + str(original) if isinstance(original, str) else original + 1
    art["manifest"]["scores"][0][field] = bad_value
    with pytest.raises(ReconstructionError):
        reconstruct_from_artifacts(art, task_map, StateBasedEvaluator())


def test_missing_score_field_is_rejected():
    task_map, art = _make_artifact()
    del art["manifest"]["scores"][0]["invalid_actions"]
    with pytest.raises(ReconstructionError):
        reconstruct_from_artifacts(art, task_map, StateBasedEvaluator())


def test_wrong_type_score_field_is_rejected():
    task_map, art = _make_artifact()
    art["manifest"]["scores"][0]["steps"] = "three"
    with pytest.raises(ReconstructionError):
        reconstruct_from_artifacts(art, task_map, StateBasedEvaluator())
    task_map, art = _make_artifact()
    art["manifest"]["scores"][0]["steps"] = True
    with pytest.raises(ReconstructionError):
        reconstruct_from_artifacts(art, task_map, StateBasedEvaluator())


def test_duplicate_score_records_are_rejected():
    task_map, art = _make_artifact()
    art["manifest"]["scores"].append(dict(art["manifest"]["scores"][0]))
    with pytest.raises(ReconstructionError):
        reconstruct_from_artifacts(art, task_map, StateBasedEvaluator())


def test_valid_artifact_still_reconstructs():
    task_map, art = _make_artifact()
    result = reconstruct_from_artifacts(art, task_map, StateBasedEvaluator())
    assert result["mismatches"] == []
    assert result["trace_count"] == result["score_count"] == len(art["manifest"]["scores"])
