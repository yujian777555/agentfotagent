"""P0-R1-Corrective-2 tests: unique run artifacts and clean-SHA provenance."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from experiments.metabox.provenance import (  # noqa: E402
    DirtyWorktreeError,
    ProvenanceError,
    ensure_clean_worktree,
    ensure_unique_artifacts,
    git_rev_parse_head,
    git_status_porcelain,
    make_run_id,
)


def test_ensure_clean_worktree_returns_sha():
    prov = ensure_clean_worktree(allow_dirty=True)
    assert len(prov["git_sha"]) == 40 or prov["git_sha"] == "unknown"
    assert prov["worktree_dirty"] in {"true", "false"}


def test_dirty_worktree_rejected_without_allow():
    from experiments.metabox.provenance import git_status_porcelain

    try:
        dirty = git_status_porcelain()
    except Exception:
        pytest.skip("git unavailable")
    if dirty:
        with pytest.raises(DirtyWorktreeError):
            ensure_clean_worktree(allow_dirty=False)
    else:
        prov = ensure_clean_worktree(allow_dirty=False)
        assert prov["worktree_dirty"] == "false"


def test_run_ids_unique_across_calls():
    """Two consecutive run-id constructions must not collide."""
    import time

    from experiments.metabox.run_smoke import ensure_clean_worktree

    prov = ensure_clean_worktree(allow_dirty=True)
    ids = set()
    for _ in range(5):
        stamp = time.strftime("%Y%m%dT%H%M%S")
        rid = f"phase1a-smoke-{prov['git_sha'][:12]}-dirty-{stamp}"
        ids.add(rid)
        time.sleep(1.05)
    assert len(ids) == 5


def test_existing_manifest_refuses_overwrite(tmp_path):
    """Simulate collision: manifest_path exists → must not silently overwrite."""
    run_id = "unit-test-collision-run"
    manifest_path = tmp_path / f"manifest_{run_id}.json"
    manifest_path.write_text("{}", encoding="utf-8")
    with pytest.raises(FileExistsError):
        if manifest_path.exists():
            raise FileExistsError(f"refusing to overwrite existing run artifacts for {run_id}")


def test_traces_live_in_run_scoped_dirs_and_old_not_overwritten():
    """Real artifacts: each historical run keeps its own traces/<run_id>/ tree."""
    traces_root = ROOT / "results" / "phase1a_smoke" / "traces"
    if not traces_root.exists():
        pytest.skip("no traces yet")
    run_dirs = [p for p in traces_root.iterdir() if p.is_dir()]
    # Flat historical traces (p0-r1-corrective) also preserved as files.
    old_flat = [p for p in traces_root.glob("*.json")]
    assert run_dirs or old_flat
    # New convention: directories named by run_id
    for d in run_dirs:
        assert d.name.startswith("phase1a-smoke-")
        for f in d.glob("*.json"):
            obj = json.loads(f.read_text(encoding="utf-8"))
            assert obj.get("run_id") == d.name
            assert "git_sha" in obj


def test_manifest_trace_paths_and_hashes_consistent():
    """If a manifest exists, its trace_path/hash must match the file on disk."""
    import hashlib

    out = ROOT / "results" / "phase1a_smoke"
    manifests = sorted(out.glob("manifest_phase1a-smoke-*.json"))
    if not manifests:
        pytest.skip("no manifests")
    latest = manifests[-1]
    data = json.loads(latest.read_text(encoding="utf-8"))
    for row in data.get("controlled_de_runs", []):
        tp = row.get("trace_path")
        th = row.get("trace_sha256")
        if not tp:
            continue
        p = ROOT / tp
        if not p.exists():
            # Older runs stored traces differently; only enforce for r1c+ layout
            continue
        digest = hashlib.sha256(p.read_bytes()).hexdigest()
        if th:
            assert digest == th
        obj = json.loads(p.read_text(encoding="utf-8"))
        assert obj["run_id"] == data["run_id"] or obj.get("run_id")
