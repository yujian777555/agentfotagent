"""Phase-1A-7 Phase C: 3 independent critique reviews.

Each review independently evaluates ALL candidates from Phase B.
Uses deepseek-flash with a different critique angle per request.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import urllib.request

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "results" / "phase1a7" / "critiques"
OUT.mkdir(parents=True, exist_ok=True)

API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
API_URL = "https://api.deepseek.com/chat/completions"

# Load repaired candidates
PROP_DIR = ROOT / "results" / "phase1a7" / "proposals"
all_candidates = []
for f in ["proposal_1_mutation_repaired.json", "proposal_2_memory_repaired.json", "proposal_3_selection_repaired.json"]:
    d = json.loads((PROP_DIR / f).read_text(encoding="utf-8"))
    for c in d.get("candidates", []):
        c["_source_perspective"] = d.get("perspective", "?")
        all_candidates.append(c)

CAND_JSON = json.dumps(all_candidates, indent=2, ensure_ascii=False)

CRITIQUE_ANGLES = [
    {
        "id": "critique_1_novelty",
        "angle": "NOVELTY AND NEAREST-NEIGHBOR OVERLAP",
        "focus": (
            "For each candidate, determine if the core mechanism already exists in the "
            "literature. Check: (a) Is the mathematical formula equivalent to an existing "
            "method? (b) Is it just a parameter re-write or threshold change? (c) Is it a "
            "combination of two known modules? (d) Does the nearest_neighbor field accurately "
            "identify the closest prior work? Rate each candidate as NOVEL_MECHANISM, "
            "MINOR_VARIANT, or ALREADY_KNOWN. Evidence level must be FULL, PARTIAL, or SECONDARY."
        ),
    },
    {
        "id": "critique_2_evidence",
        "angle": "TRAJECTORY EVIDENCE VALIDITY",
        "focus": (
            "For each candidate, evaluate: (a) Does the cited diagnostic evidence truly "
            "support the claimed defect? (b) Could the observed pattern have alternative "
            "explanations? (c) Is the falsification_gate measurable and achievable? "
            "(d) Is the expected/failure condition analysis sound? Rate evidence quality "
            "as STRONG, MODERATE, or WEAK."
        ),
    },
    {
        "id": "critique_3_ablation",
        "angle": "ABLATION AND CONFOUNDING CONTROLS",
        "focus": (
            "For each candidate, evaluate: (a) Can the minimal_ablation isolate the "
            "mechanism's independent contribution? (b) Could simple rules, random changes, "
            "or existing algorithms explain any benefit? (c) Are the hand-designed and "
            "random-change controls adequate? (d) Is the mechanism truly different from "
            "just changing a parameter? Rate as CONTROLLABLE, PARTIALLY_CONTROLLABLE, "
            "or UNCONTROLLABLE."
        ),
    },
]

REVIEW_FORMAT = """
=== REQUIRED OUTPUT FORMAT (JSON) ===
{
  "reviews": [
    {
      "candidate_name": "<name>",
      "verdict": "<PASS|FAIL|NEEDS_MORE_EVIDENCE>",
      "novelty_rating": "<NOVEL_MECHANISM|MINOR_VARIANT|ALREADY_KNOWN>",
      "evidence_quality": "<STRONG|MODERATE|WEAK>",
      "ablation_controllability": "<CONTROLLABLE|PARTIALLY_CONTROLLABLE|UNCONTROLLABLE>",
      "literature_evidence_level": "<FULL|PARTIAL|SECONDARY>",
      "key_concerns": ["<concern 1>", ...],
      "specific_fixes": ["<fix 1>", ...],
      "overall_assessment": "<one paragraph>"
    }
  ],
  "summary": "<which candidates pass all gates>"
}
"""


def call_deepseek(messages: list, max_tokens: int = 3000) -> dict:
    body = json.dumps({
        "model": "deepseek-flash",
        "messages": messages,
        "temperature": 0.2,
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


def main() -> None:
    request_log = []
    for crit in CRITIQUE_ANGLES:
        system_msg = (
            "You are a rigorous, skeptical peer reviewer for evolutionary computation "
            "research. Your job is to find flaws, overclaims, and confounds. You are NOT "
            "here to praise. You must be specific and cite the candidate's own text. "
            "Respond with valid JSON only."
        )
        user_msg = (
            f"=== YOUR CRITIQUE ANGLE ===\n{crit['angle']}\n\n{crit['focus']}\n\n"
            f"=== CANDIDATES TO REVIEW ({len(all_candidates)}) ===\n{CAND_JSON}\n\n"
            f"{REVIEW_FORMAT}\n\n"
            f"Review ALL {len(all_candidates)} candidates. Be harsh but fair."
        )

        print(f"\n--- {crit['id']}: calling deepseek-flash ---")
        t0 = time.time()
        try:
            resp = call_deepseek([
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ])
            content = resp["choices"][0]["message"]["content"]
            usage = resp.get("usage", {})
            elapsed = round(time.time() - t0, 2)

            try:
                parsed = json.loads(content)
            except json.JSONDecodeError:
                parsed = {"raw_text": content, "parse_error": True}

            out_path = OUT / f"{crit['id']}.json"
            out_path.write_text(json.dumps(parsed, indent=2, ensure_ascii=False), encoding="utf-8")

            n_reviews = len(parsed.get("reviews", [])) if not parsed.get("parse_error") else "parse_error"
            n_pass = sum(1 for r in parsed.get("reviews", []) if r.get("verdict") == "PASS") if not parsed.get("parse_error") else "?"
            request_log.append({
                "request_id": crit["id"],
                "model": "deepseek-flash",
                "elapsed_sec": elapsed,
                "usage": usage,
                "n_reviews": n_reviews,
                "n_pass": n_pass,
                "status": "ok",
            })
            print(f"  ok: {n_reviews} reviews, {n_pass} PASS, tokens={usage.get('total_tokens','?')}, {elapsed}s")

        except Exception as exc:  # noqa: BLE001
            request_log.append({"request_id": crit["id"], "status": "fail", "error": repr(exc)})
            print(f"  FAIL: {exc}")

    log_path = OUT / "request_log.json"
    log_path.write_text(json.dumps(request_log, indent=2), encoding="utf-8")
    total_req = sum(1 for r in request_log if r["status"] == "ok")
    print(f"\nDONE: {total_req}/3 critique requests ok")
    print(f"TOTAL LLM REQUESTS THIS SESSION: 3 (proposals) + {total_req} (critiques) = {3+total_req}")


if __name__ == "__main__":
    main()
