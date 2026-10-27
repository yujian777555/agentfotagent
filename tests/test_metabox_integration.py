"""MetaBox integration tests. Require the metaevobox runtime (D:/metabox-env)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# These tests need the official metaevobox package.
pytest.importorskip("metaevobox", reason="metaevobox runtime not installed")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from experiments.metabox.adapter import (  # noqa: E402
    METABOX_GIT_SHA,
    SPLIT_HELD_OUT,
    SPLIT_TRAIN,
    SPLIT_VAL,
    load_function,
    run_optimizer,
    split_manifest,
)
from experiments.metabox.controller_dsl import (  # noqa: E402
    compile_controller,
    fixed_controller_a,
    fixed_controller_b,
)


def test_split_disjoint_and_covers_all_24():
    train, val, held = set(SPLIT_TRAIN), set(SPLIT_VAL), set(SPLIT_HELD_OUT)
    assert train.isdisjoint(val) and train.isdisjoint(held) and val.isdisjoint(held)
    assert train | val | held == set(range(1, 25))
    assert len(train) == 12 and len(val) == 6 and len(held) == 6
    m = split_manifest()
    assert m["manifest_hash"]


def test_load_function_and_eval():
    p = load_function(6)
    assert p.dim == 10
    import numpy as np

    y = p.eval(np.zeros(10))
    assert isinstance(y, float)


def test_fe_accounting_and_direction():
    p = load_function(6)
    ctrl = compile_controller(fixed_controller_a())
    r = run_optimizer("DE", p, max_fes=800, seed=7, controller=ctrl)
    assert r["independent_fes"] == r["reported_fes"]
    assert r["objective_direction"] == "minimize"
    assert r["cost_curve"][0] >= r["cost_curve"][-1] - 1e-6


def test_seed_reproducibility():
    import numpy as np

    ctrl = compile_controller(fixed_controller_b())
    np.random.seed(5)
    p1 = load_function(6)
    r1 = run_optimizer("DE", p1, max_fes=600, seed=5, controller=ctrl)
    np.random.seed(5)
    p2 = load_function(6)
    r2 = run_optimizer("DE", p2, max_fes=600, seed=5, controller=ctrl)
    assert r1["cost_curve"] == r2["cost_curve"]
    assert r1["best_cost"] == r2["best_cost"]
    assert r1["independent_fes"] == r2["independent_fes"]


def test_two_controllers_both_execute_and_differ():
    a = compile_controller(fixed_controller_a())
    b = compile_controller(fixed_controller_b())
    p1 = load_function(6)
    p2 = load_function(6)
    ra = run_optimizer("DE", p1, max_fes=800, seed=11, controller=a)
    rb = run_optimizer("DE", p2, max_fes=800, seed=11, controller=b)
    assert ra["applied_action"]["action"] == "set_F_range"
    assert rb["applied_action"]["action"] == "set_F_range"
    assert ra["applied_action"]["params"] != rb["applied_action"]["params"]
    assert ra["best_cost"] != rb["best_cost"] or ra["cost_curve"] != rb["cost_curve"]


def test_smoke_manifest_reconstructable():
    path = Path(__file__).resolve().parents[1] / "results" / "phase1a_smoke" / "manifest.json"
    if not path.exists():
        pytest.skip("smoke manifest not generated")
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["metabox"]["git_sha"] == METABOX_GIT_SHA
    assert data["fe_accounting_match"] is True
    assert data["objective_direction_ok"] is True
    assert data["engineering_only"] is True
    for run in data["runs"]:
        assert run["independent_fes"] == run["reported_fes"]
        assert run["cost_curve"]
