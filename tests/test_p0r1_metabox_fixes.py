"""P0-R1 function identity, controller execution and split_v2 tests."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

pytest.importorskip("metaevobox", reason="metaevobox runtime not installed")

import numpy as np

from experiments.metabox.adapter import (
    BBOB_10D_FUNCS,
    BBOB_FAMILIES,
    METABOX_DIFFICULT,
    SPLIT_V2_HELD_OUT,
    SPLIT_V2_TRAIN,
    SPLIT_V2_VAL,
    UnsupportedActionError,
    load_function,
    run_optimizer,
    split_manifest,
)
from experiments.metabox.controller_dsl import (
    ControllerValidationError,
    compile_controller,
    fixed_controller_a,
    fixed_controller_b,
    validate_controller_spec,
)
from experiments.metabox.controlled_de import run_controlled_de


# ---------------------------------------------------------------------------
# P0-R1-00 function identity
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("fid", [1, 6, 24])
def test_requested_id_matches_loaded_class(fid):
    p = load_function(fid)
    assert p.function_id == fid
    assert p.actual_class_name == f"F{fid}"
    assert p.problem_id.endswith(f"F{fid:02d}")


def test_all_function_ids_load_correctly():
    for fid in BBOB_10D_FUNCS:
        p = load_function(fid)
        assert p.function_id == fid
        assert p.actual_class_name == f"F{fid}"


def test_distinct_ids_are_distinct_functions():
    p1 = load_function(1)
    p6 = load_function(6)
    p24 = load_function(24)
    assert p1.actual_class_name != p6.actual_class_name != p24.actual_class_name
    assert len({p1.actual_class_name, p6.actual_class_name, p24.actual_class_name}) == 3


def test_bounds_dim_direction():
    for fid in (1, 6, 24):
        p = load_function(fid)
        assert p.dim == 10
        assert p.lower_bound == -100.0
        assert p.upper_bound == 100.0
        assert p.objective_direction == "minimize"
        y = p.eval(np.zeros(10))
        assert isinstance(y, float)


def test_fe_counter_on_identity_path():
    p = load_function(6)
    r = run_optimizer("DE", p, max_fes=400, seed=3, controller=None)
    assert r["independent_fes"] == r["reported_fes"] == 400
    assert r["function_id"] == 6
    assert r["actual_class_name"] == "F6"


# ---------------------------------------------------------------------------
# P0-R1-04 split_v2
# ---------------------------------------------------------------------------

def test_split_v2_disjoint_covers_all():
    tr, va, he = set(SPLIT_V2_TRAIN), set(SPLIT_V2_VAL), set(SPLIT_V2_HELD_OUT)
    assert tr.isdisjoint(va) and tr.isdisjoint(he) and va.isdisjoint(he)
    assert tr | va | he == set(BBOB_10D_FUNCS)
    assert (len(tr), len(va), len(he)) == (12, 6, 6)


def test_split_v2_family_stratified():
    for group in (SPLIT_V2_TRAIN, SPLIT_V2_VAL, SPLIT_V2_HELD_OUT):
        fams = {BBOB_FAMILIES[i] for i in group}
        assert fams == set(BBOB_FAMILIES.values())


def test_split_v2_difficult_counts_4_2_2():
    def n_diff(ids):
        return sum(1 for i in ids if i in METABOX_DIFFICULT)

    assert n_diff(SPLIT_V2_TRAIN) == 4
    assert n_diff(SPLIT_V2_VAL) == 2
    assert n_diff(SPLIT_V2_HELD_OUT) == 2


def test_split_manifest_records_family_and_difficulty():
    m = split_manifest("split_v2")
    assert m["manifest_hash"]
    assert m["difficult_counts"] == {"train": 4, "val": 2, "held_out": 2}
    for entry in m["train_entries"] + m["val_entries"] + m["held_out_entries"]:
        assert entry["family"] in BBOB_FAMILIES.values()
        assert entry["metabox_difficulty"] in {"easy", "difficult"}
        # loader must actually return this id
        p = load_function(entry["function_id"])
        assert p.function_id == entry["function_id"]


# ---------------------------------------------------------------------------
# P0-R1-01..03 controller execution
# ---------------------------------------------------------------------------

def test_dsl_v2_scalar_actions():
    spec = fixed_controller_a()
    assert spec["schema_version"].endswith("v2")
    c = compile_controller(spec)
    act = c.select_action(
        {
            "improvement_rate": 0.0,
            "stagnation_steps": 0.0,
            "population_diversity": 1.0,
            "success_fraction": 0.0,
            "budget_fraction": 0.0,
            "generation": 0.0,
        }
    )
    assert act["action"] == "set_F"
    assert act["params"]["value"] == 0.5


def test_range_actions_rejected_in_dsl_v2():
    spec = fixed_controller_a()
    spec["initial_action"] = {"action": "set_F_range", "params": {"low": 0.2, "high": 0.8}}
    with pytest.raises(ControllerValidationError):
        validate_controller_spec(spec)


def test_unsupported_actions_rejected_by_official_de():
    p = load_function(6)
    spec = {
        "schema_version": "aes-controller-dsl-v2",
        "controller_id": "bad_restart",
        "initial_action": {"action": "restart", "params": {"max_fraction": 0.1}},
        "rules": [],
    }
    c = compile_controller(spec)
    with pytest.raises(UnsupportedActionError):
        run_optimizer("DE", p, max_fes=300, seed=1, controller=c)


def test_controlled_de_live_trajectory_triggers_rule():
    """Stagnation rule must actually fire on a real BBOB path (no false positive)."""
    spec = {
        "schema_version": "aes-controller-dsl-v2",
        "controller_id": "stag_switch",
        "initial_action": {"action": "set_F", "params": {"value": 0.5}},
        "rules": [
            {
                "when": {"stagnation_steps": {"op": ">=", "value": 2.0}},
                "then": {"action": "set_F", "params": {"value": 0.8}},
            }
        ],
    }
    ctrl = compile_controller(spec)
    p = load_function(6)
    res = run_controlled_de(p._problem, ctrl, max_fes=800, seed=4)
    assert res.fes == 800
    assert res.independent_fes == 800
    assert len(res.action_events) > 1
    f_used = [e["F_used"] for e in res.action_events]
    assert 0.5 in f_used, "initial F=0.5 must appear"
    assert 0.8 in f_used, "stagnation rule must fire and apply F=0.8"
    fire = next(e for e in res.action_events if e["effect"].get("F") == 0.8)
    assert fire["state"]["stagnation_steps"] >= 2.0
    assert fire["action"]["params"]["value"] == 0.8
    assert fire["F_used"] == 0.8


def test_controlled_de_state_change_selects_different_action():
    ctrl = compile_controller(fixed_controller_a())
    s0 = {
        "improvement_rate": 0.0,
        "stagnation_steps": 0.0,
        "population_diversity": 1.0,
        "success_fraction": 0.0,
        "budget_fraction": 0.0,
        "generation": 0.0,
    }
    s1 = dict(s0, stagnation_steps=20.0)
    a0 = ctrl.select_action(s0)
    a1 = ctrl.select_action(s1)
    assert a0["action"] != a1["action"] or a0["params"] != a1["params"]
    assert a1["params"]["value"] == 0.8


def test_applied_F_CR_match_controller_actions():
    p = load_function(6)
    spec = {
        "schema_version": "aes-controller-dsl-v2",
        "controller_id": "const_f",
        "initial_action": {"action": "set_F", "params": {"value": 0.9}},
        "rules": [],
    }
    ctrl = compile_controller(spec)
    res = run_controlled_de(p._problem, ctrl, max_fes=600, seed=2)
    assert res.applied_F_history[0] == 0.9
    for i, ev in enumerate(res.action_events):
        assert ev["F_used"] == res.applied_F_history[i]
        if ev["effect"].get("applied") == "set_F":
            assert res.applied_F_history[i] == ev["effect"]["F"]
        if ev["effect"].get("applied") == "set_CR":
            assert res.applied_CR_history[i] == ev["effect"]["Cr"]


def test_controlled_de_seed_reproducible():
    ctrl = compile_controller(fixed_controller_a())
    p1 = load_function(6)
    r1 = run_controlled_de(p1._problem, ctrl, max_fes=500, seed=9)
    p2 = load_function(6)
    r2 = run_controlled_de(p2._problem, ctrl, max_fes=500, seed=9)
    assert r1.cost_curve == r2.cost_curve
    assert r1.best_raw_objective == r2.best_raw_objective
    assert r1.fes == r2.fes == 500
    assert r1.independent_fes == r2.independent_fes == 500
    assert [e["action"] for e in r1.action_events] == [e["action"] for e in r2.action_events]


def test_recorded_actions_match_effects():
    p = load_function(6)
    ctrl = compile_controller(fixed_controller_b())
    res = run_controlled_de(p._problem, ctrl, max_fes=500, seed=5)
    for ev in res.action_events:
        name = ev["action"]["action"]
        eff = ev["effect"]
        assert eff["applied"] == name
        if name == "set_F":
            assert eff["F"] == ev["action"]["params"]["value"]
        if name == "set_CR":
            assert eff["Cr"] == ev["action"]["params"]["value"]


def test_controlled_de_success_fraction_wired():
    p = load_function(6)
    ctrl = compile_controller(fixed_controller_a())
    res = run_controlled_de(p._problem, ctrl, max_fes=400, seed=6)
    assert res.action_events[0]["state"]["success_fraction"] == 0.0
    if len(res.action_events) > 1:
        assert res.action_events[1]["state"]["success_fraction"] == pytest.approx(
            res.action_events[0]["success_fraction_this_gen"]
        )


def test_controlled_de_fe_exact_and_metric():
    p = load_function(6)
    ctrl = compile_controller(fixed_controller_a())
    res = run_controlled_de(p._problem, ctrl, max_fes=600, seed=8)
    assert res.fes == res.independent_fes == 600
    assert res.init_fes == 20
    # BBOB F6 has a bias optimum; regret should be computed
    assert res.optimum is not None
    assert res.primary_metric == "regret"
    assert res.best_regret is not None
