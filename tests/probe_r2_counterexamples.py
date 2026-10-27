"""Original R2/R3 independent-audit counterexamples as a strict standalone probe.

Pass/fail semantics (R4-04):
- Each probe returns True if the malformed input was correctly REJECTED.
- Each probe returns False if it was wrongly ACCEPTED.
- Unexpected exception types are recorded as False (not PASS).
- Exit code 0 only when every probe returns True.
"""
from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path
from typing import Callable, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agentfotagent.evaluation.evaluator import StateBasedEvaluator
from agentfotagent.evaluation.provenance import (
    ReconstructionError,
    reconstruct_from_artifacts,
)
from agentfotagent.evolution.harness import BaselineHarness
from agentfotagent.evolution.random_search import RandomSearch
from agentfotagent.genome.schema import GenomeSpace
from agentfotagent.tasks.generators import generate_task


class UnexpectedProbeAcceptance(RuntimeError):
    """Raised only in self-tests when a vulnerable stub is correctly detected as FAIL."""


def probe_r3_01_seed_enumeration() -> Tuple[bool, str]:
    """PASS only if no seed in 0..100 maps runtime_id to the target task."""
    target = generate_task("dial_set", 17, "dev")
    rid = target.runtime.runtime_id
    recovered = []
    for seed in range(0, 101):
        for family, split in (
            ("dial_set", "dev"),
            ("dial_set", "train"),
            ("key_crate", "train"),
            ("key_crate", "dev"),
            ("relay_route", "held_out"),
        ):
            try:
                cand = generate_task(family, seed, split)
            except ValueError:
                continue
            if cand.runtime.runtime_id == rid:
                recovered.append(f"{family}/{split}/{seed}")
    if recovered:
        return False, f"seed recovered: {recovered}"
    return True, "no seed in 0-100 recovered runtime_id"


def probe_r3_02_relay_goal() -> Tuple[bool, str]:
    """PASS only if malformed relay goal (code=None, frequency=99) is rejected."""
    task = generate_task("relay_route", 1, "held_out")
    object.__setattr__(
        task, "hidden_goal", {"type": "relay_route", "code": None, "frequency": 99}
    )
    state = {
        "objects": {"relay": {"type": "relay", "location": "hub"}},
        "relay": {"activated": True, "frequency": 99},
        "dials": {},
        "inventory": [],
        "location": "hub",
        "step": 5,
        "termination_reason": "agent_submit",
    }
    try:
        ok = StateBasedEvaluator().evaluate(task, state, []).success
    except Exception as exc:
        return False, f"unexpected exception: {type(exc).__name__}: {exc}"
    if ok:
        return False, "malformed relay goal ACCEPTED"
    return True, "malformed relay goal rejected"


def probe_r3_03_key_crate_entities() -> Tuple[bool, str]:
    """PASS only if entities without types/pedestal/location are rejected."""
    task = generate_task("key_crate", 1, "train")
    state = {
        "objects": {
            "statue": {"location": "pedestal"},
            "crate": {"unlocked": True},
        },
        "dials": {},
        "relay": {},
        "inventory": [],
        "location": "hall",
        "step": 5,
        "termination_reason": "agent_submit",
    }
    try:
        ok = StateBasedEvaluator().evaluate(task, state, []).success
    except Exception as exc:
        return False, f"unexpected exception: {type(exc).__name__}: {exc}"
    if ok:
        return False, "malformed key_crate entities ACCEPTED"
    return True, "malformed key_crate entities rejected"


def probe_r3_04_score_tamper() -> Tuple[bool, str]:
    """PASS only if tampered invalid_actions raises ReconstructionError."""
    tasks = [generate_task("dial_set", 1, "train")]
    space = GenomeSpace()
    harness = BaselineHarness(tasks=tasks, space=space, config={"protocol": "probe-r4"})
    art = json.loads(json.dumps(harness.run_and_collect(RandomSearch(space, seed=1), 1), default=str))
    art["manifest"]["scores"][0]["invalid_actions"] = 999999
    task_map = {t.task_id: t for t in tasks}
    try:
        reconstruct_from_artifacts(art, task_map, StateBasedEvaluator())
    except ReconstructionError as exc:
        return True, f"tampered score rejected: {exc}"
    except Exception as exc:
        return False, f"unexpected exception: {type(exc).__name__}: {exc}"
    return False, "tampered invalid_actions ACCEPTED"


