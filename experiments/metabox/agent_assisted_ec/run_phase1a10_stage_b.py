"""Phase-1A-10 Stage B: real Agent generation experiment.

Handles preflight (≤3 requests), formal A/B generation (≤12 each),
ledger management, and budget enforcement.

Budget (approved):
- Total: 24 requests max (preflight counts toward A/B quota)
- A group: 12 max, B group: 12 max
- Output: ≤800 tokens per request
- Total tokens: ≤120,000
- Model: deepseek-flash ONLY
- No auto-retry
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from experiments.metabox.agent_assisted_ec.candidate_evaluator import (
    REQUIRED_FIELDS,
    CLOSED_MECHANISMS,
    evaluate_candidate,
)

API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
API_URL = "https://api.deepseek.com/chat/completions"
MODEL = "deepseek-flash"

# Budget
MAX_REQUESTS_TOTAL = 24
MAX_REQUESTS_A = 12
MAX_REQUESTS_B = 12
MAX_OUTPUT_TOKENS = 800
MAX_TOTAL_TOKENS = 120_000

OUT = ROOT / "results" / "phase1a10"
LEDGER_PATH = OUT / "request_ledger.json"
RAW_DIR = OUT / "raw_responses"


class BudgetLedger:
    """Tracks API requests, tokens, and enforces hard limits."""

    def __init__(self, path: Path):
        self.path = path
        self.entries: List[Dict[str, Any]] = []
        if path.exists():
            self.entries = json.loads(path.read_text(encoding="utf-8"))

    @property
    def n_total(self) -> int:
        return len(self.entries)

    @property
    def n_a(self) -> int:
        return sum(1 for e in self.entries if e.get("group") == "A")

    @property
    def n_b(self) -> int:
        return sum(1 for e in self.entries if e.get("group") == "B")

    @property
    def total_tokens(self) -> int:
        return sum(e.get("total_tokens", 0) for e in self.entries)

    def can_request(self, group: str) -> Tuple[bool, str]:
        if self.n_total >= MAX_REQUESTS_TOTAL:
            return False, f"total budget exhausted ({self.n_total}/{MAX_REQUESTS_TOTAL})"
        if group == "A" and self.n_a >= MAX_REQUESTS_A:
            return False, f"A-group budget exhausted ({self.n_a}/{MAX_REQUESTS_A})"
        if group == "B" and self.n_b >= MAX_REQUESTS_B:
            return False, f"B-group budget exhausted ({self.n_b}/{MAX_REQUESTS_B})"
        # Check if we can afford the max output
        if self.total_tokens + MAX_OUTPUT_TOKENS > MAX_TOTAL_TOKENS:
            return False, f"token budget near limit ({self.total_tokens}/{MAX_TOTAL_TOKENS})"
        return True, "ok"

    def add(self, entry: Dict[str, Any]) -> None:
        self.entries.append(entry)
        self.save()

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.entries, indent=2, ensure_ascii=False), encoding="utf-8")

    def summary(self) -> Dict[str, Any]:
        return {
            "n_total": self.n_total,
            "n_a": self.n_a,
            "n_b": self.n_b,
            "total_input_tokens": sum(e.get("prompt_tokens", 0) for e in self.entries),
            "total_output_tokens": sum(e.get("completion_tokens", 0) for e in self.entries),
            "total_tokens": self.total_tokens,
            "model": MODEL,
        }


def call_deepseek(messages: List[Dict[str, str]], max_tokens: int = MAX_OUTPUT_TOKENS) -> Dict[str, Any]:
    body = json.dumps({
        "model": MODEL,
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": max_tokens,
        "response_format": {"type": "json_object"},
        "thinking": {"type": "disabled"},
    }).encode("utf-8")
    req = urllib.request.Request(
        API_URL, data=body,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))


def build_prompt(task_card: str, include_trace: bool) -> Tuple[str, str]:
    """Build system + user prompt. Returns (system_msg, user_msg)."""
    system_msg = (
        "You are an expert in evolutionary computation algorithm design. "
        "Propose ONE precise, testable algorithmic mechanism as valid JSON. "
        "CRITICAL OUTPUT LIMIT: You must fit your entire response within 750 tokens. "
        "Be CONCISE: each field should be 1-3 sentences maximum. No preamble. "
        "Do NOT propose closed mechanisms: " + ", ".join(CLOSED_MECHANISMS) + ". "
        "JSON fields (ALL required): " + ", ".join(REQUIRED_FIELDS) + ". "
        "For observed_evidence use: {\"task_id\":\"...\",\"trace_path\":\"...\",\"function\":\"F..\",\"seed\":N,\"metric\":\"...\",\"observed_value\":N}. "
        "For mathematical_rule use plain text with = + - * / symbols."
    )
    user_msg = f"=== TASK ===\n{task_card}\n"
    if include_trace:
        user_msg += "\n(Real diagnostic trace summary is included above.)\n"
    else:
        user_msg += "\n(NOTE: No diagnostic traces provided. Use problem description and source code only.)\n"
    user_msg += "\nOutput ONE JSON object with all 11 fields. Keep each field to 1-3 sentences."
    return system_msg, user_msg


def execute_request(
    ledger: BudgetLedger,
    request_id: str,
    group: str,
    task_id: str,
    candidate_idx: int,
    system_msg: str,
    user_msg: str,
) -> Optional[Dict[str, Any]]:
    """Execute a single API request with budget enforcement. Returns response or None."""
    can, reason = ledger.can_request(group)
    if not can:
        print(f"  [BUDGET] {request_id}: {reason}")
        return None

    prompt_hash = hashlib.sha256(user_msg.encode("utf-8")).hexdigest()
    t0 = time.time()
    try:
        resp = call_deepseek([
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ])
    except Exception as exc:
        entry = {
            "request_id": request_id, "group": group, "task_id": task_id,
            "candidate_idx": candidate_idx, "status": "error", "error": repr(exc),
            "timestamp": time.time(), "prompt_hash": prompt_hash,
            "prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0,
        }
        ledger.add(entry)
        print(f"  [ERROR] {request_id}: {exc}")
        return None

    content = resp.get("choices", [{}])[0].get("message", {}).get("content", "")
    usage = resp.get("usage", {})
    model_resp = resp.get("model", "unknown")
    elapsed = round(time.time() - t0, 2)

    # Verify model
    if "flash" not in model_resp.lower():
        print(f"  [MODEL_MISMATCH] {request_id}: got '{model_resp}'")
        model_ok = False
    else:
        model_ok = True

    # Parse
    parse_status = "ok"
    parse_errors = []
    try:
        parsed = json.loads(content)
        missing = [f for f in REQUIRED_FIELDS if f not in parsed]
        if missing:
            parse_status = "missing_fields"
            parse_errors = [f"missing: {m}" for m in missing]
    except json.JSONDecodeError as e:
        parsed = None
        parse_status = "json_error"
        parse_errors = [str(e)]

    # Save raw response
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    raw_path = RAW_DIR / f"{request_id}.json"
    raw_path.write_text(json.dumps(resp, indent=2, ensure_ascii=False), encoding="utf-8")

    entry = {
        "request_id": request_id,
        "group": group,
        "task_id": task_id,
        "candidate_idx": candidate_idx,
        "model_requested": MODEL,
        "model_returned": model_resp,
        "model_ok": model_ok,
        "prompt_hash": prompt_hash,
        "prompt_tokens": usage.get("prompt_tokens", 0),
        "completion_tokens": usage.get("completion_tokens", 0),
        "total_tokens": usage.get("total_tokens", 0),
        "parse_status": parse_status,
        "parse_errors": parse_errors,
        "timestamp": time.time(),
        "elapsed_sec": elapsed,
        "raw_response_path": str(raw_path.relative_to(ROOT)).replace("\\", "/"),
    }
    ledger.add(entry)

    print(f"  [OK] {request_id}: model={model_resp}, tokens={usage.get('total_tokens','?')}, parse={parse_status}, {elapsed}s")
    return {"parsed": parsed, "entry": entry, "content": content}


# ---------------------------------------------------------------------------
# Task card definitions (compact prompts for A/B)
# ---------------------------------------------------------------------------

TASK_CARDS = {
    "TASK-01": {
        "name": "zero-improvement-success",
        "description": (
            "In standard L-SHADE (lshade_canonical.py), the selection rule 'trial <= parent' "
            "accepts equal-fitness offspring. On F7 (seeds 22/33) late success rate is 0.82-0.88 "
            "but stall_gen reaches 45-53. On F21 all seeds show success_rate=1.000 with best "
            "unchanged at 786.565. These zero-improvement successes pollute M_F/M_CR memory."
        ),
        "target": "Reduce the influence of zero-improvement samples on success memory.",
        "closed_note": "Simple 'gate Δf>0' is already covered. Need substantively different mechanism.",
    },
    "TASK-02": {
        "name": "cr-memory-drift",
        "description": (
            "In standard L-SHADE, CR memory drifts to extremes: F1 CR_mean 0.52->0.85, "
            "F6 0.51->0.95, F10 0.50->0.98, F20 0.52->0.02. Positive feedback loop in "
            "weighted arithmetic mean M_CR update."
        ),
        "target": "Break the CR memory positive feedback loop.",
        "closed_note": "Simple exponential smoothing is already covered. Need different mechanism.",
    },
    "TASK-03": {
        "name": "f-collapse",
        "description": (
            "In standard L-SHADE, F memory collapses: F4 F_mean 0.58->0.06-0.13, "
            "F11 s=11 0.53->0.08, F15 0.59->0.15-0.32. Near-zero F makes differential "
            "vectors vanish."
        ),
        "target": "Maintain F in effective range, prevent differential vector vanishing.",
        "closed_note": "Simple F floor is already covered. Need different mechanism.",
    },
    "TASK-04": {
        "name": "repair-success-gap",
        "description": (
            "Boundary-repaired trials have systematically lower success rates than "
            "non-repaired: F1 0.30 vs 0.48, F7 0.12 vs 0.36, F10 0.12 vs 0.33. "
            "Repair displacement cosine is -0.4 to -0.65 (opposes search direction). "
            "The boundary repair in lshade_canonical.py is np.clip(mutant, lb, ub)."
        ),
        "target": "Reduce quality damage from boundary repair, or exploit repair events.",
        "closed_note": "Archive x boundary interaction is closed. Repair success gap is a separate observation.",
    },
    "TASK-05": {
        "name": "seed-bifurcation",
        "description": (
            "On F11, seed 11 shows diversity=0.175 (not collapsed), success_rate=0.041, "
            "stall=6; seeds 22/33 show diversity=0.000, converge to <1000. Same function, "
            "drastically different search states per seed."
        ),
        "target": "Reduce seed sensitivity of search behavior.",
        "closed_note": "Must be a specific mechanism, not just 'reduce variance'.",
    },
    "TASK-06": {
        "name": "success-regret-gap",
        "description": (
            "On F10, late success rate is 0.21-0.62 (higher than early 0.22-0.26) but "
            "best_raw remains 2.4e4-1.7e5. High conditioning landscape: success does not "
            "mean meaningful improvement."
        ),
        "target": "Distinguish meaningful improvements from trivial ones.",
        "closed_note": "Quality residual credit is closed. Must use substantively different mechanism.",
    },
}

# Trace data to include in A-group prompts (compact summaries from real diagnostics).
TRACE_SUMMARIES = {
    "TASK-01": "F7 s=22: late success_rate=0.824, stall_gen=53, diversity=0.0000. F7 s=33: success_rate=0.883, stall=45, diversity=0.0002. F21 all seeds: success_rate=1.000, stall_gen=166, best=786.565 unchanged.",
    "TASK-02": "F1: CR_mean early 0.52-0.54 -> late 0.72-0.85. F6: 0.51-0.55 -> 0.85-0.95. F10: 0.50-0.53 -> 0.90-0.98. F20: 0.52-0.54 -> 0.02-0.05. 9/12 functions show drift.",
    "TASK-03": "F4: F_mean early 0.58-0.64 -> late 0.06-0.13. F11 s=11: 0.53 -> 0.08. F15: 0.59 -> 0.15-0.32. Diversity at F11 s=11=0.175 (NOT collapsed), but F=0.08.",
    "TASK-04": "F1: repair succ 0.30 vs no-repair 0.48. F7: 0.12 vs 0.36. F10: 0.12 vs 0.33. F20: 0.11 vs 0.13. OOB rate 23.7% overall, Q1 concentration 32-71%.",
    "TASK-05": "F11 s=11: diversity=0.175, success_rate=0.041, stall=6, F_mean_late=0.08. F11 s=22: diversity=0.000, converge to 981. F11 s=33: diversity=0.000, converge to 915.",
    "TASK-06": "F10 s=11: late success_rate=0.617, best_raw=174144. s=22: 0.211, 23570. s=33: 0.318, 25316. s=44: 0.371, 7505. s=55: 0.397, 7833. High success with large cost.",
}

# Algorithm source excerpt (common to A/B).
SOURCE_EXCERPT = """
Key code from lshade_canonical.py (run_lshade_canonical):
- Population: pop[N, dim], fit[N], N linearly reduces from 100 to 4
- Mutation: mutant = pop[i] + F*(pop[p]-pop[i]) + F*(pop[r1]-vec_r2)
- F ~ Cauchy(M_F[k], 0.1), CR ~ Normal(M_CR[k], 0.1)
- Memory: M_F Lehmer mean, M_CR weighted arithmetic mean, weights=|delta_f|
- Selection: accept if trial_fit <= parent_fit
- Boundary: np.clip(mutant, lb, ub)
- Archive: replaced parents stored, used as r2 source
"""


def make_task_card_text(task_id: str, include_trace: bool) -> str:
    tc = TASK_CARDS[task_id]
    text = f"Task: {task_id} ({tc['name']})\n"
    text += f"Problem: {tc['description']}\n"
    text += f"Design target: {tc['target']}\n"
    text += f"Closed mechanisms note: {tc['closed_note']}\n"
    text += f"\nAlgorithm source excerpt:\n{SOURCE_EXCERPT}\n"
    if include_trace:
        text += f"\nDiagnostic trace summary:\n{TRACE_SUMMARIES[task_id]}\n"
    return text


def main() -> None:
    """Run preflight + formal generation based on args."""
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=["preflight", "formal"], required=True)
    parser.add_argument("--output", type=str, default=str(OUT / "candidates_raw.json"))
    args = parser.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    ledger = BudgetLedger(LEDGER_PATH)
    print(f"Budget state: total={ledger.n_total}, A={ledger.n_a}, B={ledger.n_b}, tokens={ledger.total_tokens}")

    all_candidates = []

    if args.phase == "preflight":
        print("\n=== STAGE B-PREFLIGHT (max 3 requests) ===")
        # Preflight 1: Group A, TASK-01 (with trace)
        sys_msg, user_msg = build_prompt(make_task_card_text("TASK-01", True), include_trace=True)
        r = execute_request(ledger, "PREFLIGHT-A1", "A", "TASK-01", 0, sys_msg, user_msg)
        if r:
            all_candidates.append({"group": "A", "task_id": "TASK-01", "idx": 0, "raw": r["content"]})

        # Preflight 2: Group B, TASK-02 (without trace)
        sys_msg, user_msg = build_prompt(make_task_card_text("TASK-02", False), include_trace=False)
        r = execute_request(ledger, "PREFLIGHT-B1", "B", "TASK-02", 0, sys_msg, user_msg)
        if r:
            all_candidates.append({"group": "B", "task_id": "TASK-02", "idx": 0, "raw": r["content"]})

        # Preflight 3: Group A, TASK-03 (with trace) — different task
        sys_msg, user_msg = build_prompt(make_task_card_text("TASK-03", True), include_trace=True)
        r = execute_request(ledger, "PREFLIGHT-A2", "A", "TASK-03", 0, sys_msg, user_msg)
        if r:
            all_candidates.append({"group": "A", "task_id": "TASK-03", "idx": 0, "raw": r["content"]})

    elif args.phase == "formal":
        print("\n=== STAGE B-FORMAL ===")
        import random
        rng = random.Random(20261028)  # Fixed seed for request ordering

        # Build all remaining request specs
        # Preflight used: A/TASK-01/0, A/TASK-03/0, B/TASK-02/0
        specs = []
        for task_id in TASK_CARDS:
            for idx in range(2):
                for group in ["A", "B"]:
                    # Skip already-done preflight requests
                    if group == "A" and task_id == "TASK-01" and idx == 0:
                        continue
                    if group == "A" and task_id == "TASK-03" and idx == 0:
                        continue
                    if group == "B" and task_id == "TASK-02" and idx == 0:
                        continue
                    specs.append((group, task_id, idx))

        rng.shuffle(specs)
        print(f"Planned requests: {len(specs)}")

        for i, (group, task_id, idx) in enumerate(specs):
            rid = f"FORMAL-{group}-{task_id}-{idx}"
            include_trace = (group == "A")
            sys_msg, user_msg = build_prompt(make_task_card_text(task_id, include_trace), include_trace)
            r = execute_request(ledger, rid, group, task_id, idx, sys_msg, user_msg)
            if r:
                all_candidates.append({"group": group, "task_id": task_id, "idx": idx, "raw": r["content"]})

    # Save all candidates
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    existing = []
    if out_path.exists():
        existing = json.loads(out_path.read_text(encoding="utf-8"))
    existing.extend(all_candidates)
    out_path.write_text(json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\n=== LEDGER SUMMARY ===")
    print(json.dumps(ledger.summary(), indent=2))
    print(f"Candidates saved: {len(all_candidates)} (total in file: {len(existing)})")
    print(f"Output: {out_path}")


if __name__ == "__main__":
    main()
