"""Task manifests, content hashes and split summaries."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence

from ..interfaces import TaskInstance


def manifest_hash(entries: Sequence[Mapping[str, Any]]) -> str:
    payload = json.dumps(list(entries), sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def task_to_manifest_entry(task: TaskInstance, include_hidden: bool = True) -> Dict[str, Any]:
    entry: Dict[str, Any] = {
        # Evaluation-side metadata. Runtime-facing payload is only RuntimeTask.
        "runtime": task.runtime.to_payload(),
        "family": task.family,
        "split": task.split,
        "seed": task.seed,
        "generator_version": task.generator_version,
        "content_hash": task.content_hash,
    }
    if include_hidden:
        # Manifest is an evaluation-side artifact; Agent runtime must not read held-out manifests.
        entry["hidden_goal"] = dict(task.hidden_goal)
        entry["setup"] = dict(task.setup)
    return entry


def split_summary(splits: Mapping[str, Sequence[TaskInstance]]) -> Dict[str, Any]:
    families_by_split = {
        name: sorted({t.family for t in tasks})
        for name, tasks in splits.items()
    }
    task_ids = {
        name: [t.task_id for t in tasks]
        for name, tasks in splits.items()
    }
    hashes = {
        name: [t.content_hash for t in tasks]
        for name, tasks in splits.items()
    }
    return {
        "generator_version": next(
            (t.generator_version for tasks in splits.values() for t in tasks),
            "",
        ),
        "families_by_split": families_by_split,
        "task_ids": task_ids,
        "content_hashes": hashes,
        "manifest_hashes": {
            name: manifest_hash([task_to_manifest_entry(t) for t in tasks])
            for name, tasks in splits.items()
        },
        "counts": {name: len(tasks) for name, tasks in splits.items()},
        "family_isolation": {
            "train_families": families_by_split.get("train", []),
            "dev_families": families_by_split.get("dev", []),
            "held_out_families": families_by_split.get("held_out", []),
            "train_dev_disjoint_from_held_out": set(families_by_split.get("train", []))
            .union(families_by_split.get("dev", []))
            .isdisjoint(families_by_split.get("held_out", [])),
        },
    }


@dataclass
class ManifestStore:
    """Append-only task manifest writer. Never store secrets."""

    root: Path

    def write_split(self, split_name: str, tasks: Sequence[TaskInstance], include_hidden: bool = True) -> Path:
        self.root.mkdir(parents=True, exist_ok=True)
        entries = [task_to_manifest_entry(t, include_hidden=include_hidden) for t in tasks]
        path = self.root / f"{split_name}.json"
        payload = {
            "split": split_name,
            "count": len(entries),
            "manifest_hash": manifest_hash(entries),
            "tasks": entries,
        }
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        return path

    def write_public_index(self, splits: Mapping[str, Sequence[TaskInstance]]) -> Path:
        """Public index WITHOUT hidden goals — safe for runtime-side task listing."""
        self.root.mkdir(parents=True, exist_ok=True)
        entries = []
        for split_name, tasks in splits.items():
            for t in tasks:
                entries.append(task_to_manifest_entry(t, include_hidden=False))
        path = self.root / "public_index.json"
        payload = {
            "generator_version": next(
                (t.generator_version for tasks in splits.values() for t in tasks), ""
            ),
            "count": len(entries),
            "manifest_hash": manifest_hash(entries),
            "tasks": entries,
        }
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        return path
