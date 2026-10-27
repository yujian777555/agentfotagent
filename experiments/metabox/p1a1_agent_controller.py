"""LLM Agent controller for P1A-1B (deconfounded).

Prompt contains ONLY public state, current parameters, and legal DSL actions.
No state-derived recommendation (hint) enters the prompt, cache key, or any
branch that influences the model. ``_state_hint`` is a separate deterministic
controller used for the hint_only baseline and for post-hoc comparison only.
"""
from __future__ import annotations

import hashlib
import json
import math
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Tuple

from .controller_dsl import DSL_VERSION, validate_controller_spec

PROMPT_VERSION = "p1a1b-agent-v3"
MAX_OUTPUT_TOKENS = 128
MAX_REQUESTS = 100
MAX_RETRIES = 1

# DeepSeek reasoning models emit empty content unless the prompt ends with a
# concrete "Pick <param>=<number>." instruction. We use a FIXED format dummy
# (0.5) that is independent of state; hint values never enter this prompt.
FORMAT_DUMMY_F = 0.5
PROMPT_TEMPLATE = (
    "You are a controller. User gives state. "
    'You reply ONLY {{"action":"set_F","params":{{"value":V}}}} or '
    '{{"action":"set_CR","params":{{"value":V}}}} or {{"action":"noop","params":{{}}}}. '
    "State: gen={gen} F={cur_F} CR={cur_Cr} stag={stag} succ={succ} budget={budget}. "
    "Pick F={dummy}."
)


class AgentAPIError(RuntimeError):
    pass


class BudgetExceeded(RuntimeError):
    pass


@dataclass
class LLMStats:
    requests: int = 0
    retries: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cache_hits: int = 0
    invalid_responses: int = 0
    api_failures: int = 0
    total_cost_usd_estimate: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "requests": self.requests,
            "retries": self.retries,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "cache_hits": self.cache_hits,
            "invalid_responses": self.invalid_responses,
            "api_failures": self.api_failures,
            "total_cost_usd_estimate": self.total_cost_usd_estimate,
            "note": "DeepSeek API does not return USD cost; token counts are authoritative",
        }


@dataclass
class LLMBackend:
    api_key: str
    base_url: str = "https://api.deepseek.com/v1"
    model: str = "deepseek-v4-pro"
    stats: LLMStats = field(default_factory=LLMStats)
    cache: Dict[str, str] = field(default_factory=dict)
    log: List[Dict[str, Any]] = field(default_factory=list)

    def complete(self, prompt: str, *, cache_key: str) -> Tuple[str, Dict[str, Any]]:
        if self.stats.requests >= MAX_REQUESTS:
            raise BudgetExceeded(f"request budget exhausted ({MAX_REQUESTS})")
        if cache_key in self.cache:
            self.stats.cache_hits += 1
            return self.cache[cache_key], {"cached": True, "model": self.model}

        body = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": MAX_OUTPUT_TOKENS,
            "temperature": 0.0,
        }
        data = json.dumps(body).encode("utf-8")
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        last_err = None
        for attempt in range(1 + MAX_RETRIES):
            if self.stats.requests >= MAX_REQUESTS:
                raise BudgetExceeded(f"request budget exhausted ({MAX_REQUESTS})")
            self.stats.requests += 1
            if attempt > 0:
                self.stats.retries += 1
            req = urllib.request.Request(
                f"{self.base_url.rstrip('/')}/chat/completions", data=data, headers=headers, method="POST"
            )
            try:
                with urllib.request.urlopen(req, timeout=60) as resp:
                    payload = json.loads(resp.read().decode("utf-8"))
                usage = payload.get("usage") or {}
                self.stats.prompt_tokens += int(usage.get("prompt_tokens") or 0)
                self.stats.completion_tokens += int(usage.get("completion_tokens") or 0)
                text = payload["choices"][0]["message"]["content"]
                if not (text or "").strip():
                    self.stats.invalid_responses += 1
                    if attempt < MAX_RETRIES:
                        continue
                    # Invalid model output: caller records fallback; do not raise
                    # as if the API transport failed.
                    return "", {
                        "cached": False,
                        "model": payload.get("model", self.model),
                        "usage": usage,
                        "id": payload.get("id"),
                        "empty_content": True,
                    }
                meta = {
                    "cached": False,
                    "model": payload.get("model", self.model),
                    "usage": usage,
                    "id": payload.get("id"),
                }
                self.cache[cache_key] = text
                return text, meta
            except (urllib.error.HTTPError, urllib.error.URLError, KeyError, json.JSONDecodeError) as exc:
                last_err = exc
                self.stats.api_failures += 1
                if attempt < MAX_RETRIES:
                    time.sleep(0.5)
                    continue
        raise AgentAPIError(f"LLM request failed after retries: {last_err}")


