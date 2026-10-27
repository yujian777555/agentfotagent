"""Provenance tests: scores can be reconstructed from raw traces and manifests."""
from agentfotagent.evaluation.evaluator import StateBasedEvaluator
from agentfotagent.evaluation.provenance import (
    EpisodeTrace,
    build_run_manifest,
    config_hash,
    reconstruct_scores,
)
from agentfotagent.environments.tool_world import ToolWorld
from agentfotagent.genome.schema import genome_hash
from agentfotagent.runtime.mock_backend import run_episode
from agentfotagent.tasks.generators import generate_task
from agentfotagent.tasks.manifests import manifest_hash, task_to_manifest_entry

from conftest import make_genome


def test_trace_contains_reconstruction_fields():
    task = generate_task("dial_set", 1, "train")
    g = make_genome(planning_mode="plan_first")
    ok, trace, payload = run_episode(task, g, seed=1)

    assert trace.task_id == task.task_id
    assert trace.seed == 1
    assert trace.genome_hash == genome_hash(g)
    assert trace.backend_id.startswith("mock")
    assert trace.final_state is not None
    assert trace.steps
    for step in trace.steps:
        assert "action" in step
        assert "observation" in step
        assert "state_hash" in step
        assert "valid" in step

    # Reconstruct score from trace alone.
    ev = StateBasedEvaluator(genome_hash=trace.genome_hash)
    rebuilt = ev.evaluate(task, trace.final_state, trace.steps)
    assert rebuilt.success == ok
    assert rebuilt.steps == payload["episode_result"].steps
    assert rebuilt.final_state_hash == payload["episode_result"].final_state_hash


def test_reconstruct_scores_matches_original():
    tasks = [generate_task("key_crate", 1, "train"), generate_task("key_crate", 2, "train")]
    g = make_genome()
    traces = []
    originals = []
    for t in tasks:
        ok, tr, payload = run_episode(t, g, seed=t.seed)
        traces.append(tr)
        originals.append(payload["episode_result"])

    task_map = {t.task_id: t for t in tasks}
    rebuilt = reconstruct_scores(traces, task_map, StateBasedEvaluator())
    assert [r.success for r in rebuilt] == [r.success for r in originals]
    assert [r.final_state_hash for r in rebuilt] == [r.final_state_hash for r in originals]


def test_run_manifest_records_provenance():
    task = generate_task("relay_route", 1, "held_out")
    g = make_genome()
    ok, tr, payload = run_episode(task, g, seed=1)
    config = {"protocol": "phase0", "backend": "mock-engineering-v1"}
    result = payload["episode_result"]

    manifest = build_run_manifest(
        run_id="test-run-1",
        algorithm="random_search",
        backend_id="mock-engineering-v1",
        seed=1,
        config=config,
        task_manifest_hash=manifest_hash([task_to_manifest_entry(task)]),
        genome_hash=genome_hash(g),
        environment_version="aes-tool-world-v1",
        evaluator_version="aes-evaluator-v1",
        generator_version=task.generator_version,
        max_steps=task.runtime.max_steps,
        episodes=[tr],
        results=[result],
        engineering_only=True,
    )
    d = manifest.to_dict()
    assert d["seed"] == 1
    assert d["config_hash"] == config_hash(config)
    assert d["task_manifest_hash"]
    assert d["genome_hash"] == genome_hash(g)
    assert d["environment_version"]
    assert d["evaluator_version"]
    assert d["generator_version"]
    assert d["engineering_only"] is True
    assert d["scores"] and d["scores"][0]["task_id"] == task.task_id

    # Manifest scores match evaluator results.
    assert d["scores"][0]["success"] == result.success
    assert d["scores"][0]["final_state_hash"] == result.final_state_hash


def test_episode_trace_roundtrip():
    task = generate_task("dial_set", 2, "train")
    g = make_genome()
    _, tr, _ = run_episode(task, g, seed=2)
    raw = tr.to_dict()
    tr2 = EpisodeTrace.from_dict(raw)
    assert tr2.task_id == tr.task_id
    assert tr2.steps == tr.steps
    assert tr2.final_state == tr.final_state
    assert tr2.genome_hash == tr.genome_hash


def test_environment_state_hash_stable():
    task = generate_task("key_crate", 3, "train")
    env = ToolWorld()
    env.reset(task)
    h1 = StateBasedEvaluator().evaluate(task, env.final_state(), []).final_state_hash
    env2 = ToolWorld()
    env2.reset(task)
    h2 = StateBasedEvaluator().evaluate(task, env2.final_state(), []).final_state_hash
    assert h1 == h2
