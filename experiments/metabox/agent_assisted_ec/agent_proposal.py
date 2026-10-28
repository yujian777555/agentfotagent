"""DeepSeek-flash Agent for mechanism diagnosis + DSL proposal (Phase-1A-2)."""
from __future__ import annotations

import hashlib
import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .mechanism_dsl import MECH_DSL_VERSION, compile_mechanism, validate_mechanism

PROMPT_VERSION = "p1a2-agent-mech-v1"
MAX_REQUESTS = 12
MAX_RETRIES = 1
MAX_OUTPUT_TOKENS = 700


class AgentAPIError(RuntimeError):
    pass


class BudgetExceeded(RuntimeError):
    pass


@dataclass
class ProposalStats:
    requests: int = 0
    retries: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cache_hits: int = 0
    invalid: int = 0
    api_failures: int = 0

    def to_dict(self):
        return dict(self.__dict__)


DIAG_PROMPT = """You are an evolutionary computation researcher.
Below is a compressed summary of REAL Differential Evolution search trajectories
on training functions (no hidden optimum, no test labels).

TRAJECTORY SUMMARY:
{traj}

Task: Diagnose search problems and propose ONE mechanism as JSON only:
{{
  "mechanism_id": "agent_mech_<n>",
  "description": "...",
  "rules": [
    {{"when": {{"stagnation_steps": {{"op": ">=", "value": 5.0}}}},
      "then": {{"action": "set_operator", "params": {{"operator": "rand/2/bin"}}}}}}
  ],
  "default": {{"action": "set_operator", "params": {{"operator": "rand/1/bin"}}}}
}}
Legal actions: set_operator (rand/1/bin|current-to-best/1/bin|rand/2/bin|best/1/bin),
set_F (0.1-1.0), set_CR (0.0-1.0), inject_diversity, noop.
Rules must use public features: stagnation_steps, success_fraction,
population_diversity, improvement_rate, budget_fraction.
Include at least one reachable conditional branch (not a constant policy).
Also answer briefly in description: diagnosis, evidence, failure mode, falsifiable prediction.
JSON only.
"""


def _http_complete(prompt: str, model: str, api_key: str, stats: ProposalStats) -> str:
    if stats.requests >= MAX_REQUESTS:
        raise BudgetExceeded(f"proposal budget exhausted ({MAX_REQUESTS})")
    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": MAX_OUTPUT_TOKENS,
        "temperature": 0.3,
        "thinking": {"type": "disabled"},
        "response_format": {"type": "json_object"},
    }
    data = json.dumps(body).encode()
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    last = None
    for att in range(1 + MAX_RETRIES):
        if stats.requests >= MAX_REQUESTS:
            raise BudgetExceeded()
        stats.requests += 1
        if att:
            stats.retries += 1
        req = urllib.request.Request("https://api.deepseek.com/v1/chat/completions",
                                     data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                payload = json.loads(r.read().decode())
            usage = payload.get("usage") or {}
            stats.prompt_tokens += int(usage.get("prompt_tokens") or 0)
            stats.completion_tokens += int(usage.get("completion_tokens") or 0)
            text = (payload["choices"][0]["message"].get("content") or "").strip()
            if text:
                return text
            stats.invalid += 1
            last = "empty"
        except Exception as e:
            stats.api_failures += 1
            last = str(e)
    raise AgentAPIError(f"proposal request failed: {last}")


def summarize_trajectories(traces: List[Dict[str, Any]]) -> str:
    """Compress real DE traces to public-state summary (no optimum values)."""
    lines = []
    for tr in traces:
        ev = tr.get("action_events") or []
        stag_max = max((e["state"].get("stagnation_steps", 0) for e in ev), default=0)
        succs = [e.get("success_fraction_this_gen") for e in ev if e.get("success_fraction_this_gen") is not None]
        imps = [e["state"].get("improvement_rate", 0) for e in ev]
        divs = [e["state"].get("population_diversity", 0) for e in ev]
        lines.append(
            f"- func={tr.get('function_id')} seed={tr.get('seed')} gens={len(ev)} "
            f"stag_max={stag_max:.0f} succ_mean={sum(succs)/max(1,len(succs)):.3f} "
            f"imp_mean={sum(imps)/max(1,len(imps)):.4f} div_start={divs[0] if divs else 0:.2f} "
            f"div_end={divs[-1] if divs else 0:.2f} fes={tr.get('fes')}"
        )
        # first 3 and last 2 generation states
        for e in ev[:3] + ev[-2:]:
            st = e["state"]
            lines.append(
                f"    gen={int(st.get('generation',0))} stag={st.get('stagnation_steps')} "
                f"succ={e.get('success_fraction_this_gen')} imp={st.get('improvement_rate'):.4f} "
                f"div={st.get('population_diversity'):.2f} budget={st.get('budget_fraction'):.2f} "
                f"op={e.get('operator')} F={e.get('F')}"
            )
    return "\n".join(lines)


def propose_mechanisms(traj_summary: str, n: int = 3, api_key: Optional[str] = None,
                       model: str = "deepseek-flash") -> Tuple[List[Dict[str, Any]], ProposalStats, List[Dict[str, Any]]]:
    """Request up to n distinct legal mechanisms. Returns (specs, stats, raw_log)."""
    api_key = api_key or os.environ.get("DEEPSEEK_API_KEY") or ""
    stats = ProposalStats()
    specs: List[Dict[str, Any]] = []
    raw_log: List[Dict[str, Any]] = []
    seen_hashes = set()
    attempts = 0
    while len(specs) < n and attempts < MAX_REQUESTS:
        attempts += 1
        prompt = DIAG_PROMPT.format(traj=traj_summary)
        try:
            raw = _http_complete(prompt, model, api_key, stats)
        except (AgentAPIError, BudgetExceeded) as exc:
            raw_log.append({"error": str(exc)})
            break
        try:
            obj = json.loads(raw)
            # enforce unique ids
            obj["mechanism_id"] = f"agent_mech_{len(specs)+1}"
            obj["schema_version"] = MECH_DSL_VERSION
            spec = validate_mechanism(obj)
            h = hashlib.sha256(json.dumps(spec, sort_keys=True).encode()).hexdigest()
            if h in seen_hashes:
                stats.invalid += 1
                raw_log.append({"raw": raw[:400], "error": "duplicate_mechanism"})
                continue
            seen_hashes.add(h)
            specs.append(spec)
            raw_log.append({"raw": raw[:800], "mechanism_id": spec["mechanism_id"], "hash": h[:12]})
        except Exception as exc:
            stats.invalid += 1
            raw_log.append({"raw": raw[:400], "error": str(exc)})
    return specs, stats, raw_log
