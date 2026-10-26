"""Shared fixtures and helpers for AES engineering tests.

IMPORTANT: All tests use the mock backend. Mock/synthetic scores are
engineering-only and must never be described as Agent capability evidence.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from agentfotagent.genome.schema import (  # noqa: E402
    GENES,
    Genome,
    GenomeSpace,
    genome_hash,
    normalize_genome,
)
from agentfotagent.tasks.generators import (  # noqa: E402
    FAMILIES,
    FAMILY_SPLITS,
    generate_split_manifests,
    generate_task,
)
from agentfotagent.runtime.mock_backend import run_episode  # noqa: E402


BASE_GENOME = {
    "planning_mode": "direct",
    "memory_policy": "none",
    "verification_policy": "none",
    "tool_selection_policy": "fixed_ranking",
}

ENGINEERING_ONLY = True


@pytest.fixture(scope="session")
def space() -> GenomeSpace:
    return GenomeSpace()


@pytest.fixture(scope="session")
def splits():
    return generate_split_manifests(
        train_seeds=[1, 2, 3],
        dev_seeds=[11, 12],
        held_out_seeds=[21, 22],
    )


def make_genome(**overrides) -> Genome:
    raw = dict(BASE_GENOME)
    raw.update(overrides)
    return normalize_genome(raw)


def episode(genome, family: str, split: str, seed: int):
    task = generate_task(family, seed, split)
    return run_episode(task, genome, seed=seed)


def action_tools(trace) -> list:
    return [s["action"]["tool"] for s in trace.steps]


def action_list(trace) -> list:
    return [(s["action"]["tool"], tuple(sorted(s["action"].get("args", {}).items()))) for s in trace.steps]
