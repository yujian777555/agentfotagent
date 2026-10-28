"""Phase-1A-3N2 unit tests: propensity logging, refusal, config freeze."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.phase1a3n2_final_battery import (
    CONFIG,
    CONFIG_HASH,
    DRLearner,
    IPWLearner,
    QualityResidualUCB,
    Transition,
    behavior_propensity,
    generate_data,
    true_mean,
)


def test_config_frozen_hash():
    assert CONFIG["seeds"] == [11, 22, 33, 44, 55, 66, 77, 88, 99, 110]
    assert len(CONFIG_HASH) == 16


def test_behavior_propensity_sums_to_one():
    for scenario in ("A_no_confounding", "C_endogenous_quality"):
        for q in (0.1, 0.9):
            e = behavior_propensity(scenario, 0, q, 0)
            assert abs(sum(e.values()) - 1.0) < 1e-9
            assert all(v >= 0 for v in e.values())


def test_endogenous_quality_shifts_mass():
    e_lo = behavior_propensity("C_endogenous_quality", 0, 0.1, 0)
    e_hi = behavior_propensity("C_endogenous_quality", 0, 0.9, 0)
    assert e_hi[0] > e_lo[0]  # high-q → more op0
    assert e_lo[1] > e_hi[1]


def test_zero_propensity_cell_in_E():
    e = behavior_propensity("E_no_support", 1, 0.5, 0)
    assert e[2] == 0.0
    e2 = behavior_propensity("E_no_support", 0, 0.5, 0)
    assert e2[2] > 0.0


def test_empirical_frequency_close_to_propensity():
    data = generate_data("C_endogenous_quality", 11)
    assert len(data) == 600
    emp = {a: 0 for a in range(3)}
    for tr in data:
        emp[tr.a] += 1
    exp = {a: sum(tr.e_vec[a] for tr in data) for a in range(3)}
    for a in range(3):
        # Monte Carlo tolerance ~ 4 sigma of binomial
        tol = 0.06
        assert abs(emp[a] / len(data) - exp[a] / len(data)) < tol


def test_ipw_refuses_on_zero_support():
    ipw = IPWLearner()
    # feed zero-propensity observations for (b=1,a=2)
    for i in range(5):
        tr = Transition(b=1, q=0.5, t=i, a=2, e=0.0, e_vec={0: 0.5, 1: 0.5, 2: 0.0}, r=0.1, mu=0.1, best_a=0, mu_best=0.3)
        ipw.observe(tr)
    a, status = ipw.decide(1, 0.5, 0)
    # after zero-support flag, op2 excluded; other ops available
    assert status == "ok" or a >= 0
    # force all three unsupported
    for a2 in (0, 1):
        for i in range(3):
            tr = Transition(b=1, q=0.5, t=i, a=a2, e=0.0, e_vec={}, r=0.0, mu=0.0, best_a=0, mu_best=0.0)
            ipw.observe(tr)
    a2, status2 = ipw.decide(1, 0.5, 1)
    assert a2 == -1 and status2 == "UNIDENTIFIABLE"


def test_small_nonzero_propensity_not_refused():
    ipw = IPWLearner()
    tr = Transition(b=0, q=0.5, t=0, a=2, e=0.001, e_vec={}, r=0.2, mu=0.2, best_a=0, mu_best=0.3)
    ipw.observe(tr)
    assert ipw.zero_support[(0, 2)] is False


def test_ipw_weight_clip_recorded():
    ipw = IPWLearner()
    tr = Transition(b=0, q=0.5, t=0, a=0, e=0.001, e_vec={}, r=0.1, mu=0.1, best_a=0, mu_best=0.1)
    ipw.observe(tr)
    assert ipw.clips >= 1


def test_dr_refuses_when_no_support():
    dr = DRLearner()
    for a in range(3):
        for i in range(2):
            tr = Transition(b=1, q=0.5, t=i, a=a, e=0.0, e_vec={}, r=0.0, mu=0.0, best_a=0, mu_best=0.0)
            dr.observe(tr)
    a, status = dr.decide(1, 0.5, 0)
    assert a == -1 and status == "UNIDENTIFIABLE"


def test_true_mean_matches_scenario_formula():
    assert abs(true_mean("A_no_confounding", 0, 0, 0.5, 0) - 0.35) < 1e-9
    assert abs(true_mean("C_endogenous_quality", 0, 0, 1.0, 0) - (0.10 + 0.6 + 0.05)) < 1e-9
