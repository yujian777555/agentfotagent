"""Contracts for task environments, Agent backends, phenotype execution and evaluation.

These interfaces are the freeze surface between the genome/runtime, the tool-use
world, the evaluator and the search baselines. Implementations must keep the
boundaries in docs/OWN_EXPERIMENTAL_ENVIRONMENT_SPEC.md.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

# Backward-compatible alias removed: PublicTask split into RuntimeTask + TaskInstance.


# ---------------------------------------------------------------------------
# Actions and observations
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Action:
    """A single tool invocation proposed by an Agent runtime."""

    tool: str
    args: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {"tool": self.tool, "args": dict(self.args)}

    @staticmethod
    def from_dict(raw: Mapping[str, Any]) -> "Action":
        return Action(tool=str(raw["tool"]), args=dict(raw.get("args", {})))


@dataclass(frozen=True)
class Observation:
    """Public observation returned by the environment. Never contains hidden goals."""

    content: Mapping[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return dict(self.content)


@dataclass(frozen=True)
class StepResult:
    observation: Observation
    terminated: bool
    termination_reason: str
    info: Mapping[str, Any]


# ---------------------------------------------------------------------------
# Task views
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RuntimeTask:
    """Model-facing task payload.

    Contains only the instruction fields the Agent is permitted to see.
    ``runtime_id`` is an opaque token: it must not encode family, split or seed.
    Evaluation-side IDs, seeds, generator version, content hashes and hidden
    goals live exclusively on TaskInstance.
    """

    runtime_id: str
    description: str
    max_steps: int

    def to_payload(self) -> Dict[str, Any]:
        """Exact serialization sent to a backend together with observations."""
        return {
            "runtime_id": self.runtime_id,
            "description": self.description,
            "max_steps": self.max_steps,
        }


@dataclass(frozen=True)
class TaskInstance:
    """Full evaluation-side task record. Not exposed to the Agent runtime."""

    runtime: RuntimeTask
    family: str
    split: str
    hidden_goal: Mapping[str, Any]
    setup: Mapping[str, Any]
    seed: int
    generator_version: str
    content_hash: str
    task_id: str = ""  # evaluation-side ID (family/split/seed); never model-facing

    @property
    def eval_id(self) -> str:
        return self.task_id


# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------

class ToolEnvironment(ABC):
    """Deterministic multi-step tool-use world."""

    @abstractmethod
    def reset(self, task: TaskInstance) -> Observation:
        """Reset to the initial state of ``task``. Deterministic given the task."""

    @abstractmethod
    def step(self, action: Action) -> StepResult:
        """Apply one tool call. Invalid actions must fail closed without state change."""

    @abstractmethod
    def final_state(self) -> Mapping[str, Any]:
        """Return the terminal world state used by the evaluator."""

    @property
    @abstractmethod
    def current_public_view(self) -> Mapping[str, Any]:
        """Public state view; must never expose hidden goals."""


# ---------------------------------------------------------------------------
# Backends and runtime
# ---------------------------------------------------------------------------

class AgentBackend(ABC):
    """Model/backend interface. Phase-0 provides only MockBackend (engineering tests)."""

    backend_id: str = "abstract"

    @abstractmethod
    def propose(self, observation: Observation, context: Mapping[str, Any]) -> Action:
        """Propose the next action given the public observation and runtime context."""


class PhenotypeRuntime(ABC):
    """Compiled phenotype: planning, memory, verification and tool ranking behavior."""

    @abstractmethod
    def next_action(self, observation: Observation) -> Action:
        ...

    @abstractmethod
    def observe(self, observation: Observation, action: Action, result: StepResult) -> None:
        ...

    @abstractmethod
    def trace(self) -> Sequence[Mapping[str, Any]]:
        ...


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class EpisodeResult:
    """Scored outcome of one episode. Primary score comes from final environment state."""

    task_id: str
    genome_hash: str
    success: bool
    steps: int
    invalid_actions: int
    repeated_states: int
    termination_reason: str
    final_state_hash: str
    diagnostic: Mapping[str, Any] = field(default_factory=dict)


class Evaluator(ABC):
    @abstractmethod
    def evaluate(self, task: TaskInstance, final_state: Mapping[str, Any], trace: Sequence[Mapping[str, Any]]) -> EpisodeResult:
        """Derive success exclusively from ``final_state`` and the task's hidden goal.

        The Agent's self-report in ``trace`` must not affect ``success``.
        """


# ---------------------------------------------------------------------------
# Search algorithms
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SearchRecord:
    genome: Mapping[str, Any]
    genome_hash: str
    task_ids: Tuple[str, ...]
    successes: int
    total: int
    success_rate: float
    episode_results: Tuple[EpisodeResult, ...]


class SearchAlgorithm(ABC):
    """Same-interface contract for random search and conventional EA baselines."""

    name: str = "abstract"

    @abstractmethod
    def run(self, evaluate_genome, budget: int) -> List[SearchRecord]:
        """``evaluate_genome`` must be the shared evaluator path for every algorithm."""
