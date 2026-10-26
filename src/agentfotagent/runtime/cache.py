"""Evaluation cache with task/genome/backend/config keys and split isolation.

Held-out evaluation cannot reuse development outputs: cache keys include the
task content hash and split namespace.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Optional, Tuple

from ..interfaces import EpisodeResult


class CacheIsolationError(RuntimeError):
    """Raised when a held-out evaluation would read development cache entries."""


def make_cache_key(
    *,
    task_id: str,
    task_content_hash: str,
    split: str,
    genome_hash: str,
    backend_id: str,
    config_hash: str,
    environment_version: str,
    evaluator_version: str,
) -> str:
    payload = {
        "task_id": task_id,
        "task_content_hash": task_content_hash,
        "split": split,
        "genome_hash": genome_hash,
        "backend_id": backend_id,
        "config_hash": config_hash,
        "environment_version": environment_version,
        "evaluator_version": evaluator_version,
    }
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


@dataclass
class EvaluationCache:
    """In-memory evaluation cache. Keys are content-addressed and split-scoped."""

    _store: Dict[str, EpisodeResult] = field(default_factory=dict)
    _key_meta: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def get(self, key: str, *, expected_split: Optional[str] = None) -> Optional[EpisodeResult]:
        if key not in self._store:
            return None
        meta = self._key_meta.get(key, {})
        if expected_split is not None and meta.get("split") != expected_split:
            raise CacheIsolationError(
                f"cache split mismatch: key is {meta.get('split')!r}, expected {expected_split!r}"
            )
        return self._store[key]

    def put(self, key: str, result: EpisodeResult, *, meta: Mapping[str, Any]) -> None:
        self._store[key] = result
        self._key_meta[key] = dict(meta)

    def __len__(self) -> int:
        return len(self._store)

    def splits_present(self) -> set:
        return {m.get("split") for m in self._key_meta.values()}

    def keys_for_split(self, split: str) -> list:
        return [k for k, m in self._key_meta.items() if m.get("split") == split]
