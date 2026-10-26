"""Random search baseline over the exact normalized genome space."""
from __future__ import annotations

import random
from typing import Callable, List

from ..genome.schema import Genome, GenomeSpace
from ..interfaces import SearchAlgorithm, SearchRecord


class RandomSearch(SearchAlgorithm):
    name = "random_search"

    def __init__(self, space: GenomeSpace, seed: int = 0) -> None:
        self.space = space
        self.seed = seed

    def run(self, evaluate_genome: Callable[[Genome], SearchRecord], budget: int) -> List[SearchRecord]:
        rng = random.Random(self.seed)
        records: List[SearchRecord] = []
        seen = set()
        for _ in range(max(0, budget)):
            genome = self.space.sample(rng)
            h = genome.genes  # cheap uniqueness via normalized genes tuple
            key = tuple(sorted(h.items()))
            rec = evaluate_genome(genome)
            records.append(rec)
            seen.add(key)
        return records
