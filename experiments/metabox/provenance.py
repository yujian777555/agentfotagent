"""Git source provenance for official reproducible runs.

Fail-closed: command failures, empty SHA, and dirty worktrees are never
interpreted as a clean successful run.
"""
from __future__ import annotations

import subprocess
import time
from typing import Dict, List, Optional, Sequence


class ProvenanceError(RuntimeError):
    """Git provenance could not be established."""


class DirtyWorktreeError(ProvenanceError):
    """Worktree has uncommitted changes; official runs refuse to proceed."""


def _run_git(args: Sequence[str], timeout: int = 10) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def git_rev_parse_head() -> str:
    """Return HEAD SHA or raise ProvenanceError. Never returns 'unknown' silently."""
    try:
        out = _run_git(["rev-parse", "HEAD"])
    except Exception as exc:  # noqa: BLE001
        raise ProvenanceError(f"git rev-parse HEAD failed to execute: {exc}") from exc
    if out.returncode != 0:
        raise ProvenanceError(f"git rev-parse HEAD failed rc={out.returncode}: {out.stderr}")
    sha = (out.stdout or "").strip()
    if not sha or sha == "unknown" or len(sha) < 7:
        raise ProvenanceError(f"git rev-parse HEAD returned empty/invalid SHA: {sha!r}")
    return sha


def git_status_porcelain() -> str:
    """Return porcelain status or raise ProvenanceError. Fail-closed."""
    try:
        out = _run_git(["status", "--porcelain"])
    except Exception as exc:  # noqa: BLE001
        raise ProvenanceError(f"git status failed to execute: {exc}") from exc
    if out.returncode != 0:
        raise ProvenanceError(f"git status --porcelain failed rc={out.returncode}: {out.stderr}")
    return (out.stdout or "").strip()


def ensure_clean_worktree(*, allow_dirty: bool = False) -> Dict[str, str]:
    """Fail-closed provenance gate for official runs."""
    sha = git_rev_parse_head()
    try:
        dirty = git_status_porcelain()
    except ProvenanceError:
        if allow_dirty:
            return {
                "git_sha": sha,
                "worktree_dirty": "unknown",
                "dirty_files": "git-status-unavailable",
            }
        raise
    if dirty and not allow_dirty:
        raise DirtyWorktreeError(
            "worktree is dirty; commit first or pass --allow-dirty. Diff:\n" + dirty[:2000]
        )
    return {
        "git_sha": sha,
        "worktree_dirty": "true" if dirty else "false",
        "dirty_files": dirty[:2000] if dirty else "",
    }


def make_run_id(
    git_sha: str,
    *,
    worktree_dirty: str,
    tag: str = "run",
    now: Optional[str] = None,
) -> str:
    """Unique run identifier: tag-sha12-clean|dirty-timestamp."""
    if not git_sha or git_sha == "unknown":
        raise ProvenanceError("cannot build run_id from empty/unknown git SHA")
    dirty_tag = "dirty" if worktree_dirty == "true" else "clean"
    if worktree_dirty == "unknown":
        dirty_tag = "dirty"
    stamp = now or time.strftime("%Y%m%dT%H%M%S")
    return f"{tag}-{git_sha[:12]}-{dirty_tag}-{stamp}"


def ensure_unique_artifacts(manifest_path, trace_dir) -> None:
    """Refuse to overwrite existing run artifacts."""
    if manifest_path.exists():
        raise FileExistsError(f"refusing to overwrite existing manifest {manifest_path}")
    if trace_dir.exists():
        raise FileExistsError(f"refusing to overwrite existing trace dir {trace_dir}")