def probe_r4_01_success_type() -> Tuple[bool, str]:
    """PASS only if integer success=1 is rejected."""
    tasks = [generate_task("dial_set", 1, "train")]
    space = GenomeSpace()
    harness = BaselineHarness(tasks=tasks, space=space, config={"protocol": "probe-r401"})
    art = json.loads(json.dumps(harness.run_and_collect(RandomSearch(space, seed=2), 1), default=str))
    art["manifest"]["scores"][0]["success"] = 1  # int, not bool
    task_map = {t.task_id: t for t in tasks}
    try:
        reconstruct_from_artifacts(art, task_map, StateBasedEvaluator())
    except ReconstructionError as exc:
        return True, f"non-bool success rejected: {exc}"
    except Exception as exc:
        return False, f"unexpected exception: {type(exc).__name__}: {exc}"
    return False, "integer success ACCEPTED"


def probe_r4_02_unknown_field() -> Tuple[bool, str]:
    """PASS only if unknown score field is rejected."""
    tasks = [generate_task("dial_set", 1, "train")]
    space = GenomeSpace()
    harness = BaselineHarness(tasks=tasks, space=space, config={"protocol": "probe-r402"})
    art = json.loads(json.dumps(harness.run_and_collect(RandomSearch(space, seed=3), 1), default=str))
    art["manifest"]["scores"][0]["unvalidated_metric"] = 999999
    task_map = {t.task_id: t for t in tasks}
    try:
        reconstruct_from_artifacts(art, task_map, StateBasedEvaluator())
    except ReconstructionError as exc:
        return True, f"unknown field rejected: {exc}"
    except Exception as exc:
        return False, f"unexpected exception: {type(exc).__name__}: {exc}"
    return False, "unknown score field ACCEPTED"


def probe_r4_03_locations() -> Tuple[bool, str]:
    """PASS only if missing crate/surface locations are rejected."""
    task = generate_task("key_crate", 1, "train")
    state = {
        "objects": {
            "statue": {"type": "artifact", "location": "pedestal"},
            "crate": {"type": "crate", "unlocked": True},  # no location
            "pedestal": {"type": "surface"},  # no location
        },
        "dials": {},
        "relay": {},
        "inventory": [],
        "location": "hall",
        "step": 5,
        "termination_reason": "agent_submit",
    }
    try:
        ok = StateBasedEvaluator().evaluate(task, state, []).success
    except Exception as exc:
        return False, f"unexpected exception: {type(exc).__name__}: {exc}"
    if ok:
        return False, "missing entity locations ACCEPTED"
    return True, "missing entity locations rejected"


def run_probes(probes: List[Tuple[str, Callable[[], Tuple[bool, str]]]]) -> int:
    failures = 0
    for name, fn in probes:
        try:
            passed, detail = fn()
        except Exception as exc:
            passed, detail = False, f"unexpected exception in probe: {type(exc).__name__}: {exc}"
            traceback.print_exc()
        status = "PASS" if passed else "FAIL"
        if not passed:
            failures += 1
        print(f"{status}  {name}: {detail}")
    return failures


ALL_PROBES: List[Tuple[str, Callable[[], Tuple[bool, str]]]] = [
    ("R3-01 seed enumeration", probe_r3_01_seed_enumeration),
    ("R3-02 malformed relay goal", probe_r3_02_relay_goal),
    ("R3-03 malformed key_crate entities", probe_r3_03_key_crate_entities),
    ("R3-04 tampered invalid_actions", probe_r3_04_score_tamper),
    ("R4-01 non-bool success", probe_r4_01_success_type),
    ("R4-02 unknown score field", probe_r4_02_unknown_field),
    ("R4-03 missing entity locations", probe_r4_03_locations),
]


if __name__ == "__main__":
    failures = run_probes(ALL_PROBES)
    print(f"probe failures: {failures}")
    sys.exit(1 if failures else 0)
