"""Source-domain allele prior (surrogate) and transfer application.

This is a pilot transfer object. It is NOT MetaBox-v2 and is not a research
contribution. Weights bias mutation in the conventional EA toward alleles that
the surrogate source landscape prefers.
"""
from __future__ import annotations

import random
from typing import Dict, Mapping

from ..genome.schema import GENES, Genome, GenomeSpace, normalize_genome


# Surrogate source landscape preference (higher = preferred).
# Values are fixed for reproducibility of the pilot; they are not fitted to AES outcomes.
SOURCE_ALLELE_WEIGHTS: Dict[str, Dict[str, float]] = {
    "planning_mode": {"direct": 0.35, "plan_first": 0.85},
    "memory_policy": {"none": 0.40, "bounded_episodic": 0.80},
    "verification_policy": {"none": 0.30, "check_before_finalize": 0.90},
    "tool_selection_policy": {"fixed_ranking": 0.45, "state_conditioned": 0.75},
}


def shuffled_weights(rng: random.Random, base: Mapping[str, Mapping[str, float]] | None = None):
    """Negative control: permute allele labels within each gene."""
    base = base or SOURCE_ALLELE_WEIGHTS
    out: Dict[str, Dict[str, float]] = {}
    for gene, alleles in base.items():
        names = list(alleles.keys())
        values = list(alleles.values())
        rng.shuffle(values)
        out[gene] = dict(zip(names, values))
    return out


def biased_mutate(
    parent: Genome,
    space: GenomeSpace,
    weights: Mapping[str, Mapping[str, float]],
    rng: random.Random,
) -> Genome:
    """Pick one gene to flip; flip toward the higher-weight allele when possible."""
    neighbors = space.neighbors(parent)
    if not neighbors:
        return parent
    # Score each neighbor by total weight delta.
    def score(n: Genome) -> float:
        total = 0.0
        for gene, allele in n.genes.items():
            total += float(weights.get(gene, {}).get(allele, 0.0))
        return total

    # Stochastic: sample one neighbor with probability proportional to max(score,eps).
    scores = [score(n) + 1e-6 for n in neighbors]
    total = sum(scores)
    r = rng.random() * total
    acc = 0.0
    for n, s in zip(neighbors, scores):
        acc += s
        if r <= acc:
            return n
    return neighbors[-1]
