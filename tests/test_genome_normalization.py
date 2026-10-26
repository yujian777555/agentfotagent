"""Normalization tests: inactive/duplicate values are canonicalized."""
from agentfotagent.genome.schema import (
    GENES,
    GenomeSpace,
    canonicalize_value,
    genome_hash,
    normalize_genome,
)


def test_alias_normalization_collapses_duplicates():
    a = normalize_genome({"planning_mode": "plan-first"})
    b = normalize_genome({"planning_mode": "plan_first"})
    c = normalize_genome({"planning_mode": "PLAN_FIRST"})
    assert a.planning_mode == b.planning_mode == c.planning_mode == "plan_first"


def test_boolean_collapse():
    on = normalize_genome({"memory_policy": True})
    off = normalize_genome({"memory_policy": False})
    assert on.memory_policy == "bounded_episodic"
    assert off.memory_policy == "none"


def test_missing_keys_fall_back_to_defaults():
    g = normalize_genome({})
    assert g.planning_mode == "direct"
    assert g.memory_policy == "none"
    assert g.verification_policy == "none"
    assert g.tool_selection_policy == "fixed_ranking"


def test_unknown_keys_rejected():
    try:
        normalize_genome({"planning_mode": "direct", "sneaky_gene": "on"})
    except KeyError:
        pass
    else:
        raise AssertionError("unknown gene key must be rejected")


def test_invalid_value_rejected():
    try:
        canonicalize_value("planning_mode", "telepathy")
    except ValueError:
        pass
    else:
        raise AssertionError("invalid allele must be rejected")


def test_genome_hash_stable_and_order_independent():
    g1 = normalize_genome(
        {
            "tool_selection_policy": "state_conditioned",
            "planning_mode": "plan_first",
            "memory_policy": "bounded_episodic",
            "verification_policy": "check_before_finalize",
        }
    )
    g2 = normalize_genome(
        {
            "planning_mode": "plan_first",
            "memory_policy": "bounded_episodic",
            "verification_policy": "check_before_finalize",
            "tool_selection_policy": "state_conditioned",
        }
    )
    assert genome_hash(g1) == genome_hash(g2)


def test_duplicate_allele_encoding_same_hash():
    g1 = normalize_genome({"verification_policy": "verify"})
    g2 = normalize_genome({"verification_policy": "check_before_finalize"})
    assert genome_hash(g1) == genome_hash(g2)


def test_genome_space_size_and_uniqueness(space):
    assert len(space) == 16
    hashes = space.all_hashes()
    assert len(set(hashes)) == 16


def test_neighbors_share_effective_search_space(space):
    g = normalize_genome({})
    neigh = space.neighbors(g)
    assert neigh
    space_hashes = set(space.effective_search_space_hashes())
    for n in neigh:
        assert genome_hash(n) in space_hashes
        # single-gene difference
        diffs = sum(1 for k in g.genes if g.genes[k] != n.genes[k])
        assert diffs == 1
