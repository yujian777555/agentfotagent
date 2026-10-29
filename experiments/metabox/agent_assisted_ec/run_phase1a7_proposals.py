"""Phase-1A-7 Phase B: 3 independent deepseek-flash mechanism proposals.

Each request studies ONE mechanism perspective with real diagnostic evidence.
Saves raw responses to results/phase1a7/proposals/.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import urllib.request
import urllib.error

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "results" / "phase1a7" / "proposals"
OUT.mkdir(parents=True, exist_ok=True)

API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
API_URL = "https://api.deepseek.com/chat/completions"

DIAG_EVIDENCE = """
=== REAL DIAGNOSTIC EVIDENCE (Phase-1A-7, 36 runs, BBOB 10D, 5000 FE) ===

Pattern 1 - SUCCESS-IMPROVEMENT DECOUPLING (F7, F21):
  F7 s=22: late success_rate=0.824, stall_gen=53, diversity=0.0000
  F7 s=33: late success_rate=0.883, stall_gen=45, diversity=0.0002
  F21 all seeds: success_rate=1.000 always, stall_gen=166, best unchanged at 786.565
  → Many trials satisfy trial<=parent but with negligible Δf. Equal-fitness
    acceptance pollutes success memory with zero-information samples.

Pattern 2 - CR MEMORY DRIFT TO EXTREMES (9/12 functions):
  F1: CR_mean early 0.52-0.54 → late 0.72-0.85
  F6: 0.51-0.55 → 0.85-0.95
  F10: 0.50-0.53 → 0.90-0.98
  F20: 0.52-0.54 → 0.02-0.05 (opposite direction)
  → Positive feedback: once CR drifts, subsequent successes amplify it.

Pattern 3 - DIVERSITY COLLAPSE (F1, F6, F10, F12):
  Early normalized diversity 0.15-0.27 → late 0.000-0.003.
  Combined with N: 100→4 linear reduction.

Pattern 4 - F MEMORY COLLAPSE TO ZERO (F4, F11s11, F15):
  F4: F_mean early 0.58-0.64 → late 0.06-0.13
  F11 s=11: 0.53 → 0.08
  → Near-zero F makes differential vectors vanish; search degrades to
    tiny perturbation around parent.

Pattern 5 - SEED-DEPENDENT BEHAVIORAL BIFURCATION (F11):
  s=11: diversity=0.175 (NOT collapsed), success_rate=0.041, stall=6
  s=22/33: diversity=0.000, converge to <1000
  → Same function, completely different search states per seed.

Pattern 6 - HIGH SUCCESS BUT LARGE REGRET (F10):
  Late success_rate 0.21-0.62 but best_raw 2.4e4-1.7e5.
  High conditioning: success ≠ meaningful improvement.
"""

CLOSED_ROUTES = """
=== CLOSED ROUTES (must NOT propose) ===
- CC-SOC, quality residual, IPW/DR credit estimation (Phase-1A-3N/3N2 closed)
- N+I restart and state-triggered interventions (Phase-1A-4R3 closed)
- Adaptive population reduction as a "new algorithm" (Phase-1A-5 closed)
- LLM-generated mutation operators as innovation (Phase-1A-0/1 closed)
- Operator switching without controlling random-change effects
- Changing thresholds, adding smoothing coefficients, renaming existing
  methods, or concatenating two existing modules
