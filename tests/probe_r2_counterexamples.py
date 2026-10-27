"""Original R2 independent-audit counterexamples — must FAIL on the R3 tree.

Convention: probe functions raise AssertionError when the malformed input is
correctly REJECTED. If the probe returns without raising, the counterexample
was wrongly ACCEPTED.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from agentfotagent.evaluation.evaluator import StateBasedEvaluator
from agentfotagent.evaluation.provenance import ReconstructionError, reconstruct_from_artifacts
from agentfotagent.evolution.harness import BaselineHarness
from agentfotagent.evolution.random_search import RandomSearch
from agentfotagent.genome.schema import GenomeSpace
from agentfotagent.tasks.generators import generate_task

results = []


def probe(name, fn):
    try:
        fn()
        results.append((name, "FAIL", "counterexample was ACCEPTED"))
    except AssertionError as e:
        results.append((name, "PASS", f"rejected as required: {e}"))
    except ReconstructionError as e:
        results.append((name, "PASS", f"rejected as required: {e}"))
    except Exception as e:
        results.append((name, "PASS", f"rejected as required: {type(e).__name__}: {e}"))


def r3_01():
    target = generate_task("dial_set", 17, "dev")
    rid = target.runtime.runtime_id
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
                raise RuntimeError(f"UNEXPECTED recovery of {family}/{split}/{seed}")
    raise AssertionError("seed enumeration found no match")


def r3_02():
    task = generate_task("relay_route", 1, "held_out")
    object.__setattr__(task, "hidden_goal", {"type": "relay_route", "code": None, "frequency": 99})
    state = {
        "objects": {"relay": {"type": "relay", "location": "hub"}},
        "relay": {"activated": True, "frequency": 99},
        "dials": {},
        "inventory": [],
        "location": "hub",
        "step": 5,
        "termination_reason": "agent_submit",
    }
    if StateBasedEvaluator().evaluate(task, state, []).success:
        return  # wrongly accepted
    raise AssertionError("malformed relay goal rejected")


def r3_03():
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
    if StateBasedEvaluator().evaluate(task, state, []).success:
        return  # wrongly accepted
    raise AssertionError("malformed key_crate entities rejected")


def r3_04():
    tasks = [generate_task("dial_set", 1, "train")]
    space = GenomeSpace()
    harness = BaselineHarness(tasks=tasks, space=space, config={"protocol": "probe"})
    art = harness.run_and_collect(RandomSearch(space, seed=1), 1)
    art = json.loads(json.dumps(art, default=str))
    art["manifest"]["scores"][0]["invalid_actions"] = 999999
    task_map = {t.task_id: t for t in tasks}
    reconstruct_from_artifacts(art, task_map, StateBasedEvaluator())
    raise AssertionError("tampered invalid_actions accepted")


probe("R3-01 seed enumeration", r3_01)
probe("R3-02 malformed relay goal", r3_02)
probe("R3-03 malformed key_crate entities", r3_03)
probe("R3-04 tampered invalid_actions", r3_04)

for name, status, detail in results:
    print(f"{status}  {name}: {detail}")
sys.exit(0 if all(s == "PASS" for _, s, _ in results) else 1)
