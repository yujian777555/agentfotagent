"""Canonical, versioned Agent genome schema and normalization.

Candidate genes (design proposals frozen for Phase-0 engineering tests only):

1. planning_mode: direct vs plan-first
2. memory_policy: no carry-over vs bounded episodic retrieval
3. verification_policy: no verification vs check-before-finalization
4. tool_selection_policy: fixed deterministic ranking vs state/goal-conditioned ranking

A gene is admissible only if an intervention test shows that changing it changes
the intended runtime behavior, and normalization collapses inactive/duplicate values.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple


GENOME_SCHEMA_VERSION = "aes-genome-v1"

# Canonical alleles per gene. Normalization maps aliases onto these strings.
GENES: Dict[str, Tuple[str, ...]] = {
    "planning_mode": ("direct", "plan_first"),
    "memory_policy": ("none", "bounded_episodic"),
    "verification_policy": ("none", "check_before_finalize"),
    "tool_selection_policy": ("fixed_ranking", "state_conditioned"),
}

DEFAULT_ALLELE = {
    "planning_mode": "direct",
    "memory_policy": "none",
    "verification_policy": "none",
    "tool_selection_policy": "fixed_ranking",
}

# Aliases are canonicalized so inactive/duplicate encodings collapse.
_ALIASES: Dict[str, Dict[str, str]] = {
    "planning_mode": {
        "direct": "direct",
        "direct_execution": "direct",
        "none": "direct",
        "plan_first": "plan_first",
        "plan-first": "plan_first",
        "planfirst": "plan_first",
        "explicit_plan": "plan_first",
    },
    "memory_policy": {
        "none": "none",
        "no_carry_over": "none",
        "off": "none",
        "bounded_episodic": "bounded_episodic",
        "bounded-episodic": "bounded_episodic",
        "episodic": "bounded_episodic",
        "on": "bounded_episodic",
    },
    "verification_policy": {
        "none": "none",
        "off": "none",
        "no_verification": "none",
        "check_before_finalize": "check_before_finalize",
        "check-before-finalize": "check_before_finalize",
        "verify": "check_before_finalize",
        "on": "check_before_finalize",
    },
    "tool_selection_policy": {
        "fixed_ranking": "fixed_ranking",
        "fixed": "fixed_ranking",
        "static": "fixed_ranking",
        "state_conditioned": "state_conditioned",
        "state-conditioned": "state_conditioned",
        "adaptive": "state_conditioned",
    },
}


def canonicalize_value(gene: str, value: Any) -> str:
    if gene not in GENES:
        raise KeyError(f"unknown gene: {gene}")
    if isinstance(value, bool):
        # Boolean collapse: True → the non-default 'on' allele where applicable.
        value = "on" if value else "off"
    key = str(value).strip().lower()
    aliases = _ALIASES[gene]
    if key not in aliases:
        raise ValueError(f"invalid value {value!r} for gene {gene}")
    canonical = aliases[key]
    assert canonical in GENES[gene]
    return canonical


@dataclass(frozen=True)
class Genome:
    """Normalized agent genotype. Immutable once constructed via ``normalize_genome``."""

    planning_mode: str
    memory_policy: str
    verification_policy: str
    tool_selection_policy: str
    schema_version: str = GENOME_SCHEMA_VERSION

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "planning_mode": self.planning_mode,
            "memory_policy": self.memory_policy,
            "verification_policy": self.verification_policy,
            "tool_selection_policy": self.tool_selection_policy,
        }

    @property
    def genes(self) -> Dict[str, str]:
        return {
            "planning_mode": self.planning_mode,
            "memory_policy": self.memory_policy,
            "verification_policy": self.verification_policy,
            "tool_selection_policy": self.tool_selection_policy,
        }


def normalize_genome(raw: Mapping[str, Any] | Genome | Any) -> Genome:
    """Canonicalize a genome mapping (or pass through an already-normalized Genome).

    - unknown keys are rejected (no silent genes);
    - values are alias-normalized and deduplicated;
    - missing keys fall back to the fixed default allele;
    - duplicate gene entries after alias collapse are identical by construction.
    """
    if isinstance(raw, Genome):
        return raw
    if not isinstance(raw, Mapping):
        raise TypeError("genome must be a mapping or Genome")

    known = set(GENES)
    provided = {k for k in raw.keys() if k != "schema_version"}
    unknown = provided - known
    if unknown:
        raise KeyError(f"unknown genome keys: {sorted(unknown)}")

    normalized: Dict[str, str] = {}
    for gene in GENES:
        if gene in raw and raw[gene] is not None:
            normalized[gene] = canonicalize_value(gene, raw[gene])
        else:
            normalized[gene] = DEFAULT_ALLELE[gene]
    return Genome(**normalized)


def genome_hash(genome: Genome | Mapping[str, Any]) -> str:
    """Stable content hash of the normalized genome."""
    if not isinstance(genome, Genome):
        genome = normalize_genome(genome)
    payload = json.dumps(genome.to_dict(), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class GenomeSpace:
    """Exact finite search space shared by every baseline algorithm."""

    def __init__(self) -> None:
        self._values: List[Genome] = []
        # Cartesian product in fixed gene order → reproducible enumeration.
        for pm in GENES["planning_mode"]:
            for mp in GENES["memory_policy"]:
                for vp in GENES["verification_policy"]:
                    for tp in GENES["tool_selection_policy"]:
                        self._values.append(
                            normalize_genome(
                                {
                                    "planning_mode": pm,
                                    "memory_policy": mp,
                                    "verification_policy": vp,
                                    "tool_selection_policy": tp,
                                }
                            )
                        )

    def __len__(self) -> int:
        return len(self._values)

    def __iter__(self):
        return iter(self._values)

    def all_genomes(self) -> List[Genome]:
        return list(self._values)

    def all_hashes(self) -> List[str]:
        return [genome_hash(g) for g in self._values]

    def sample(self, rng) -> Genome:
        return self._values[int(rng.randrange(len(self._values)))]

    def neighbors(self, genome: Genome) -> List[Genome]:
        """Single-gene mutants (conventional EA variation over the same space)."""
        out: List[Genome] = []
        for gene, alleles in GENES.items():
            for allele in alleles:
                if allele == genome.genes[gene]:
                    continue
                raw = dict(genome.genes)
                raw[gene] = allele
                out.append(normalize_genome(raw))
        return out

    def effective_search_space_hashes(self) -> List[str]:
        """Canonical hash list; used by fairness tests to prove shared search space."""
        return sorted(set(self.all_hashes()))
