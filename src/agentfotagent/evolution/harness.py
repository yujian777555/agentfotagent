"""Shared baseline harness: identical evaluation path for every algorithm.

Both RandomSearch and ConventionalEA call ``shared_evaluate_genome`` which uses
the same normalized genome space, the same environment, the same evaluator and
the same max-step budget.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Mapping, Sequence, Tuple

from ..environments.tool_world import ToolWorld, TOOL_WORLD_VERSION
from ..evaluation.evaluator import StateBasedEvaluator
from ..evaluation.provenance import EpisodeTrace, build_run_manifest, config_hash
from ..genome.schema import Genome, GenomeSpace, genome_hash, normalize_genome
from ..interfaces import EpisodeResult, SearchRecord, TaskInstance
from ..runtime.cache import EvaluationCache, make_cache_key
from ..runtime.mock_backend import MOCK_BACKEND_ID, run_episode


EVALUATOR_VERSION = "aes-evaluator-v1"


@dataclass
class BaselineHarness:
    """Shared evaluation path for random search and conventional EA baselines."""

    tasks: Sequence[TaskInstance]
    space: GenomeSpace
    config: Mapping[str, Any] = field(default_factory=dict)
    cache: EvaluationCache = field(default_factory=EvaluationCache)
    backend_id: str = MOCK_BACKEND_ID

    def config_hash(self) -> str:
        return config_hash(self.config)

    def task_manifest_hash(self) -> str:
        from ..tasks.manifests import manifest_hash, task_to_manifest_entry

        return manifest_hash([task_to_manifest_entry(t) for t in self.tasks])

    def evaluate_genome(self, genome: Genome | Mapping[str, Any]) -> SearchRecord:
        """The single shared evaluator path used by every baseline algorithm."""
        g = normalize_genome(genome)
        gh = genome_hash(g)
        results: List[EpisodeResult] = []
        for task in self.tasks:
            key = make_cache_key(
                task_id=task.public.task_id,
                task_content_hash=task.content_hash,
                split=task.public.split,
                genome_hash=gh,
                backend_id=self.backend_id,
                config_hash=self.config_hash(),
                environment_version=TOOL_WORLD_VERSION,
                evaluator_version=EVALUATOR_VERSION,
            )
            cached = self.cache.get(key, expected_split=task.public.split)
            if cached is not None:
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
            self.cache.put(
                key,
                result,
                meta={
                    "split": task.public.split,
                    "task_id": task.public.task_id,
                    "genome_hash": gh,
                    "backend_id": self.backend_id,
                },
            )
            results.append(result)

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

    def run_algorithm(self, algorithm, budget: int) -> Tuple[List[SearchRecord], Any]:
        records = algorithm.run(self.evaluate_genome, budget)
        return records

    def build_manifest(self, algorithm_name: str, seed: int, records: Sequence[SearchRecord]):
        episodes = []
        results = []
        for rec in records:
            for er in rec.episode_results:
                results.append(er)
                episodes.append(
                    EpisodeTrace(
                        task_id=er.task_id,
                        split="",
                        genome_hash=er.genome_hash,
                        backend_id=self.backend_id,
                        seed=seed,
                        final_state={"step": er.steps, "termination_reason": er.termination_reason},
                        termination_reason=er.termination_reason,
                    )
                )
        # Use the best record's genome hash as representative when multiple genomes
        # were evaluated; per-episode genome hashes remain inside scores.
        rep_hash = records[0].genome_hash if records else ""
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
            max_steps=int(self.config.get("max_steps", 0)) or (
                self.tasks[0].public.max_steps if self.tasks else 0
            ),
            episodes=episodes,
            results=results,
            engineering_only=True,
        )


def shared_evaluate_genome(
    harness: BaselineHarness, genome: Genome | Mapping[str, Any]
) -> SearchRecord:
    return harness.evaluate_genome(genome)
