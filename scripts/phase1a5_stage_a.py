"""Phase-1A-5 Stage A: ask deepseek-flash for mechanism candidates (max 3)."""
from __future__ import annotations

import hashlib
import json
import os
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

MODEL = "deepseek-flash"
PROMPT_VERSION = "p1a5-stageA-v1"
MAX_REQ = 3

STAGE_A_PROMPT = """You are an evolutionary computation researcher.

Frozen L-SHADE trajectory summary (BBOB-10D, 5000 FE, N_init=100, linear N to 4):
{traj}

Closed lines (do NOT propose these): restart/immigration interventions;
stagnation or diversity triggers; memory reset; baseline-subtraction credit;
IPW/DR operator credit; LLM-generated code.

Known weak spots from real traces: Lehmer-mean M_F update can be dominated by
rare huge improvements; linear N(t) can be too fast/slow vs actual progress.

Propose ONE minimal, executable mechanism change to L-SHADE. Return JSON only:
{{
  "candidate_id": "cand_1",
  "defect": "...",
  "evidence": "...",
  "patch_location": "...",
  "math": "...",
  "nearest_paper": "...",
  "difference": "...",
  "predicted_behavior": "...",
  "falsification": "...",
  "ablation": "..."
}}
"""


def call(prompt: str, tag: str):
    key = os.environ["DEEPSEEK_API_KEY"]
    body = json.dumps({
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 700,
        "temperature": 0.4,
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
    text = d["choices"][0]["message"].get("content") or ""
    usage = d.get("usage") or {}
    return text, usage


def main():
    traj = (ROOT / "results" / "phase1a5" / "lshade_trajectory_summary.txt").read_text(encoding="utf-8")
    prompt = STAGE_A_PROMPT.format(traj=traj)
    out_dir = ROOT / "results" / "phase1a5"
    out_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for i in range(MAX_REQ):
        try:
            text, usage = call(prompt, f"stageA_{i+1}")
        except Exception as exc:
            results.append({"error": str(exc)})
            print("ERR", exc)
            continue
        try:
            obj = json.loads(text)
        except Exception as exc:
            results.append({"raw": text[:500], "error": str(exc)})
            print("PARSE_ERR", exc)
            continue
        results.append({"response": obj, "usage": usage,
                        "prompt_sha": hashlib.sha256(prompt.encode()).hexdigest()[:16]})
        print(f"cand_{i+1}:")
        for k, v in obj.items():
            print(f"  {k}: {str(v)[:150]}")
        print("  usage", usage)
    (out_dir / "stageA_candidates.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    print("WROTE results/phase1a5/stageA_candidates.json")


if __name__ == "__main__":
    main()
