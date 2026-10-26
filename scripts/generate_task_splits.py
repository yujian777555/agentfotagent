"""Generate frozen task-split manifests under configs/ and results/manifests/.

Usage: python scripts/generate_task_splits.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agentfotagent.tasks.generators import generate_split_manifests  # noqa: E402
from agentfotagent.tasks.manifests import ManifestStore, split_summary  # noqa: E402


def main() -> None:
    seeds_path = ROOT / "configs" / "seeds.json"
    seeds = json.loads(seeds_path.read_text(encoding="utf-8"))

    splits = generate_split_manifests(
        train_seeds=seeds["train_seeds"],
        dev_seeds=seeds["dev_seeds"],
        held_out_seeds=seeds["held_out_seeds"],
    )

    store = ManifestStore(root=ROOT / "results" / "manifests")
    for name, tasks in splits.items():
        store.write_split(name, tasks, include_hidden=True)
    store.write_public_index(splits)

    summary = split_summary(splits)
    summary_path = ROOT / "configs" / "task_splits.json"
    payload = {
        "schema_version": "aes-task-splits-v1",
        "seeds": seeds,
        **summary,
    }
    summary_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("counts", "families_by_split", "manifest_hashes", "family_isolation")}, indent=2))


if __name__ == "__main__":
    main()
