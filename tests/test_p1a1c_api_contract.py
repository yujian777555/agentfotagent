"""API contract tests for P1A-1C (mocked HTTP; not a substitute for real preflight)."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from experiments.metabox.p1a1_agent_controller import (
    PROMPT_VERSION,
    AgentAPIError,
    BudgetExceeded,
    LLMBackend,
    P1A1AgentController,
    parse_action,
    render_prompt,
    state_hint,
)


STATE = {
    "generation": 2,
    "F": 0.5,
    "CR": 0.5,
    "stagnation_steps": 6,
    "success_fraction": 0.1,
    "budget_fraction": 0.2,
    "improvement_rate": 0.05,
}


def _resp(payload: dict):
    m = MagicMock()
    m.status = 200
    m.read.return_value = json.dumps(payload).encode()
    m.__enter__ = lambda s: s
    m.__exit__ = lambda s, *a: False
    return m


def _payload(content: str, finish="stop", reasoning="", usage=None):
    return {
        "id": "req-1",
        "model": "deepseek-v4-pro",
        "choices": [
            {
                "finish_reason": finish,
                "message": {"content": content, "reasoning_content": reasoning},
            }
        ],
        "usage": usage
        or {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "completion_tokens_details": {"reasoning_tokens": 0},
        },
    }


def test_prompt_has_no_hint_and_no_pick():
    p = render_prompt(STATE)
    assert "Pick" not in p
    assert "Suggested" not in p
    assert "recommendation" not in p.lower() or "not recommendations" in p
    # no state-derived hint value 0.8 (hint for this state is set_F 0.8)
    assert '"value":0.8}} (CR' in p  # syntax example for CR is present
    # but "Pick F=0.8" style recommendation must be absent
    assert "Pick F=0.8" not in p
    assert "syntax examples only" in p
    assert "Choose one action based on the state" in p


def test_prompt_ignores_hint_controller(monkeypatch):
    p1 = render_prompt(STATE)
    monkeypatch.setattr(
        "experiments.metabox.p1a1_agent_controller.state_hint",
        lambda s: {"action": "noop", "params": {}},
    )
    assert render_prompt(STATE) == p1


def test_normal_json_action():
    b = LLMBackend(api_key="x")
    with patch("urllib.request.urlopen", return_value=_resp(_payload('{"action":"set_CR","params":{"value":0.9}}'))):
        c = P1A1AgentController(b)
        a = c.select_action(STATE)
    assert a == {"action": "set_CR", "params": {"value": 0.9}}
    assert c.events[-1]["valid"] is True
    assert b.stats.requests == 1


def test_empty_content_with_reasoning_is_invalid():
    b = LLMBackend(api_key="x")
    with patch(
        "urllib.request.urlopen",
        return_value=_resp(_payload("", finish="stop", reasoning="long thought")),
    ):
        c = P1A1AgentController(b)
        a = c.select_action(STATE)
    assert a == {"action": "noop", "params": {}}
    assert c.events[-1]["valid"] is False
    assert c.events[-1]["error"] == "empty_model_content"
    assert c.events[-1]["meta"]["reasoning_content_length"] > 0
    assert b.stats.empty_content >= 1


def test_bad_json_is_invalid():
    b = LLMBackend(api_key="x")
    with patch("urllib.request.urlopen", return_value=_resp(_payload("not json"))):
        c = P1A1AgentController(b)
        a = c.select_action(STATE)
    assert a["action"] == "noop"
    assert c.events[-1]["valid"] is False


def test_illegal_action_rejected():
    b = LLMBackend(api_key="x")
    with patch("urllib.request.urlopen", return_value=_resp(_payload('{"action":"exec_python","params":{}}'))):
        c = P1A1AgentController(b)
        a = c.select_action(STATE)
    assert a["action"] == "noop"
    assert c.events[-1]["valid"] is False


def test_out_of_range_F_rejected():
    assert parse_action('{"action":"set_F","params":{"value":0.5}}')["params"]["value"] == 0.5
    with pytest.raises(Exception):
        parse_action('{"action":"set_F","params":{"value":5.0}}')
    with pytest.raises(Exception):
        parse_action('{"action":"set_CR","params":{"value":-0.1}}')


def test_finish_reason_length_recorded():
    b = LLMBackend(api_key="x")
    # Two empty contents in a row (initial + retry) both finish=length
    with patch(
        "urllib.request.urlopen",
        return_value=_resp(_payload("", finish="length", reasoning="truncated")),
    ):
        c = P1A1AgentController(b)
        c.select_action(STATE)
    assert b.stats.finish_reasons.get("length", 0) >= 1
    assert c.events[-1]["meta"]["finish_reason"] == "length"
    assert c.events[-1]["valid"] is False


def test_http_error_raises_and_counts():
    import urllib.error

    b = LLMBackend(api_key="x")
    err = urllib.error.HTTPError("u", 500, "ISE", {}, None)
    with patch("urllib.request.urlopen", side_effect=err):
        with pytest.raises(AgentAPIError):
            P1A1AgentController(b).select_action(STATE)
    assert b.stats.api_failures >= 1


def test_retry_counts_toward_budget():
    b = LLMBackend(api_key="x")
    calls = {"n": 0}

    def fake(*a, **k):
        calls["n"] += 1
        return _resp(_payload(""))

    with patch("urllib.request.urlopen", side_effect=fake):
        c = P1A1AgentController(b)
        c.select_action(STATE)
    assert b.stats.requests == 2  # initial + 1 retry
    assert b.stats.retries == 1


def test_cache_hit_does_not_use_request_budget():
    b = LLMBackend(api_key="x")
    b.cache["k"] = '{"action":"noop","params":{}}'
    c = P1A1AgentController(b)
    # force cache key by pre-seeding after computing? call complete directly
    text, meta = b.complete("p", cache_key="k")
    assert meta["cached"] is True
    assert b.stats.requests == 0
    assert b.stats.cache_hits == 1


def test_budget_exhausted_raises():
    b = LLMBackend(api_key="x")
    b.stats.requests = 140
    with pytest.raises(BudgetExceeded):
        b.complete("p", cache_key="z")
