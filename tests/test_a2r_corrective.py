"""Phase-1A-2R regression tests: rand/2, config, first-match, FE-safe inject, ablations."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from experiments.metabox.agent_assisted_ec.mechanism_dsl import (
    compile_mechanism,
    validate_mechanism,
)
from experiments.metabox.agent_assisted_ec.multi_de import mutate, run_multi_de
from experiments.metabox.agent_assisted_ec.run_corrective_repro import (
    deterministic_spec,
    fixed_classic_spec,
    random_mechanism,
)


class Quad:
    dim = 6
    lb = -20.0
    ub = 20.0
    optimum = 0.0

    def reset(self):
        pass

    def eval(self, x):
        x = np.asarray(x).reshape(-1)
        return float(np.dot(x, x))


def test_rand2_uses_five_distinct_indices():
    pop = np.arange(60, dtype=float).reshape(10, 6)
    rng = np.random.RandomState(0)
    seen = set()
    for _ in range(20):
        v = mutate("rand/2/bin", pop, i=3, rng_np=rng, F=0.5, best_idx=0)
        assert v.shape == (6,)
    # formula check with forced indices
    class FixedRng:
        def __init__(self):
            self.n = 0

        def choice(self, others, size, replace=False):
            self.n += 1
            assert replace is False
            assert size == 5
            return [0, 1, 2, 4, 5]

    fr = FixedRng()
    v = mutate("rand/2/bin", pop, i=3, rng_np=fr, F=0.5, best_idx=9)
    expected = pop[0] + 0.5 * (pop[1] - pop[2]) + 0.5 * (pop[4] - pop[5])
    assert np.allclose(v, expected)
    # i=3 not in {0,1,2,4,5}
    assert 3 not in [0, 1, 2, 4, 5]


def test_rand2_insufficient_population_raises():
    pop = np.zeros((5, 4))  # only 4 others when i=0
    with pytest.raises(ValueError):
        mutate("rand/2/bin", pop, i=0, rng_np=np.random.RandomState(1), F=0.5, best_idx=1)


def test_all_operators_run():
    for op in ("rand/1/bin", "current-to-best/1/bin", "rand/2/bin", "best/1/bin"):
        spec = {
            "schema_version": "aes-mech-dsl-v1",
            "mechanism_id": f"op_{op}",
            "description": "",
            "rules": [{"when": {"stagnation_steps": {"op": ">=", "value": 999}},
                       "then": {"action": "noop", "params": {}}}],
            "default": {"action": "set_operator", "params": {"operator": op}},
        }
        res = run_multi_de(Quad(), compile_mechanism(spec), max_fes=60, seed=1,
                           np_size=10, F=0.5, Cr=0.9)
        assert res.fes == res.independent_fes == 60


def test_fixed_classic_config_F_CR():
    spec = fixed_classic_spec()
    m = compile_mechanism(spec)
    p = Quad()
    res = run_multi_de(p, m, max_fes=40, seed=2, np_size=10, F=0.5, Cr=0.9)
    # default action is set_operator rand/1; base F/CR used
    assert res.action_events[0]["F"] == 0.5
    assert res.action_events[0]["CR"] == 0.9


def test_deterministic_rules_all_reachable():
    spec = deterministic_spec()
    m = compile_mechanism(spec)
    assert len(m.spec["rules"]) == 1  # no unreachable duplicate
    a1 = m.select({"stagnation_steps": 6, "success_fraction": 0.2,
                   "population_diversity": 30, "improvement_rate": 0, "budget_fraction": 0.2})
    assert a1["params"]["operator"] == "rand/2/bin"
    a2 = m.select({"stagnation_steps": 0, "success_fraction": 0.2,
                   "population_diversity": 30, "improvement_rate": 0, "budget_fraction": 0.2})
    assert a2["params"]["operator"] == "rand/1/bin"


def test_first_match_rule_priority():
    spec = {
        "schema_version": "aes-mech-dsl-v1",
        "mechanism_id": "fm",
        "description": "",
        "rules": [
            {"when": {"stagnation_steps": {"op": ">=", "value": 5.0}},
             "then": {"action": "set_operator", "params": {"operator": "rand/2/bin"}}},
            {"when": {"population_diversity": {"op": "<=", "value": 30.0}},
             "then": {"action": "inject_diversity", "params": {}}},
        ],
        "default": {"action": "set_operator", "params": {"operator": "rand/1/bin"}},
    }
    m = compile_mechanism(spec)
    # both conditions true → first rule wins
    a = m.select({"stagnation_steps": 6, "population_diversity": 20,
                  "success_fraction": 0, "improvement_rate": 0, "budget_fraction": 0.1})
    assert a["action"] == "set_operator"
    # only second condition → inject
    a2 = m.select({"stagnation_steps": 0, "population_diversity": 20,
                   "success_fraction": 0, "improvement_rate": 0, "budget_fraction": 0.1})
    assert a2["action"] == "inject_diversity"


def test_inject_never_exceeds_fe_budget():
    spec = {
        "schema_version": "aes-mech-dsl-v1",
        "mechanism_id": "inj",
        "description": "",
        "rules": [{"when": {"stagnation_steps": {"op": ">=", "value": 0.0}},
                   "then": {"action": "inject_diversity", "params": {}}}],
        "default": {"action": "noop", "params": {}},
    }
    m = compile_mechanism(spec)
    res = run_multi_de(Quad(), m, max_fes=25, seed=3, np_size=10, F=0.5, Cr=0.9)
    assert res.fes == 25
    assert res.independent_fes == 25
    for ev in res.inject_events:
        assert ev["resampled"] <= ev["planned"]
        assert ev["reason"] in (None, "insufficient_FE", "FE_exhausted_mid_inject")


def test_mech3_action_trace_first_match():
    """Frozen agent_mech_3: when both stag and div fire, operator switch wins."""
    frozen = json.loads(
        (ROOT / "results" / "agent_assisted_ec" / "manifest_a2-1fc40335619e-clean-20261028T111308.json").read_text(encoding="utf-8")
    )
    s = next(x for x in frozen["agent_mechanisms"] if x["mechanism_id"] == "agent_mech_3")
    m = compile_mechanism(s)
    # both conditions
    a = m.select({"stagnation_steps": 6, "population_diversity": 20,
                  "success_fraction": 0.1, "improvement_rate": 0, "budget_fraction": 0.2})
    assert a["action"] == "set_operator" and a["params"]["operator"] == "rand/2/bin"
    # only div
    a2 = m.select({"stagnation_steps": 0, "population_diversity": 20,
                   "success_fraction": 0.1, "improvement_rate": 0, "budget_fraction": 0.2})
    assert a2["action"] == "inject_diversity"
    res = run_multi_de(Quad(), m, max_fes=60, seed=4, np_size=10, F=0.5, Cr=0.9)
    # recorded actions consistent
    for ev in res.action_events:
        if ev["effect"]["rule_index"] == 0:
            assert ev["action"]["action"] == "set_operator"
        elif ev["effect"]["rule_index"] == 1:
            assert ev["action"]["action"] == "inject_diversity"


def test_random_mech_scales_and_seed_reproducible():
    import random

    r1 = random_mechanism(random.Random(5), "m")
    r2 = random_mechanism(random.Random(5), "m")
    assert r1 == r2
    for rule in r1["rules"]:
        feat = list(rule["when"])[0]
        thr = rule["when"][feat]["value"]
        lo, hi = {"stagnation_steps": (0, 80), "success_fraction": (0, 1),
                  "population_diversity": (15, 60), "improvement_rate": (0, 1),
                  "budget_fraction": (0, 1)}[feat]
        assert lo <= thr <= hi


def test_ablations_from_mech3_structure():
    frozen = json.loads(
        (ROOT / "results" / "agent_assisted_ec" / "manifest_a2-1fc40335619e-clean-20261028T111308.json").read_text(encoding="utf-8")
    )
    s = next(x for x in frozen["agent_mechanisms"] if x["mechanism_id"] == "agent_mech_3")
    ab1 = {**s, "mechanism_id": "ablate_no_stag",
           "rules": [r for r in s["rules"] if "stagnation_steps" not in r["when"]]}
    ab2 = {**s, "mechanism_id": "ablate_no_div",
           "rules": [r for r in s["rules"] if "population_diversity" not in r["when"]]}
    assert len(validate_mechanism(ab1)["rules"]) == 1
    assert len(validate_mechanism(ab2)["rules"]) == 1
    assert validate_mechanism(ab1)["rules"][0]["then"]["action"] == "inject_diversity"
    assert validate_mechanism(ab2)["rules"][0]["then"]["action"] == "set_operator"
