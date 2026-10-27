"""LLM Agent controller — DeepSeek API contract fix (P1A-1C).

- thinking disabled, response_format=json_object, max_tokens=256
- No state-derived hint and no fixed parameter placeholder in the prompt
- Full response diagnostics (finish_reason, reasoning length, usage, ids)
- Empty content → logged invalid + noop fallback (not a successful decision)
"""
from __future__ import annotations

import hashlib
import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Tuple

from .controller_dsl import DSL_VERSION, validate_controller_spec

PROMPT_VERSION = "p1a1d-agent-v1"
MAX_OUTPUT_TOKENS = 256
MAX_REQUESTS = 140
MAX_RETRIES = 1

# Pure text protocol: NO concrete parameter-value examples (P1A-1D).
PROMPT_TEMPLATE = (
    "You control Differential Evolution parameters. "
    "Output one JSON object and nothing else. "
    "The object has exactly two fields: action and params. "
    "action must be one of: set_F, set_CR, noop. "
    "If action is set_F, params must contain value in [0.1, 1.0]. "
    "If action is set_CR, params must contain value in [0.0, 1.0]. "
    "If action is noop, params must be an empty object. "
    "Choose the action only from the current public state. "
    "Do not output explanations, code, or extra fields. "
    "State: gen={gen} F={cur_F} CR={cur_Cr} stag={stag} succ={succ} budget={budget} improve={imp}."
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
    reasoning_tokens: int = 0
    cache_hits: int = 0
    invalid_responses: int = 0
    api_failures: int = 0
    empty_content: int = 0
    finish_reasons: Dict[str, int] = field(default_factory=dict)
    total_cost_usd_estimate: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "requests": self.requests,
            "retries": self.retries,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "reasoning_tokens": self.reasoning_tokens,
            "cache_hits": self.cache_hits,
            "invalid_responses": self.invalid_responses,
            "api_failures": self.api_failures,
            "empty_content": self.empty_content,
            "finish_reasons": dict(self.finish_reasons),
            "total_cost_usd_estimate": self.total_cost_usd_estimate,
            "note": "DeepSeek returns usage tokens; USD cost not provided by API",
        }


@dataclass
class LLMBackend:
    api_key: str
    base_url: str = "https://api.deepseek.com/v1"
    model: str = "deepseek-v4-pro"
    stats: LLMStats = field(default_factory=LLMStats)
    cache: Dict[str, str] = field(default_factory=dict)

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
            "thinking": {"type": "disabled"},
            "response_format": {"type": "json_object"},
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
                    http_status = getattr(resp, "status", 200)
                    payload = json.loads(resp.read().decode("utf-8"))
                choice = (payload.get("choices") or [{}])[0]
                msg = choice.get("message") or {}
                usage = payload.get("usage") or {}
                details = usage.get("completion_tokens_details") or {}
                finish_reason = choice.get("finish_reason")
                if finish_reason:
                    self.stats.finish_reasons[str(finish_reason)] = (
                        self.stats.finish_reasons.get(str(finish_reason), 0) + 1
                    )
                self.stats.prompt_tokens += int(usage.get("prompt_tokens") or 0)
                self.stats.completion_tokens += int(usage.get("completion_tokens") or 0)
                self.stats.reasoning_tokens += int(details.get("reasoning_tokens") or 0)
                text = msg.get("content") or ""
                diag = {
                    "cached": False,
                    "model": payload.get("model", self.model),
                    "request_id": payload.get("id"),
                    "http_status": http_status,
                    "finish_reason": finish_reason,
                    "content_length": len(text),
                    "reasoning_content_length": len(msg.get("reasoning_content") or ""),
                    "usage": usage,
                    "reasoning_tokens": details.get("reasoning_tokens"),
                }
                if not text.strip():
                    self.stats.empty_content += 1
                    self.stats.invalid_responses += 1
                    if attempt < MAX_RETRIES:
                        continue
                    diag["empty_content"] = True
                    return "", diag
                self.cache[cache_key] = text
                return text, diag
            except urllib.error.HTTPError as exc:
                last_err = f"HTTPError {exc.code}"
                self.stats.api_failures += 1
                if attempt < MAX_RETRIES:
                    continue
                raise AgentAPIError(f"HTTP {exc.code}: {exc.reason}") from exc
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError) as exc:
                last_err = str(exc)
                self.stats.api_failures += 1
                if attempt < MAX_RETRIES:
                    time.sleep(0.3)
                    continue
        raise AgentAPIError(f"LLM request failed after retries: {last_err}")


def state_hint(state: Mapping[str, Any]) -> Dict[str, Any]:
    """Deterministic hint controller (hint_only baseline + post-hoc comparison)."""
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


_state_hint = state_hint


def render_prompt(state_d: Mapping[str, Any]) -> str:
    return PROMPT_TEMPLATE.format(
        gen=state_d.get("generation", 0),
        cur_F=state_d.get("F", state_d.get("cur_F", 0.5)),
        cur_Cr=state_d.get("CR", state_d.get("cur_Cr", 0.5)),
        stag=int(float(state_d.get("stagnation_steps", 0) or 0)),
        succ=round(float(state_d.get("success_fraction", 0) or 0), 3),
        budget=round(float(state_d.get("budget_fraction", 0) or 0), 3),
        imp=round(float(state_d.get("improvement_rate", 0) or 0), 4),
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
        raise ValueError(f"no JSON object in response: {raw[:80]!r}")
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
    def __init__(self, backend: LLMBackend, controller_id: str = "llm_agent_v3") -> None:
        self.backend = backend
        self.controller_id = controller_id
        self.controller_hash = hashlib.sha256(f"{PROMPT_VERSION}:{controller_id}".encode()).hexdigest()
        self.events: List[Dict[str, Any]] = []
        self._fallback = {"action": "noop", "params": {}}

    def select_action(self, state: Any) -> Dict[str, Any]:
        state_d = dict(state)
        prompt = render_prompt(state_d)
        cache_key = hashlib.sha256(
            json.dumps([PROMPT_VERSION, prompt], separators=(",", ":")).encode()
        ).hexdigest()
        raw = ""
        meta: Dict[str, Any] = {}
        try:
            raw, meta = self.backend.complete(prompt, cache_key=cache_key)
        except BudgetExceeded:
            raise
        except AgentAPIError as exc:
            hint = state_hint(state_d)
            self.events.append(
                {
                    "state": state_d,
                    "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                    "hint_action": hint,
                    "llm_action": None,
                    "raw_response": raw,
                    "action": self._fallback,
                    "meta": meta,
                    "valid": False,
                    "error": f"api:{exc}",
                    "deviates_from_hint": None,
                }
            )
            raise

        hint = state_hint(state_d)  # post-hoc only
        if meta.get("empty_content") or not (raw or "").strip():
            self.events.append(
                {
                    "state": state_d,
                    "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
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

        try:
            action = parse_action(raw)
            self.events.append(
                {
                    "state": state_d,
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
        except Exception as exc:
            self.backend.stats.invalid_responses += 1
            self.events.append(
                {
                    "state": state_d,
                    "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                    "hint_action": hint,
                    "llm_action": None,
                    "raw_response": raw,
                    "action": self._fallback,
                    "meta": meta,
                    "valid": False,
                    "error": f"parse:{exc}",
                    "deviates_from_hint": None,
                }
            )
            return self._fallback


class HintOnlyController:
    controller_id = "hint_only"
    controller_hash = "static-hint-only-v1"

    def select_action(self, state: Any) -> Dict[str, Any]:
        return state_hint(dict(state))
