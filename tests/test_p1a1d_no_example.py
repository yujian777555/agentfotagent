"""P1A-1D: no-example prompt protocol tests (mocked; real preflight is separate)."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from experiments.metabox.p1a1_agent_controller import (
    PROMPT_TEMPLATE,
    PROMPT_VERSION,
    LLMBackend,
    P1A1AgentController,
    render_prompt,
    state_hint,
)


STATE = {
    "generation": 3,
    "F": 0.5,
    "CR": 0.5,
    "stagnation_steps": 8,
    "success_fraction": 0.1,
    "budget_fraction": 0.4,
    "improvement_rate": 0.05,
}


def test_template_has_no_concrete_action_json_example():
    assert '{"action"' not in PROMPT_TEMPLATE
    assert "0.35" not in PROMPT_TEMPLATE
    assert "0.8" not in PROMPT_TEMPLATE
    assert "set_F" in PROMPT_TEMPLATE  # action names still specified
    assert "set_CR" in PROMPT_TEMPLATE
    assert "noop" in PROMPT_TEMPLATE


def test_prompt_contains_state_but_no_hint():
    p = render_prompt(STATE)
    assert "stag=8" in p
    assert "budget=0.4" in p
    assert "gen=3" in p
    hint = state_hint(STATE)
    # hint for this state is set_F 0.8 — must not appear as recommendation
    assert "Pick" not in p
    assert "Suggested" not in p
    assert "recommendation" not in p.lower()


def test_hint_change_does_not_change_prompt(monkeypatch):
    p1 = render_prompt(STATE)
    monkeypatch.setattr(
        "experiments.metabox.p1a1_agent_controller.state_hint",
        lambda s: {"action": "set_CR", "params": {"value": 0.1}},
    )
    assert render_prompt(STATE) == p1


def test_cache_key_includes_new_prompt_version():
    import hashlib

    prompt = render_prompt(STATE)
    k_new = hashlib.sha256(json.dumps([PROMPT_VERSION, prompt], separators=(",", ":")).encode()).hexdigest()
    k_old = hashlib.sha256(json.dumps(["p1a1c-agent-v1", prompt], separators=(",", ":")).encode()).hexdigest()
    assert k_new != k_old
    assert PROMPT_VERSION == "p1a1d-agent-v1"


def _resp(payload: dict):
    m = MagicMock()
    m.status = 200
    m.read.return_value = json.dumps(payload).encode()
    m.__enter__ = lambda s: s
    m.__exit__ = lambda s, *a: False
    return m


def test_normal_json_still_parses():
    b = LLMBackend(api_key="x")
    body = {
        "id": "r1",
        "model": "deepseek-v4-pro",
        "choices": [{"finish_reason": "stop", "message": {"content": '{"action":"set_CR","params":{"value":0.25}}', "reasoning_content": ""}}],
        "usage": {"prompt_tokens": 5, "completion_tokens": 10, "completion_tokens_details": {"reasoning_tokens": 0}},
    }
    with patch("urllib.request.urlopen", return_value=_resp(body)):
        a = P1A1AgentController(b).select_action(STATE)
    assert a == {"action": "set_CR", "params": {"value": 0.25}}


def test_illegal_and_bounds_still_rejected():
    from experiments.metabox.p1a1_agent_controller import parse_action

    for bad in (
        '{"action":"exec","params":{}}',
        '{"action":"set_F","params":{"value":9}}',
        '{"action":"set_CR","params":{"value":-1}}',
    ):
        try:
            parse_action(bad)
            raise AssertionError("should reject " + bad)
        except Exception:
            pass
