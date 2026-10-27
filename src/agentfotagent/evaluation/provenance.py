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
    source_commit_sha: str = ""

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
            "source_commit_sha": self.source_commit_sha,
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
    source_commit_sha: str = "",
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
        source_commit_sha=source_commit_sha,
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


class ReconstructionError(RuntimeError):
    """Raised when artifact traces and manifest scores are not in exact correspondence."""


# All persisted score fields that must match the rebuilt EpisodeResult (R3-04/R4-01/R4-02).
SCORE_COMPARE_FIELDS = (
    "success",
    "steps",
    "invalid_actions",
    "repeated_states",
    "termination_reason",
    "final_state_hash",
)

# Identity fields allowed on a score record (no unknown keys, R4-02).
SCORE_IDENTITY_FIELDS = (
    "task_id",
    "genome_hash",
)

# Versioned score-record schema. Extensions require bumping this and validating.
SCORE_RECORD_SCHEMA_VERSION = "aes-score-record-v2"
ALLOWED_SCORE_FIELDS = frozenset(SCORE_COMPARE_FIELDS) | frozenset(SCORE_IDENTITY_FIELDS)


def _normalize_score_value(field: str, value: Any) -> Any:
    if field == "success":
        # R4-01: require a real boolean; never coerce int/str/None.
        if not isinstance(value, bool):
            raise ReconstructionError(
                f"{field} must be bool, got {type(value).__name__}"
            )
        return value
    if field in {"steps", "invalid_actions", "repeated_states"}:
        if isinstance(value, bool):
            raise ReconstructionError(f"{field} must be int, got bool")
        if not isinstance(value, int):
            raise ReconstructionError(f"{field} must be int, got {type(value).__name__}")
        return value
    if field == "termination_reason":
        if not isinstance(value, str):
            raise ReconstructionError(f"{field} must be str, got {type(value).__name__}")
        return value
    if field == "final_state_hash":
        if not isinstance(value, str) or not value:
            raise ReconstructionError(f"{field} must be non-empty str")
        return value
    return value


def validate_score_record_schema(recorded: Mapping[str, Any]) -> None:
    """R4-02: closed schema — reject unknown keys and missing required keys."""
    if not isinstance(recorded, Mapping):
        raise ReconstructionError("score record must be a mapping")
    keys = set(recorded.keys())
    unknown = keys - ALLOWED_SCORE_FIELDS
    if unknown:
        raise ReconstructionError(f"unknown score fields: {sorted(unknown)}")
    missing = set(SCORE_COMPARE_FIELDS) | set(SCORE_IDENTITY_FIELDS)
    missing -= keys
    if missing:
        raise ReconstructionError(f"manifest score missing field: {sorted(missing)}")
    # Identity field types
    for f in SCORE_IDENTITY_FIELDS:
        if not isinstance(recorded[f], str) or not recorded[f]:
            raise ReconstructionError(f"{f} must be non-empty str")
    # Score field types
    for f in SCORE_COMPARE_FIELDS:
        _normalize_score_value(f, recorded[f])


def compare_score_fields(recorded: Mapping[str, Any], rebuilt: EpisodeResult) -> None:
    """Strict full-field comparison between a manifest score and a rebuilt result."""
    validate_score_record_schema(recorded)
    for field in SCORE_COMPARE_FIELDS:
        rec_val = _normalize_score_value(field, recorded[field])
        reb_val = getattr(rebuilt, field)
        if rec_val != reb_val:
            raise ReconstructionError(
                f"score field mismatch for {rebuilt.task_id}: {field} recorded={rec_val!r} rebuilt={reb_val!r}"
            )
    if recorded["task_id"] != rebuilt.task_id:
        raise ReconstructionError("score task_id does not match rebuilt result")


def reconstruct_from_artifacts(
    artifact: Mapping[str, Any],
    tasks: Mapping[str, TaskInstance],
    evaluator,
) -> Dict[str, Any]:
    """Reload a serialized run artifact and rebuild every score from actual traces.

    Completeness is enforced in both directions:
    - every trace must map to exactly one manifest score;
    - every manifest score must map to exactly one trace.
    Missing traces, extra scores or hash mismatches raise ReconstructionError.
    """
    raw_traces = artifact.get("traces")
    raw_scores = artifact.get("manifest", {}).get("scores")
    if raw_traces is None or raw_scores is None:
        raise ReconstructionError("artifact must contain traces and manifest.scores")

    traces = [EpisodeTrace.from_dict(t) for t in raw_traces]
    recorded_scores = list(raw_scores)

    # Index manifest scores by full identity key.
    score_index: Dict[Tuple[Any, Any, Any], Mapping[str, Any]] = {}
    for s in recorded_scores:
        key = (s.get("task_id"), s.get("genome_hash"), s.get("final_state_hash"))
        if key in score_index:
            raise ReconstructionError(f"duplicate manifest score key: {key}")
        score_index[key] = s

    rebuilt = []
    matched_keys = set()
    mismatches = []

    for trace in traces:
        task = tasks.get(trace.task_id)
        if task is None:
            raise ReconstructionError(f"missing task for trace {trace.task_id}")
        result = evaluator.evaluate(task, trace.final_state, trace.steps)
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
        if key not in score_index:
            raise ReconstructionError(
                f"trace has no corresponding manifest score: {key}"
            )
        if key in matched_keys:
            raise ReconstructionError(f"duplicate trace identity: {key}")
        matched_keys.add(key)

        rec = score_index[key]
        try:
            compare_score_fields(rec, result)
        except ReconstructionError:
            raise
        except Exception as exc:
            raise ReconstructionError(f"invalid manifest score record: {exc}") from exc

    # Every manifest score must be covered by a trace (R1-05: reverse direction).
    unmatched_scores = [k for k in score_index if k not in matched_keys]
    if unmatched_scores:
        raise ReconstructionError(
            f"manifest scores missing corresponding traces: {unmatched_scores}"
        )

    if mismatches:
        raise ReconstructionError(f"score values disagree after rebuild: {mismatches}")

    return {
        "rebuilt": rebuilt,
        "mismatches": [],
        "trace_count": len(traces),
        "score_count": len(recorded_scores),
        "manifest_task_manifest_hash": artifact.get("manifest", {}).get("task_manifest_hash"),
        "accounting": artifact.get("accounting"),
    }
