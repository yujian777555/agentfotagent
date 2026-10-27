"""R1-05 regression: bidirectional reconstruction completeness and run-scoped isolation."""
import copy
import json

import pytest

from agentfotagent.evaluation.evaluator import StateBasedEvaluator
from agentfotagent.evaluation.provenance import ReconstructionError, reconstruct_from_artifacts
from agentfotagent.evolution.conventional_ea import ConventionalEA
from agentfotagent.evolution.harness import BaselineHarness
from agentfotagent.evolution.random_search import RandomSearch
from agentfotagent.genome.schema import GenomeSpace
from agentfotagent.tasks.generators import generate_task

from conftest import make_genome


def _tasks():
    return [
        generate_task("dial_set", 1, "train"),
        generate_task("dial_set", 2, "train"),
    ]


def _run_and_reload(harness, algorithm, budget=3):
    artifact = harness.run_and_collect(algorithm, budget)
    return artifact, json.loads(json.dumps(artifact, sort_keys=True, default=str))


def test_every_score_has_trace_and_every_trace_has_score():
    tasks = _tasks()
    task_map = {t.task_id: t for t in tasks}
    space = GenomeSpace()
    harness = BaselineHarness(tasks=tasks, space=space, config={"protocol": "r1-05"})
    artifact, reloaded = _run_and_reload(harness, RandomSearch(space, seed=1), budget=3)

    traces = reloaded["traces"]
    scores = reloaded["manifest"]["scores"]
    assert len(traces) == len(scores)
    rebuilt = reconstruct_from_artifacts(reloaded, task_map, StateBasedEvaluator())
    assert rebuilt["trace_count"] == rebuilt["score_count"] == len(scores)
    assert rebuilt["mismatches"] == []


def test_missing_trace_is_an_error():
    tasks = _tasks()
    task_map = {t.task_id: t for t in tasks}
    space = GenomeSpace()
    harness = BaselineHarness(tasks=tasks, space=space, config={"protocol": "r1-05-drop"})
    artifact, reloaded = _run_and_reload(harness, RandomSearch(space, seed=2), budget=3)

    reloaded["traces"] = reloaded["traces"][:-1]  # drop one trace, keep scores
    with pytest.raises(ReconstructionError):
        reconstruct_from_artifacts(reloaded, task_map, StateBasedEvaluator())


def test_extra_score_without_trace_is_an_error():
    tasks = _tasks()
    task_map = {t.task_id: t for t in tasks}
    space = GenomeSpace()
    harness = BaselineHarness(tasks=tasks, space=space, config={"protocol": "r1-05-extra"})
    artifact, reloaded = _run_and_reload(harness, RandomSearch(space, seed=3), budget=2)

    extra = dict(reloaded["manifest"]["scores"][0])
    extra["final_state_hash"] = "deadbeef-not-a-trace"
    extra["genome_hash"] = "ghost-genome"
    reloaded["manifest"]["scores"].append(extra)
    with pytest.raises(ReconstructionError):
        reconstruct_from_artifacts(reloaded, task_map, StateBasedEvaluator())


def test_hash_mismatch_is_an_error():
    tasks = _tasks()
    task_map = {t.task_id: t for t in tasks}
    space = GenomeSpace()
    harness = BaselineHarness(tasks=tasks, space=space, config={"protocol": "r1-05-hash"})
    artifact, reloaded = _run_and_reload(harness, RandomSearch(space, seed=4), budget=2)

    # Tamper with a score success flag so rebuild disagrees.
    reloaded["manifest"]["scores"][0]["success"] = not reloaded["manifest"]["scores"][0]["success"]
    with pytest.raises(ReconstructionError):
        reconstruct_from_artifacts(reloaded, task_map, StateBasedEvaluator())


def test_second_run_does_not_mix_first_run_traces_or_accounting():
    tasks = _tasks()
    space = GenomeSpace()
    harness = BaselineHarness(tasks=tasks, space=space, config={"protocol": "r1-05-reuse"})

    art1 = harness.run_and_collect(RandomSearch(space, seed=1), budget=3)
    traces1 = list(art1["traces"])
    acc1 = dict(art1["accounting"])

    art2 = harness.run_and_collect(ConventionalEA(space, seed=2, mu=2, lam=2), budget=3)
    traces2 = art2["traces"]
    acc2 = dict(art2["accounting"])

    # Run 2 artifacts must not contain run 1 traces.
    ids1 = {(t["task_id"], t["genome_hash"]) for t in traces1}
    ids2 = {(t["task_id"], t["genome_hash"]) for t in traces2}
    # Overlap is allowed only if the same genome was re-evaluated in run 2,
    # but run 2's accounting/trace list must be rebuilt from run 2 only.
    assert art2["run_id"] != art1["run_id"]
    assert acc2["candidate_proposals"] == 3  # not cumulative with run 1
    assert acc1["candidate_proposals"] == 3
    # Accounting resets: run2 actual episodes must not include run1 count.
    assert acc2["actual_episode_executions"] <= len(tasks) * 3
    # Each artifact reconstructs independently against its own traces/scores.
    task_map = {t.task_id: t for t in tasks}
    r1 = reconstruct_from_artifacts(
        json.loads(json.dumps(art1, default=str)), task_map, StateBasedEvaluator()
    )
    r2 = reconstruct_from_artifacts(
        json.loads(json.dumps(art2, default=str)), task_map, StateBasedEvaluator()
    )
    assert r1["mismatches"] == [] and r2["mismatches"] == []
    assert r1["trace_count"] == len(art1["traces"])
    assert r2["trace_count"] == len(art2["traces"])


def test_begin_run_resets_trace_store():
    tasks = _tasks()
    space = GenomeSpace()
    harness = BaselineHarness(tasks=tasks, space=space, config={"protocol": "r1-05-reset"})
    harness.begin_run("a")
    harness.evaluate_genome(make_genome())
    assert harness.trace_store
    assert harness.accounting.actual_episode_executions > 0

    harness.begin_run("b")
    assert harness.trace_store == {}
    assert harness.accounting.actual_episode_executions == 0
    assert harness.accounting.candidate_proposals == 0
    assert harness._seen_genome_hashes == set()


def test_manifest_records_source_and_versions():
    tasks = _tasks()
    space = GenomeSpace()
    harness = BaselineHarness(tasks=tasks, space=space, config={"protocol": "r1-05-ver"})
    art = harness.run_and_collect(RandomSearch(space, seed=5), budget=2)
    assert art["manifest"]["environment_version"] == "aes-tool-world-v2"
    assert art["manifest"]["evaluator_version"] == "aes-evaluator-v2"
    assert art["backend_id"] == "mock-engineering-v2"
    assert art["manifest"].get("source_commit_sha")
