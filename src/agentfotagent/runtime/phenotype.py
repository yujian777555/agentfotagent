"""Genotype → phenotype compiler.

The phenotype is the compiled runtime behavior derived from a normalized genome:
- planning_mode        → whether an explicit plan action is emitted first;
- memory_policy        → bounded episodic retrieval over permitted observations;
- verification_policy  → check-before-finalization via the public verify_state tool;
- tool_selection_policy→ fixed deterministic tool ranking vs state-conditioned ranking.

Execution traces are recorded separately (evaluation.provenance.EpisodeTrace).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from ..genome.schema import Genome, normalize_genome
from ..interfaces import Action, Observation


MEMORY_WINDOW = 4  # fixed bound; not a gene (avoids budget confounds)

# Fixed ranking used by tool_selection_policy == "fixed_ranking".
FIXED_TOOL_RANK: Tuple[str, ...] = (
    "make_plan",
    "list_objects",
    "inspect",
    "read_note",
    "read_gauge",
    "read_offset_card",
    "move",
    "take",
    "unlock",
    "place",
    "set_dial",
    "activate_relay",
    "set_frequency",
    "verify_state",
    "submit",
)

# State-conditioned ranking prefers tools that are relevant to the current situation.
# Order inside each ranking is the preference under tool_selection_policy=state_conditioned.
STATE_CONDITIONED_RANK_HINTS: Tuple[Tuple[str, Tuple[str, ...]], ...] = (
    ("holding_key_unlockable", ("unlock", "take", "move", "inspect", "submit")),
    ("in_room_with_notes", ("read_note", "inspect", "move", "submit")),
    ("dials_unsolved", ("read_offset_card", "read_gauge", "set_dial", "submit")),
    ("relay_ready", ("activate_relay", "set_frequency", "submit")),
    ("artifact_on_surface", ("verify_state", "submit")),
    ("default", ("take", "inspect", "move", "list_objects", "submit")),
)


@dataclass
class Phenotype:
    """Compiled executable behavior derived from a genome."""

    genome: Genome
    memory_window: int = MEMORY_WINDOW
    planned: bool = False
    verified: bool = False
    memory: List[Mapping[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.genome = (
            self.genome
            if isinstance(self.genome, Genome)
            else normalize_genome(self.genome)  # type: ignore[arg-type]
        )

    # -- planning ----------------------------------------------------------

    def should_plan_first(self) -> bool:
        return self.genome.planning_mode == "plan_first" and not self.planned

    def mark_planned(self) -> None:
        self.planned = True

    # -- memory ------------------------------------------------------------

    def remember(self, observation: Mapping[str, Any]) -> None:
        if self.genome.memory_policy != "bounded_episodic":
            return
        self.memory.append(dict(observation))
        if len(self.memory) > self.memory_window:
            self.memory = self.memory[-self.memory_window :]

    def recall(self) -> List[Mapping[str, Any]]:
        if self.genome.memory_policy != "bounded_episodic":
            return []
        return list(self.memory)

    # -- verification ------------------------------------------------------

    def should_verify_before_finalize(self) -> bool:
        return self.genome.verification_policy == "check_before_finalize" and not self.verified

    def mark_verified(self) -> None:
        self.verified = True

    # -- tool ranking ------------------------------------------------------

    def rank_tools(self, observation: Mapping[str, Any], situation: str = "default") -> Tuple[str, ...]:
        if self.genome.tool_selection_policy == "fixed_ranking":
            return FIXED_TOOL_RANK
        for key, ranking in STATE_CONDITIONED_RANK_HINTS:
            if key == situation:
                return ranking
        return STATE_CONDITIONED_RANK_HINTS[-1][1]

    def prefers_tool(self, situation: str, tool: str) -> bool:
        ranking = self.rank_tools({}, situation=situation)
        return tool in ranking[:3]

    def compiled_summary(self) -> Dict[str, Any]:
        return {
            "planning_mode": self.genome.planning_mode,
            "memory_policy": self.genome.memory_policy,
            "memory_window": self.memory_window,
            "verification_policy": self.genome.verification_policy,
            "tool_selection_policy": self.genome.tool_selection_policy,
        }


def compile_phenotype(genome: Genome | Mapping[str, Any]) -> Phenotype:
    if not isinstance(genome, Genome):
        genome = normalize_genome(genome)
    return Phenotype(genome=genome)
