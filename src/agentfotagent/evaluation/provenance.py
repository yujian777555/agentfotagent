"""Execution traces, run manifests and score reconstruction.

Every run records enough provenance (seed, config hash, task-manifest hash,
genome hash, backend id) that evaluation results can be rebuilt from raw
trajectories and manifests alone.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from ..interfaces import EpisodeResult, TaskInstance


def config_hash(config: Mapping[str, Any]) -> str:
    payload = json.dumps(config, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass
class EpisodeTrace:
    """Full execution trace for one episode."""

    task_id: str
    split: str
    genome_hash: str
    backend_id: str
    seed: int
    steps: List[Dict[str, Any]] = field(default_factory=list)
    final_state: Dict[str, Any] = field(default_factory=dict)
    termination_reason: str = ""
    self_report_success: Optional[bool] = None

    def append_step(
        self,
        *,
        step_index: int,
        observation: Mapping[str, Any],
        action: Mapping[str, Any],
        info: Mapping[str, Any],
        state_hash: str,
        valid: bool,
    ) -> None:
        self.steps.append(
            {
                "step_index": step_index,
                "observation": dict(observation),
                "action": dict(action),
                "info": dict(info),
                "state_hash": state_hash,
                "valid": valid,
                # Trace records self-reports for audit only; evaluator ignores them.
                "self_report_success": bool(
                    (info or {}).get("self_report_success", False)
                ),
            }
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "split": self.split,
            "genome_hash": self.genome_hash,
            "backend_id": self.backend_id,
            "seed": self.seed,
            "steps": self.steps,
            "final_state": self.final_state,
            "termination_reason": self.termination_reason,
            "self_report_success": self.self_report_success,
        }

    @staticmethod
    def from_dict(raw: Mapping[str, Any]) -> "EpisodeTrace":
        tr = EpisodeTrace(
            task_id=str(raw["task_id"]),
            split=str(raw.get("split", "")),
            genome_hash=str(raw.get("genome_hash", "")),
            backend_id=str(raw.get("backend_id", "")),
            seed=int(raw.get("seed", 0)),
            steps=list(raw.get("steps", [])),
            final_state=dict(raw.get("final_state", {})),
            termination_reason=str(raw.get("termination_reason", "")),
            self_report_success=raw.get("self_report_success"),
        )
        return tr


@dataclass
class RunManifest:
    """Immutable run record: enough provenance to reconstruct scores."""

    run_id: str
    algorithm: str
    backend_id: str
    seed: int
    config_hash: str
    task_manifest_hash: str
    genome_hash: str
    environment_version: str
    evaluator_version: str
    generator_version: str
    max_steps: int
    engineering_only: bool = True
    episodes: Tuple[str, ...] = ()
    scores: Tuple[Mapping[str, Any], ...] = ()
    accounting: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "algorithm": self.algorithm,
            "backend_id": self.backend_id,
            "seed": self.seed,
            "config_hash": self.config_hash,
            "task_manifest_hash": self.task_manifest_hash,
            "genome_hash": self.genome_hash,
            "environment_version": self.environment_version,
            "evaluator_version": self.evaluator_version,
            "generator_version": self.generator_version,
            "max_steps": self.max_steps,
            "engineering_only": self.engineering_only,
            "episodes": list(self.episodes),
            "scores": [dict(s) for s in self.scores],
            "accounting": dict(self.accounting),
        }


def build_run_manifest(
    *,
    run_id: str,
    algorithm: str,
    backend_id: str,
    seed: int,
    config: Mapping[str, Any],
    task_manifest_hash: str,
    genome_hash: str,
    environment_version: str,
    evaluator_version: str,
    generator_version: str,
    max_steps: int,
    episodes: Sequence[EpisodeTrace],
    results: Sequence[EpisodeResult],
    engineering_only: bool = True,
    accounting: Optional[Mapping[str, Any]] = None,
) -> RunManifest:
    scores = tuple(
        {
            "task_id": r.task_id,
            "success": r.success,
            "steps": r.steps,
            "invalid_actions": r.invalid_actions,
            "repeated_states": r.repeated_states,
            "termination_reason": r.termination_reason,
            "final_state_hash": r.final_state_hash,
            "genome_hash": r.genome_hash,
        }
        for r in results
    )
    return RunManifest(
        run_id=run_id,
        algorithm=algorithm,
        backend_id=backend_id,
        seed=seed,
        config_hash=config_hash(config),
        task_manifest_hash=task_manifest_hash,
        genome_hash=genome_hash,
        environment_version=environment_version,
        evaluator_version=evaluator_version,
        generator_version=generator_version,
        max_steps=max_steps,
        engineering_only=engineering_only,
        episodes=tuple(e.task_id for e in episodes),
        scores=scores,
        accounting=dict(accounting or {}),
    )


def reconstruct_scores(
    traces: Sequence[EpisodeTrace],
    tasks: Mapping[str, TaskInstance],
    evaluator,
) -> List[EpisodeResult]:
    """Rebuild evaluation results purely from raw traces + task manifests."""
    out: List[EpisodeResult] = []
    for trace in traces:
        task = tasks.get(trace.task_id)
        if task is None:
            raise KeyError(f"missing task for trace {trace.task_id}")
        result = evaluator.evaluate(task, trace.final_state, trace.steps)
        out.append(result)
    return out


def reconstruct_from_artifacts(
    artifact: Mapping[str, Any],
    tasks: Mapping[str, TaskInstance],
    evaluator,
) -> Dict[str, Any]:
    """Reload a serialized run artifact and rebuild every score from actual traces.

    Rebuilt results are matched to manifest scores by (task_id, final_state_hash);
    the trace's own genome_hash is checked against the recorded value.
    """
    traces = [EpisodeTrace.from_dict(t) for t in artifact.get("traces", [])]
    rebuilt = []
    mismatches = []

    recorded_scores = {
        (s.get("task_id"), s.get("genome_hash"), s.get("final_state_hash")): s
        for s in artifact.get("manifest", {}).get("scores", [])
    }

    for trace in traces:
        task = tasks.get(trace.task_id)
        if task is None:
            mismatches.append({"task_id": trace.task_id, "reason": "missing_task"})
            continue
        result = evaluator.evaluate(task, trace.final_state, trace.steps)
        # Attach the genome hash recorded in the actual trace.
        result_with_genome = result.__class__(
            task_id=result.task_id,
            genome_hash=trace.genome_hash,
            success=result.success,
            steps=result.steps,
            invalid_actions=result.invalid_actions,
            repeated_states=result.repeated_states,
            termination_reason=result.termination_reason,
            final_state_hash=result.final_state_hash,
            diagnostic=result.diagnostic,
        )
        rebuilt.append(result_with_genome)

        key = (result.task_id, trace.genome_hash, result.final_state_hash)
        if key not in recorded_scores:
            mismatches.append(
                {
                    "task_id": result.task_id,
                    "reason": "missing_in_manifest",
                    "final_state_hash": result.final_state_hash,
                    "genome_hash": trace.genome_hash,
                }
            )
            continue
        rec = recorded_scores[key]
        if bool(rec.get("success")) != bool(result.success) or int(rec.get("steps", -1)) != int(
            result.steps
        ):
            mismatches.append(
                {
                    "task_id": result.task_id,
                    "reason": "score_mismatch",
                    "recorded": rec,
                    "rebuilt_success": result.success,
                }
            )

    return {
        "rebuilt": rebuilt,
        "mismatches": mismatches,
        "manifest_task_manifest_hash": artifact.get("manifest", {}).get("task_manifest_hash"),
        "accounting": artifact.get("accounting"),
    }