def state_hint(state: Mapping[str, Any]) -> Dict[str, Any]:
    """Deterministic hint controller (hint_only baseline + post-hoc comparison).

    MUST NOT be called on the LLM prompt/cache path.
    """
    stag = float(state.get("stagnation_steps", 0) or 0)
    budget = float(state.get("budget_fraction", 0) or 0)
    succ = float(state.get("success_fraction", 0) or 0)
    if stag >= 5:
        return {"action": "set_F", "params": {"value": 0.8}}
    if budget >= 0.8:
        return {"action": "set_CR", "params": {"value": 0.3}}
    if succ <= 0.05:
        return {"action": "set_F", "params": {"value": 0.7}}
    return {"action": "set_F", "params": {"value": 0.5}}


# Back-compat alias
_state_hint = state_hint


def render_prompt(state_d: Mapping[str, Any]) -> str:
    """Public-state prompt + fixed format dummy. No state-derived hint."""
    return PROMPT_TEMPLATE.format(
        gen=state_d.get("generation", 0),
        cur_F=state_d.get("F", state_d.get("cur_F", 0.5)),
        cur_Cr=state_d.get("CR", state_d.get("cur_Cr", 0.5)),
        stag=int(float(state_d.get("stagnation_steps", 0) or 0)),
        succ=round(float(state_d.get("success_fraction", 0) or 0), 3),
        budget=round(float(state_d.get("budget_fraction", 0) or 0), 3),
        dummy=FORMAT_DUMMY_F,
    )


def parse_action(raw: str) -> Dict[str, Any]:
    text = (raw or "").strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end < start:
        raise ValueError(f"no JSON object in response: {raw!r}")
    obj = json.loads(text[start : end + 1])
    spec = {
        "schema_version": DSL_VERSION,
        "controller_id": "tmp",
        "initial_action": obj,
        "rules": [],
    }
    validate_controller_spec(spec)
    return {"action": obj["action"], "params": obj.get("params") or {}}


class P1A1AgentController:
    def __init__(self, backend: LLMBackend, controller_id: str = "llm_agent_v2") -> None:
        self.backend = backend
        self.controller_id = controller_id
        self.controller_hash = hashlib.sha256(f"{PROMPT_VERSION}:{controller_id}".encode()).hexdigest()
        self.events: List[Dict[str, Any]] = []
        self._fallback = {"action": "noop", "params": {}}

    def select_action(self, state: Any) -> Dict[str, Any]:
        state_d = dict(state)
        prompt = render_prompt(state_d)
        # Cache key: prompt text only — never includes hint.
        cache_key = hashlib.sha256(
            json.dumps([PROMPT_VERSION, prompt], separators=(",", ":")).encode()
        ).hexdigest()
        raw = None
        meta: Dict[str, Any] = {}
        try:
            raw, meta = self.backend.complete(prompt, cache_key=cache_key)
            if meta.get("empty_content") or not (raw or "").strip():
                hint = state_hint(state_d)
                self.backend.stats.invalid_responses += 1
                self.events.append(
                    {
                        "state": state_d,
                        "prompt": prompt,
                        "hint_action": hint,
                        "llm_action": None,
                        "raw_response": raw,
                        "action": self._fallback,
                        "meta": meta,
                        "valid": False,
                        "error": "empty_model_content",
                        "deviates_from_hint": None,
                    }
                )
                return self._fallback
            action = parse_action(raw)
            hint = state_hint(state_d)  # post-hoc only
            self.events.append(
                {
                    "state": state_d,
                    "prompt": prompt,
                    "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                    "hint_action": hint,
                    "llm_action": action,
                    "raw_response": raw,
                    "action": action,
                    "meta": meta,
                    "valid": True,
                    "error": None,
                    "deviates_from_hint": action != hint,
                }
            )
            return action
        except BudgetExceeded:
            raise
        except AgentAPIError as exc:
            hint = state_hint(state_d)
            self.events.append(
                {
                    "state": state_d,
                    "prompt": prompt,
                    "hint_action": hint,
                    "llm_action": None,
                    "raw_response": raw,
                    "action": self._fallback,
                    "meta": meta,
                    "valid": False,
                    "error": str(exc),
                    "api_failure": True,
                    "deviates_from_hint": None,
                }
            )
            raise
        except Exception as exc:
            self.backend.stats.invalid_responses += 1
            hint = state_hint(state_d)
            self.events.append(
                {
                    "state": state_d,
                    "prompt": prompt,
                    "hint_action": hint,
                    "llm_action": None,
                    "raw_response": raw,
                    "action": self._fallback,
                    "meta": meta,
                    "valid": False,
                    "error": str(exc),
                    "deviates_from_hint": None,
                }
            )
            return self._fallback


class HintOnlyController:
    """Executes state_hint(state) with no LLM call."""

    controller_id = "hint_only"
    controller_hash = "static-hint-only-v1"

    def select_action(self, state: Any) -> Dict[str, Any]:
        return state_hint(dict(state))
