"""LLM Agent controller for P1A-1.

The Agent receives only public search-state features and must emit a DSL action
(JSON). No arbitrary code, no hidden optimum, no test labels. Invalid actions are
rejected and recorded; the API is never silently swapped for a mock.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .controller_dsl import DSL_VERSION, compile_controller, validate_controller_spec

PROMPT_VERSION = "p1a1-agent-v3"
MAX_OUTPUT_TOKENS = 192  # content is one JSON line; headroom for short reasoning
MAX_REQUESTS = 100
MAX_RETRIES = 1

PROMPT_TEMPLATE = """You are a DE parameter controller. Reply ONLY with one JSON object, no markdown.
Allowed: set_F value in [0.1,1.0], set_CR value in [0.0,1.0], or noop.
State: gen={gen} F={cur_F} CR={cur_Cr} best={best} improve={imp} stag={stag} succ={succ} budget={budget} div={div}
Pick a reasonable next parameter action."""


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
            "note": "cost estimate from reported tokens × published prices; if service omits usage, cost stays 0 and token counts are authoritative",
        }


@dataclass
class LLMBackend:
    api_key: str
    base_url: str = "https://api.deepseek.com/v1"
    model: str = "deepseek-flash"
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
            "temperature": 0.2,
        }
        data = json.dumps(body).encode("utf-8")
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
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
                        self.stats.retries += 1
                        self.stats.requests += 1
                        # compact retry prompt
                        body2 = dict(body)
                        body2["max_tokens"] = 320
                        data = json.dumps(body2).encode("utf-8")
                        continue
                    raise AgentAPIError("empty model content after retries")
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


class P1A1AgentController:
    """Controller-compatible object: select_action(state) -> DSL action dict."""

    def __init__(self, backend: LLMBackend, controller_id: str = "llm_agent_v1") -> None:
        self.backend = backend
        self.controller_id = controller_id
        self.controller_hash = hashlib.sha256(f"{PROMPT_VERSION}:{controller_id}".encode()).hexdigest()
        self.events: List[Dict[str, Any]] = []
        self._fallback = {
            "action": "noop",
            "params": {},
        }

    def select_action(self, state: MappingLike) -> Dict[str, Any]:
        state_d = dict(state)
        prompt = PROMPT_TEMPLATE.format(
            gen=state_d.get("generation", 0),
            cur_F=state_d.get("F", state_d.get("cur_F", 0.5)),
            cur_Cr=state_d.get("CR", state_d.get("cur_Cr", 0.5)),
            best=round(float(state_d.get("best", state_d.get("best_after", 0)) or 0), 4),
            imp=round(float(state_d.get("improvement_rate", 0) or 0), 5),
            stag=int(float(state_d.get("stagnation_steps", 0) or 0)),
            succ=round(float(state_d.get("success_fraction", 0) or 0), 3),
            budget=round(float(state_d.get("budget_fraction", 0) or 0), 3),
            div=round(float(state_d.get("population_diversity", 0) or 0), 3),
        )
        cache_key = hashlib.sha256(
            json.dumps([PROMPT_VERSION, state_d], sort_keys=True, default=str).encode()
        ).hexdigest()
        raw = None
        meta: Dict[str, Any] = {}
        err = None
        try:
            raw, meta = self.backend.complete(prompt, cache_key=cache_key)
            action = _parse_action(raw)
            self.events.append(
                {
                    "state": state_d,
                    "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                    "raw_response": raw,
                    "action": action,
                    "meta": meta,
                    "valid": True,
                    "error": None,
                }
            )
            return action
        except BudgetExceeded:
            raise
        except AgentAPIError as exc:
            err = str(exc)
            self.events.append(
                {
                    "state": state_d,
                    "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                    "raw_response": raw,
                    "action": self._fallback,
                    "meta": meta,
                    "valid": False,
                    "error": err,
                    "api_failure": True,
                }
            )
            # Do NOT silently switch to mock: re-raise so caller can mark blocked.
            raise
        except Exception as exc:  # invalid parse / schema
            err = str(exc)
            self.backend.stats.invalid_responses += 1
            self.events.append(
                {
                    "state": state_d,
                    "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                    "raw_response": raw,
                    "action": self._fallback,
                    "meta": meta,
                    "valid": False,
                    "error": err,
                }
            )
            # Invalid agent output → execute documented fallback noop and record.
            return self._fallback


MappingLike = Any


def _parse_action(raw: str) -> Dict[str, Any]:
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
