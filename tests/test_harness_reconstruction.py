"""F4 regression: search-run artifacts preserve actual traces and rebuild scores end to end."""
import json

from agentfotagent.evaluation.evaluator import StateBasedEvaluator
from agentfotagent.evaluation.provenance import (
    EpisodeTrace,
    reconstruct_from_artifacts,
    reconstruct_scores,
)
from agentfotagent.evolution.conventional_ea import ConventionalEA
from agentfotagent.evolution.harness import BaselineHarness
from agentfotagent.evolution.random_search import RandomSearch
from agentfotagent.genome.schema import GenomeSpace, genome_hash
from agentfotagent.tasks.generators import generate_task

from conftest import make_genome


def _tasks():
    return [
        generate_task("dial_set", 1, "train"),
        generate_task("dial_set", 2, "train"),
    ]


def test_harness_retains_actual_episode_traces():
    tasks = _tasks()
    space = GenomeSpace()
    harness = BaselineHarness(tasks=tasks, space=space, config={"protocol": "phase0-r1"})
    g = make_genome()
    harness.evaluate_genome(g)

    assert harness.trace_store
    for trace in harness.trace_store.values():
        # Real traces have per-step records and a full final state.
        assert isinstance(trace, EpisodeTrace)
        assert trace.steps, "actual trace must contain steps"
        assert trace.final_state is not None
        assert "objects" in trace.final_state
        assert "dials" in trace.final_state
        assert trace.split == "train"
        assert trace.termination_reason


def test_manifest_uses_actual_traces_and_best_genome():
    tasks = _tasks()
    space = GenomeSpace()
    harness = BaselineHarness(tasks=tasks, space=space, config={"protocol": "phase0-r1"})
    records = []
    for g in (
        make_genome(),  # often weaker
        make_genome(
            planning_mode="plan_first",
            memory_policy="bounded_episodic",
            verification_policy="check_before_finalize",
            tool_selection_policy="state_conditioned",
        ),
        make_genome(verification_policy="check_before_finalize"),
    ):
        records.append(harness.evaluate_genome(g))

    manifest = harness.build_manifest("random_search", 7, records)
    d = manifest.to_dict()

    best = max(records, key=lambda r: (r.success_rate, r.successes, r.genome_hash))
    assert d["genome_hash"] == best.genome_hash
    assert d["scores"], "manifest must record per-episode scores"
    assert d["accounting"].get("actual_episode_executions", 0) > 0

    # Traces referenced in the manifest are the actual stored ones with full state.
    stored = harness.actual_traces()
    assert stored
    for tr in stored:
        assert len(tr.final_state.keys()) > 2  # not just step/termination_reason


def test_end_to_end_random_search_reconstruction():
    tasks = _tasks()
    task_map = {t.task_id: t for t in tasks}
    space = GenomeSpace()
    harness = BaselineHarness(tasks=tasks, space=space, config={"protocol": "phase0-r1"})
    rs = RandomSearch(space, seed=3)
    artifact = harness.run_and_collect(rs, budget=4)

    # Serialize / reload (round-trip through JSON).
    blob = json.dumps(artifact, sort_keys=True, default=str)
    reloaded = json.loads(blob)

    assert reloaded["traces"], "serialized artifact must include actual traces"
    assert reloaded["manifest"]["scores"]
    assert reloaded["accounting"]["candidate_proposals"] >= 1

    rebuilt = reconstruct_from_artifacts(
        reloaded, task_map, StateBasedEvaluator()
    )
    assert rebuilt["mismatches"] == []
    assert len(rebuilt["rebuilt"]) == len(reloaded["traces"])

    # Direct reconstruction agrees too.
    traces = [EpisodeTrace.from_dict(t) for t in reloaded["traces"]]
    direct = reconstruct_scores(traces, task_map, StateBasedEvaluator())
    assert [r.success for r in direct] == [r.success for r in rebuilt["rebuilt"]]
    assert [r.final_state_hash for r in direct] == [
        r.final_state_hash for r in rebuilt["rebuilt"]
    ]


def test_end_to_end_ea_reconstruction():
    tasks = _tasks()
    task_map = {t.task_id: t for t in tasks}
    space = GenomeSpace()
    harness = BaselineHarness(tasks=tasks, space=space, config={"protocol": "phase0-r1"})
    ea = ConventionalEA(space, seed=4, mu=2, lam=2)
    artifact = harness.run_and_collect(ea, budget=4)
    reloaded = json.loads(json.dumps(artifact, sort_keys=True, default=str))
    rebuilt = reconstruct_from_artifacts(reloaded, task_map, StateBasedEvaluator())
    assert rebuilt["mismatches"] == []
    # Hashes recorded in the manifest match rebuilt hashes.
    recorded_hashes = {
        (s["task_id"], s["genome_hash"], s["final_state_hash"])
        for s in reloaded["manifest"]["scores"]
    }
    for r in rebuilt["rebuilt"]:
        assert (r.task_id, r.genome_hash, r.final_state_hash) in recorded_hashes


def test_accounting_counts_proposals_unique_cache_and_episodes():
    tasks = _tasks()
    space = GenomeSpace()
    harness = BaselineHarness(tasks=tasks, space=space, config={"protocol": "phase0-r1"})
    g = make_genome()
    harness.evaluate_genome(g)
    harness.evaluate_genome(g)  # second call should hit cache

    acc = harness.accounting.to_dict()
    assert acc["candidate_proposals"] == 2
    assert acc["unique_genomes"] == 1
    assert acc["cache_hits"] == len(tasks)
    assert acc["actual_episode_executions"] == len(tasks)
    assert acc["task_evaluations"] == 2 * len(tasks)
