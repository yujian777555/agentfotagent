"""Shared baseline harness: identical evaluation path for every algorithm.

Both RandomSearch and ConventionalEA call ``shared_evaluate_genome`` which uses
the same normalized genome space, the same environment, the same evaluator and
the same max-step budget.

Phase-0-R1: actual EpisodeTrace objects are retained per evaluation so run
artifacts can be serialized, reloaded and used to reconstruct every score.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Tuple

from ..environments.tool_world import ToolWorld, TOOL_WORLD_VERSION
from ..evaluation.evaluator import StateBasedEvaluator
from ..evaluation.provenance import (
    EpisodeTrace,
    RunManifest,
    build_run_manifest,
    config_hash,
)
from ..genome.schema import Genome, GenomeSpace, genome_hash, normalize_genome
from ..interfaces import EpisodeResult, SearchRecord, TaskInstance
from ..runtime.cache import EvaluationCache, make_cache_key
from ..runtime.mock_backend import MOCK_BACKEND_ID, run_episode


EVALUATOR_VERSION = "aes-evaluator-v1"


@dataclass
class EvaluationAccounting:
    """Counts needed before any scientific baseline comparison (audit C1)."""

    candidate_proposals: int = 0
    unique_genomes: int = 0
    cache_hits: int = 0
    actual_episode_executions: int = 0
    task_evaluations: int = 0

    def to_dict(self) -> Dict[str, int]:
        return {
            "candidate_proposals": self.candidate_proposals,
            "unique_genomes": self.unique_genomes,
            "cache_hits": self.cache_hits,
            "actual_episode_executions": self.actual_episode_executions,
            "task_evaluations": self.task_evaluations,
        }


@dataclass
class BaselineHarness:
    """Shared evaluation path for random search and conventional EA baselines."""

    tasks: Sequence[TaskInstance]
    space: GenomeSpace
    config: Mapping[str, Any] = field(default_factory=dict)
    cache: EvaluationCache = field(default_factory=EvaluationCache)
    backend_id: str = MOCK_BACKEND_ID
    accounting: EvaluationAccounting = field(default_factory=EvaluationAccounting)
    # key -> actual EpisodeTrace (never a synthetic stand-in)
    trace_store: Dict[str, EpisodeTrace] = field(default_factory=dict)
    _seen_genome_hashes: set = field(default_factory=set)

    def config_hash(self) -> str:
        return config_hash(self.config)

    def task_manifest_hash(self) -> str:
        from ..tasks.manifests import manifest_hash, task_to_manifest_entry

        return manifest_hash([task_to_manifest_entry(t) for t in self.tasks])

    def evaluate_genome(self, genome: Genome | Mapping[str, Any]) -> SearchRecord:
        """The single shared evaluator path used by every baseline algorithm."""
        g = normalize_genome(genome)
        gh = genome_hash(g)
        self.accounting.candidate_proposals += 1
        self._seen_genome_hashes.add(gh)

        results: List[EpisodeResult] = []
        for task in self.tasks:
            key = make_cache_key(
                task_id=task.task_id,
                task_content_hash=task.content_hash,
                split=task.split,
                genome_hash=gh,
                backend_id=self.backend_id,
                config_hash=self.config_hash(),
                environment_version=TOOL_WORLD_VERSION,
                evaluator_version=EVALUATOR_VERSION,
            )
            self.accounting.task_evaluations += 1
            cached = self.cache.get(key, expected_split=task.split)
            if cached is not None:
                self.accounting.cache_hits += 1
                results.append(cached)
                continue

            env = ToolWorld()
            ev = StateBasedEvaluator(genome_hash=gh)
            success, trace, payload = run_episode(
                task,
                g,
                seed=task.seed,
                backend_id=self.backend_id,
                environment=env,
                evaluator=ev,
            )
            result: EpisodeResult = payload["episode_result"]
            # Retain the actual trace (not a synthetic replacement).
            self.trace_store[key] = trace
            self.cache.put(
                key,
                result,
                meta={
                    "split": task.split,
                    "task_id": task.task_id,
                    "genome_hash": gh,
                    "backend_id": self.backend_id,
                    "trace_key": key,
                },
            )
            self.accounting.actual_episode_executions += 1
            results.append(result)

        self.accounting.unique_genomes = len(self._seen_genome_hashes)
        successes = sum(1 for r in results if r.success)
        total = len(results)
        return SearchRecord(
            genome=g.to_dict(),
            genome_hash=gh,
            task_ids=tuple(r.task_id for r in results),
            successes=successes,
            total=total,
            success_rate=(successes / total if total else 0.0),
            episode_results=tuple(results),
        )

    def run_algorithm(self, algorithm, budget: int) -> List[SearchRecord]:
        return algorithm.run(self.evaluate_genome, budget)

    def actual_traces(self) -> List[EpisodeTrace]:
        return list(self.trace_store.values())

    def build_manifest(self, algorithm_name: str, seed: int, records: Sequence[SearchRecord]) -> RunManifest:
        """Build a run manifest from actual traces produced by evaluations."""
        # Representative genome: the best-scoring record (not merely the first).
        if records:
            best = max(records, key=lambda r: (r.success_rate, r.successes, r.genome_hash))
            rep_hash = best.genome_hash
        else:
            rep_hash = ""

        episodes: List[EpisodeTrace] = []
        results: List[EpisodeResult] = []
        seen_task_genome = set()
        for rec in records:
            for er in rec.episode_results:
                pair = (er.task_id, er.genome_hash)
                if pair in seen_task_genome:
                    continue
                seen_task_genome.add(pair)
                results.append(er)
                # Locate the actual trace for this evaluation.
                for key, tr in self.trace_store.items():
                    if tr.task_id == er.task_id and tr.genome_hash == er.genome_hash:
                        episodes.append(tr)
                        break

        return build_run_manifest(
            run_id=f"{algorithm_name}-{seed}",
            algorithm=algorithm_name,
            backend_id=self.backend_id,
            seed=seed,
            config=self.config,
            task_manifest_hash=self.task_manifest_hash(),
            genome_hash=rep_hash,
            environment_version=TOOL_WORLD_VERSION,
            evaluator_version=EVALUATOR_VERSION,
            generator_version=self.tasks[0].generator_version if self.tasks else "",
            max_steps=int(self.config.get("max_steps", 0))
            or (self.tasks[0].runtime.max_steps if self.tasks else 0),
            episodes=episodes,
            results=results,
            engineering_only=True,
            accounting=self.accounting.to_dict(),
        )

    def serialize_run_artifacts(self, algorithm_name: str, seed: int) -> Dict[str, Any]:
        """Serializable run artifact: manifest + actual traces + task map."""
        records = getattr(self, "_last_records", [])
        manifest = self.build_manifest(algorithm_name, seed, records)
        return {
            "manifest": manifest.to_dict(),
            "traces": [t.to_dict() for t in self.actual_traces()],
            "accounting": self.accounting.to_dict(),
            "task_manifest_hash": self.task_manifest_hash(),
        }

    def run_and_collect(self, algorithm, budget: int) -> Dict[str, Any]:
        """Run an algorithm and return serializable artifacts from actual traces."""
        self._last_records = algorithm.run(self.evaluate_genome, budget)
        return self.serialize_run_artifacts(algorithm.name, algorithm.seed)


def shared_evaluate_genome(
    harness: BaselineHarness, genome: Genome | Mapping[str, Any]
) -> SearchRecord:
    return harness.evaluate_genome(genome)
