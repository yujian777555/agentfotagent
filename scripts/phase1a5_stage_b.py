"""Phase-1A-5 Stage B: independent critique of the converged candidate (max 3)."""
from __future__ import annotations

import hashlib
import json
import os
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MODEL = "deepseek-flash"
MAX_REQ = 3

STAGE_B_PROMPT = """You are a skeptical reviewer of evolutionary computation methods.

Frozen L-SHADE defect evidence: linear N(t)=round(N_init*(1-FE/FEmax)) shrinks
independently of progress. F1 converges by ~1500 FE but N keeps falling to 4;
F10 still improves at 5000 FE after N=4.

Candidate mechanism (from another agent): replace linear N(t) with a
progress-adaptive schedule, e.g. N_{t+1}=max(4, round(N_init*(1-t/T)^alpha_t))
where alpha_t depends on smoothed relative improvement rate.

Your job: adversarial review. Answer JSON only:
{{
  "already_covered": true/false,
  "closest_work": "...",
  "is_renaming": true/false,
  "is_just_randomness": true/false,
  "simpler_explanation": "...",
  "minimal_control": "...",
  "verdict": "PASS_TO_PILOT" or "REJECT",
  "reason": "..."
}}
"""


def call(prompt):
    key = os.environ["DEEPSEEK_API_KEY"]
    body = json.dumps({
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500,
        "temperature": 0.5,
        "thinking": {"type": "disabled"},
        "response_format": {"type": "json_object"},
    }).encode()
    req = urllib.request.Request(
        "https://api.deepseek.com/v1/chat/completions",
        data=body,
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        d = json.loads(r.read())
    return d["choices"][0]["message"].get("content") or "", d.get("usage") or {}


def main():
    out_dir = ROOT / "results" / "phase1a5"
    results = []
    for i in range(MAX_REQ):
        try:
            text, usage = call(STAGE_B_PROMPT)
            obj = json.loads(text)
        except Exception as exc:
            results.append({"error": str(exc)})
            print("ERR", exc)
            continue
        results.append({"review": obj, "usage": usage})
        print(f"review_{i+1}:", obj.get("verdict"), "-", str(obj.get("reason", ""))[:200])
        print("   covered", obj.get("already_covered"), "renaming", obj.get("is_renaming"))
    (out_dir / "stageB_reviews.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    print("WROTE results/phase1a5/stageB_reviews.json")


if __name__ == "__main__":
    main()
