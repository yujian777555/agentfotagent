"""Conventional evolutionary baseline (small (mu+lambda) ES) over the same space.

This is a standard baseline skeleton, not a new research algorithm.
"""
from __future__ import annotations

import random
from typing import Callable, List

from ..genome.schema import Genome, GenomeSpace, normalize_genome
from ..interfaces import SearchAlgorithm, SearchRecord


class ConventionalEA(SearchAlgorithm):
    name = "conventional_ea"

    def __init__(
        self,
        space: GenomeSpace,
        seed: int = 0,
        mu: int = 4,
        lam: int = 4,
    ) -> None:
        self.space = space
        self.seed = seed
        self.mu = max(1, mu)
        self.lam = max(1, lam)

    def run(self, evaluate_genome: Callable[[Genome], SearchRecord], budget: int) -> List[SearchRecord]:
        rng = random.Random(self.seed)
        records: List[SearchRecord] = []
        if budget <= 0:
            return records

        population: List[SearchRecord] = []
        for _ in range(min(self.mu, budget)):
            rec = evaluate_genome(self.space.sample(rng))
            population.append(rec)
            records.append(rec)

        while len(records) < budget:
            parents: List[SearchRecord] = []
            for _ in range(self.lam):
                if len(records) >= budget:
                    break
                if len(population) >= 2:
                    a = population[int(rng.randrange(len(population)))]
                    b = population[int(rng.randrange(len(population)))]
                    parent = a if a.success_rate >= b.success_rate else b
                else:
                    parent = population[0]
                parent_genome = normalize_genome(parent.genome)
                neighbors = self.space.neighbors(parent_genome)
                if not neighbors:
                    child = self.space.sample(rng)
                else:
                    child = neighbors[int(rng.randrange(len(neighbors)))]
                rec = evaluate_genome(child)
                records.append(rec)
                parents.append(rec)

            if not parents:
                break
            # (mu+lambda) truncation selection.
            combined = population + parents
            combined.sort(key=lambda r: r.success_rate, reverse=True)
            population = combined[: self.mu]

        return records
