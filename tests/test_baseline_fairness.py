"""Baseline fairness tests: random search and conventional EA share the same
effective search space and evaluation path."""
from agentfotagent.evolution.conventional_ea import ConventionalEA
from agentfotagent.evolution.harness import BaselineHarness
from agentfotagent.evolution.random_search import RandomSearch
from agentfotagent.genome.schema import GenomeSpace, genome_hash
from agentfotagent.runtime.cache import EvaluationCache
from agentfotagent.tasks.generators import generate_task

from conftest import make_genome


def _small_tasks():
    return [
        generate_task("dial_set", 1, "train"),
        generate_task("dial_set", 2, "train"),
    ]


def test_shared_search_space_hashes(space):
    rs = RandomSearch(space, seed=1)
    ea = ConventionalEA(space, seed=1)
    assert rs.space is ea.space
    assert rs.space.effective_search_space_hashes() == space.effective_search_space_hashes()
    assert len(space.effective_search_space_hashes()) == 16


def test_algorithms_use_identical_evaluator_path():
    space = GenomeSpace()
    tasks = _small_tasks()
    harness = BaselineHarness(tasks=tasks, space=space, config={"protocol": "test"})

    calls = []
    original = harness.evaluate_genome

    def counting(genome):
        calls.append(genome_hash(genome) if not isinstance(genome, dict) else genome_hash(genome))
        return original(genome)

    # Both algorithms must only call harness.evaluate_genome.
    rs = RandomSearch(space, seed=0)
    ea = ConventionalEA(space, seed=0, mu=2, lam=2)

    rs_records = rs.run(counting, budget=3)
    rs_calls = list(calls)
    calls.clear()
    ea_records = ea.run(counting, budget=3)
    ea_calls = list(calls)

    assert rs_calls and ea_calls
    # Every evaluated genome hash is from the shared space.
    space_hashes = set(space.effective_search_space_hashes())
    for h in rs_calls + ea_calls:
        assert h in space_hashes

    # Results were produced by the same SearchRecord interface.
    assert all(r.total == len(tasks) for r in rs_records)
    assert all(r.total == len(tasks) for r in ea_records)


def test_same_genome_same_score_regardless_of_algorithm():
    space = GenomeSpace()
    tasks = _small_tasks()
    harness_a = BaselineHarness(tasks=tasks, space=space, config={"protocol": "test"})
    harness_b = BaselineHarness(tasks=tasks, space=space, config={"protocol": "test"})

    g = make_genome(planning_mode="plan_first")
    rec_a = harness_a.evaluate_genome(g)
    rec_b = harness_b.evaluate_genome(g)

    assert rec_a.genome_hash == rec_b.genome_hash
    assert rec_a.success_rate == rec_b.success_rate
    assert rec_a.successes == rec_b.successes
    assert [r.success for r in rec_a.episode_results] == [r.success for r in rec_b.episode_results]


def test_budget_respected():
    space = GenomeSpace()
    tasks = _small_tasks()
    harness = BaselineHarness(tasks=tasks, space=space, config={"protocol": "test"})
    rs = RandomSearch(space, seed=1)
    ea = ConventionalEA(space, seed=1, mu=2, lam=3)
    assert len(rs.run(harness.evaluate_genome, budget=5)) == 5
    assert len(ea.run(harness.evaluate_genome, budget=5)) == 5


def test_max_steps_shared_across_methods():
    """Budget confound guard: max interaction limit is task-fixed, not genome-set."""
    task = generate_task("key_crate", 1, "train")
    assert task.public.max_steps == 24
    g_best = make_genome(
        planning_mode="plan_first",
        memory_policy="bounded_episodic",
        verification_policy="check_before_finalize",
        tool_selection_policy="state_conditioned",
    )
    g_worst = make_genome()
    assert task.public.max_steps == 24  # independent of genome
    from agentfotagent.runtime.mock_backend import run_episode

    _, tr_best, _ = run_episode(task, g_best, seed=1)
    _, tr_worst, _ = run_episode(task, g_worst, seed=1)
    # Neither genome receives a larger step budget.
    assert len(tr_best.steps) <= task.public.max_steps
    assert len(tr_worst.steps) <= task.public.max_steps
