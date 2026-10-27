"""Fail-closed git provenance tests (P1A-1 blocker fix)."""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from experiments.metabox.provenance import (
    DirtyWorktreeError,
    ProvenanceError,
    ensure_clean_worktree,
    ensure_unique_artifacts,
    git_rev_parse_head,
    git_status_porcelain,
    make_run_id,
)


def test_git_rev_parse_returns_sha_or_raises():
    try:
        sha = git_rev_parse_head()
    except ProvenanceError:
        # acceptable only if truly not a git repo
        pytest.skip("not a git repo")
    assert len(sha) >= 7 and sha != "unknown"


def test_git_status_fail_closed(monkeypatch, tmp_path):
    def fake_run(*a, **k):
        raise OSError("git missing")

    monkeypatch.setattr("experiments.metabox.provenance._run_git", fake_run)
    with pytest.raises(ProvenanceError):
        git_status_porcelain()


def test_git_rev_parse_empty_sha_raises(monkeypatch):
    class R:
        returncode = 0
        stdout = "   \n"
        stderr = ""

    monkeypatch.setattr("experiments.metabox.provenance._run_git", lambda *a, **k: R())
    with pytest.raises(ProvenanceError):
        git_rev_parse_head()


def test_git_rev_parse_unknown_raises(monkeypatch):
    class R:
        returncode = 0
        stdout = "unknown\n"
        stderr = ""

    monkeypatch.setattr("experiments.metabox.provenance._run_git", lambda *a, **k: R())
    with pytest.raises(ProvenanceError):
        git_rev_parse_head()


def test_git_rev_parse_failure_raises(monkeypatch):
    class R:
        returncode = 128
        stdout = ""
        stderr = "fatal: not a git repository"

    monkeypatch.setattr("experiments.metabox.provenance._run_git", lambda *a, **k: R())
    with pytest.raises(ProvenanceError):
        git_rev_parse_head()


def test_dirty_worktree_rejected(monkeypatch):
    monkeypatch.setattr("experiments.metabox.provenance._run_git", _FakeGit("abc123def4567890", " M dirty.py"))
    with pytest.raises(DirtyWorktreeError):
        ensure_clean_worktree(allow_dirty=False)


def test_clean_worktree_ok(monkeypatch):
    monkeypatch.setattr("experiments.metabox.provenance._run_git", _FakeGit("abc123def4567890", ""))
    prov = ensure_clean_worktree(allow_dirty=False)
    assert prov["git_sha"].startswith("abc123")
    assert prov["worktree_dirty"] == "false"


class _FakeGit:
    def __init__(self, sha: str, status: str):
        self.sha = sha
        self.status = status

    def __call__(self, args, timeout=10):
        class R:
            returncode = 0
            stderr = ""

        if args and args[0] == "rev-parse":
            R.stdout = self.sha + "\n"
        else:
            R.stdout = self.status + "\n" if self.status else ""
        return R()


def test_make_run_id_rejects_unknown_sha():
    with pytest.raises(ProvenanceError):
        make_run_id("unknown", worktree_dirty="false")
    with pytest.raises(ProvenanceError):
        make_run_id("", worktree_dirty="false")


def test_make_run_id_unique():
    a = make_run_id("abc123def4567890", worktree_dirty="false", now="20261027T000001")
    b = make_run_id("abc123def4567890", worktree_dirty="true", now="20261027T000001")
    assert a != b
    assert "clean" in a and "dirty" in b


def test_ensure_unique_artifacts_refuses_overwrite(tmp_path):
    m = tmp_path / "m.json"
    d = tmp_path / "t"
    ensure_unique_artifacts(m, d)  # ok first
    m.write_text("{}", encoding="utf-8")
    with pytest.raises(FileExistsError):
        ensure_unique_artifacts(m, d)
    m.unlink()
    d.mkdir()
    with pytest.raises(FileExistsError):
        ensure_unique_artifacts(m, d)