"""

FORMAT_REQ = """
=== REQUIRED OUTPUT FORMAT (JSON) ===
{
  "perspective": "<mutation|memory|selection>",
  "candidates": [
    {
      "name": "<short name>",
      "observable_defect": "<what defect, citing specific function/seed/gen evidence>",
      "evidence": "<exact diagnostic numbers>",
      "mathematical_definition": "<precise formula>",
      "modification_location": "<where in lshade_canonical.py>",
      "pseudocode": "<key pseudocode>",
      "nearest_neighbor": "<closest existing method and paper>",
      "evidence_level": "<FULL|PARTIAL|SECONDARY>",
      "mechanism_difference": "<how this differs mechanistically from nearest neighbor>",
      "expected_conditions": "<when it should help>",
      "failure_conditions": "<when it should fail>",
      "minimal_ablation": "<smallest ablation>",
      "hand_designed_control": "<manual alternative of same complexity>",
      "random_change_control": "<random perturbation control>",
      "falsification_gate": "<measurable threshold that would falsify>"
    }
  ],
  "no_candidate_reason": null
}
If evidence is insufficient, return {"candidates": [], "no_candidate_reason": "..."}.
"""

PERSPECTIVES = [
    {
        "id": "proposal_1_mutation",
        "focus": "Mutation vector construction and differential directions",
        "detail": (
            "Study the current-to-pbest/1/bin mutation in lshade_canonical.py. "
            "The differential vectors are x_pbest - x_i and x_r1 - x_r2. "
            "Consider: how are pbest, r1, r2 selected? How does F scale the "
            "differential? What happens when diversity collapses (Pattern 3) or "
            "F collapses to zero (Pattern 4)? Can the construction of the "
            "difference vectors be improved WITHOUT just changing F's distribution? "
            "Look at Patterns 3, 4, 5 as evidence for mutation-vector limitations."
        ),
    },
    {
        "id": "proposal_2_memory",
        "focus": "Success parameter memory update and utilization",
        "detail": (
            "Study M_F and M_CR success-history memory in lshade_canonical.py. "
            "M_F uses Lehmer mean, M_CR uses weighted arithmetic mean, weights "
            "= |Δf|. Consider: what happens when Δf≈0 (Pattern 1)? What drives "
            "CR drift (Pattern 2)? What drives F collapse (Pattern 4)? Can the "
            "memory update rule or sampling rule be improved WITHOUT just changing "
            "the Cauchy/Normal distribution? Look at Patterns 1, 2, 4 as evidence "
            "for memory-update limitations."
        ),
    },
    {
        "id": "proposal_3_selection",
        "focus": "Parent-offspring survival selection and archive utilization",
        "detail": (
            "Study the selection rule (trial <= parent) and external archive in "
            "lshade_canonical.py. Consider: what does '<=' mean in flat regions "
            "(Pattern 1)? How does the archive interact with diversity collapse "
            "(Pattern 3)? How does selection pressure change as N shrinks? Can "
            "selection or archive usage be improved WITHOUT N+I or restarts? "
            "Look at Patterns 1, 3, 6 as evidence for selection/archive limitations."
        ),
    },
]


def call_deepseek(messages: list, max_tokens: int = 2000) -> dict:
    body = json.dumps({
        "model": "deepseek-flash",
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": max_tokens,
        "response_format": {"type": "json_object"},
        "thinking": {"type": "disabled"},
    }).encode("utf-8")

    req = urllib.request.Request(
        API_URL,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> None:
    request_log = []
    for persp in PERSPECTIVES:
        system_msg = (
            "You are an expert in evolutionary computation algorithms, specifically "
            "Differential Evolution variants (SHADE, L-SHADE, jSO, etc.). You propose "
            "precise, testable algorithmic mechanisms based on real trajectory evidence. "
            "You must not propose already-closed mechanisms. You must cite specific "
            "diagnostic numbers. Respond with valid JSON only."
        )
        user_msg = (
            f"{DIAG_EVIDENCE}\n{CLOSED_ROUTES}\n{FORMAT_REQ}\n"
            f"=== YOUR PERSPECTIVE ===\n{persp['focus']}\n\n"
            f"{persp['detail']}\n\n"
            f"Propose 1-3 candidate mechanisms from THIS perspective only. "
            f"Each must cite real diagnostic evidence (function, seed, number)."
        )

        print(f"\n--- {persp['id']}: calling deepseek-flash ---")
        t0 = time.time()
        try:
            resp = call_deepseek([
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ])
            content = resp["choices"][0]["message"]["content"]
            usage = resp.get("usage", {})
            elapsed = round(time.time() - t0, 2)

            # parse JSON
            try:
                parsed = json.loads(content)
            except json.JSONDecodeError:
                parsed = {"raw_text": content, "parse_error": True}

            out_path = OUT / f"{persp['id']}.json"
            out_path.write_text(json.dumps(parsed, indent=2, ensure_ascii=False), encoding="utf-8")

            request_log.append({
                "request_id": persp["id"],
                "model": "deepseek-flash",
                "elapsed_sec": elapsed,
                "usage": usage,
                "n_candidates": len(parsed.get("candidates", [])),
                "no_candidate_reason": parsed.get("no_candidate_reason"),
                "status": "ok",
            })
            print(f"  ok: {len(parsed.get('candidates', []))} candidates, "
                  f"tokens={usage.get('total_tokens', '?')}, {elapsed}s")

        except Exception as exc:  # noqa: BLE001
            request_log.append({
                "request_id": persp["id"],
                "status": "fail",
                "error": repr(exc),
            })
            print(f"  FAIL: {exc}")

    log_path = OUT / "request_log.json"
    log_path.write_text(json.dumps(request_log, indent=2), encoding="utf-8")
    print(f"\nDONE: {sum(1 for r in request_log if r['status']=='ok')}/3 requests ok")
    print(f"Log: {log_path}")


if __name__ == "__main__":
    main()
