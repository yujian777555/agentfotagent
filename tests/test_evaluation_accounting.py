"""C1 regression: evaluation accounting distinguishes proposals, unique genomes,
cache hits and actual episode executions.

Budget meaning for Phase-0 (documented, not a scientific comparison yet):
- candidate_proposals: genomes handed to the shared evaluator
- unique_genomes: distinct genome hashes proposed
- cache_hits: task-level scores served from cache (not new episodes)
- actual_episode_executions: uncached environment episodes actually run
"""
from agentfotagent.evolution.conventional_ea import ConventionalEA
from agentfotagent.evolution.harness import BaselineHarness
from agentfotagent.evolution.random_search import RandomSearch
from agentfotagent.genome.schema import GenomeSpace
from agentfotagent.tasks.generators import generate_task

from conftest import make_genome


def test_duplicate_genome_hits_cache_not_episode():
    tasks = [generate_task("dial_set", 1, "train")]
    space = GenomeSpace()
    harness = BaselineHarness(tasks=tasks, space=space, config={"protocol": "c1"})
    g = make_genome()
    harness.evaluate_genome(g)
    harness.evaluate_genome(g)
    harness.evaluate_genome(g)

    acc = harness.accounting.to_dict()
    assert acc["candidate_proposals"] == 3
    assert acc["unique_genomes"] == 1
    assert acc["actual_episode_executions"] == 1
    assert acc["cache_hits"] == 2
    assert acc["task_evaluations"] == 3


def test_random_search_and_ea_report_accounting():
    tasks = [
        generate_task("dial_set", 1, "train"),
        generate_task("dial_set", 2, "train"),
    ]
    space = GenomeSpace()
    h1 = BaselineHarness(tasks=tasks, space=space, config={"protocol": "c1-rs"})
    rs = RandomSearch(space, seed=1)
    artifact_rs = h1.run_and_collect(rs, budget=5)

    h2 = BaselineHarness(tasks=tasks, space=space, config={"protocol": "c1-ea"})
    ea = ConventionalEA(space, seed=1, mu=2, lam=2)
    artifact_ea = h2.run_and_collect(ea, budget=5)

    for art, label in ((artifact_rs, "rs"), (artifact_ea, "ea")):
        acc = art["accounting"]
        assert acc["candidate_proposals"] == 5, label
        assert acc["unique_genomes"] >= 1
        assert acc["actual_episode_executions"] + acc["cache_hits"] == acc["task_evaluations"]
        # Cached hits are not counted as new episodes.
        assert acc["actual_episode_executions"] <= acc["task_evaluations"]

    # Manifest carries accounting for the run record.
    assert artifact_rs["manifest"]["accounting"]["candidate_proposals"] == 5


def test_effective_budget_is_not_inflated_by_cache():
    """Repeated proposals of the same genome must not look like extra episodes."""
    tasks = [generate_task("key_crate", 1, "train")]
    space = GenomeSpace()
    harness = BaselineHarness(tasks=tasks, space=space, config={"protocol": "c1-eff"})
    g = make_genome()
    for _ in range(10):
        harness.evaluate_genome(g)
    acc = harness.accounting.to_dict()
    assert acc["candidate_proposals"] == 10
    assert acc["actual_episode_executions"] == 1
    assert acc["cache_hits"] == 9
