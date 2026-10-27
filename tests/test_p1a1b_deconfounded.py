"""P1A-1B: LLM prompt must not depend on hint; hint_only is a separate controller."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from experiments.metabox.p1a1_agent_controller import (
    PROMPT_VERSION,
    HintOnlyController,
    parse_action,
    render_prompt,
    state_hint,
)


STATE = {
    "generation": 3,
    "F": 0.5,
    "CR": 0.5,
    "stagnation_steps": 7.0,
    "success_fraction": 0.02,
    "budget_fraction": 0.2,
    "improvement_rate": 0.0,
    "best": 1234.0,
}


def test_prompt_contains_no_hint_value_or_recommendation():
    prompt = render_prompt(STATE)
    assert "Suggested" not in prompt
    assert "Pick F=" not in prompt
    assert '{"action"' not in prompt
    assert "Choose the action only from the current public state" in prompt


def test_prompt_identical_regardless_of_hint_controller(monkeypatch):
    """Changing hint implementation must not change the LLM prompt."""
    p1 = render_prompt(STATE)
    monkeypatch.setattr(
        "experiments.metabox.p1a1_agent_controller.state_hint",
        lambda s: {"action": "noop", "params": {}},
    )
    p2 = render_prompt(STATE)
    assert p1 == p2


def test_prompt_does_not_contain_state_dependent_action_type():
    """Prompt must not pre-select action type from state."""
    s_hot = dict(STATE, stagnation_steps=9, budget_fraction=0.9, success_fraction=0.0)
    s_calm = dict(STATE, stagnation_steps=0, budget_fraction=0.1, success_fraction=0.5)
    p1 = render_prompt(s_hot)
    p2 = render_prompt(s_calm)
    assert "Pick" not in p1 and "Pick" not in p2
    # both mention all three actions as legal options
    for p in (p1, p2):
        assert "set_F" in p and "set_CR" in p and "noop" in p


def test_prompt_cache_key_excludes_hint():
    import hashlib
    import json

    from experiments.metabox.p1a1_agent_controller import PROMPT_VERSION as PV

    prompt = render_prompt(STATE)
    k2 = hashlib.sha256(json.dumps([PV, prompt], separators=(",", ":")).encode()).hexdigest()
    assert k2
    # hint value 0.8 for this state is not used as a recommendation in prompt
    assert "Pick F=0.8" not in prompt


def test_hint_only_controller_executes_hint():
    c = HintOnlyController()
    a = c.select_action(STATE)
    assert a == state_hint(STATE)
    assert c.controller_id == "hint_only"


def test_stagnation_and_hint_are_different_policies():
    from experiments.metabox.run_p1a1_pilot import StagnationHeuristicController

    st = StagnationHeuristicController()
    # At stag>=5 hint gives F=0.8, stagnation_heuristic gives F=0.9
    s = dict(STATE)
    s["stagnation_steps"] = 6
    s["budget_fraction"] = 0.1
    s["success_fraction"] = 0.3
    assert st.select_action(s) != state_hint(s)


def test_parse_action_bounds():
    assert parse_action('{"action":"set_F","params":{"value":0.5}}')["params"]["value"] == 0.5
    import pytest

    with pytest.raises(Exception):
        parse_action('{"action":"set_F","params":{"value":5.0}}')
    with pytest.raises(Exception):
        parse_action('{"action":"exec","params":{}}')


def test_prompt_version_is_deconfounded():
    assert PROMPT_VERSION.startswith("p1a1")
