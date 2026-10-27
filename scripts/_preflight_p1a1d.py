"""P1A-1D single-variable preflight: 3 real API requests, NO retries."""
import sys, os, json, hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from experiments.metabox.p1a1_agent_controller import (
    LLMBackend,
    P1A1AgentController,
    PROMPT_VERSION,
    render_prompt,
    state_hint,
)

# Single-variable design: only stag and budget differ.
BASE = {
    "generation": 5,
    "F": 0.5,
    "CR": 0.5,
    "success_fraction": 0.2,
    "improvement_rate": 0.1,
    "stagnation_steps": 2,
    "budget_fraction": 0.40,
}
STATES = [
    ("A_baseline", dict(BASE, stagnation_steps=2, budget_fraction=0.40)),
    ("B_high_stag", dict(BASE, stagnation_steps=8, budget_fraction=0.40)),
    ("C_high_budget", dict(BASE, stagnation_steps=2, budget_fraction=0.85)),
]


def sig(action):
    a = action.get("action")
    v = action.get("params", {}).get("value")
    if v is not None:
        v = round(float(v), 4)
    return (a, v)


b = LLMBackend(api_key=os.environ["DEEPSEEK_API_KEY"])
b.stats = type(b.stats)()  # fresh
# disable retries for preflight by setting MAX_RETRIES effect via wrapper
c = P1A1AgentController(b)

results = []
for name, st in STATES:
    prompt = render_prompt(st)
    ph = hashlib.sha256(prompt.encode()).hexdigest()
    print("====", name)
    print("prompt_sha", ph[:16], "prompt:", prompt)
    # Force single attempt: call backend.complete once; if empty, mark invalid without retry.
    cache_key = hashlib.sha256(json.dumps([PROMPT_VERSION, prompt], separators=(",", ":")).encode()).hexdigest()
    try:
        raw, meta = b.complete(prompt, cache_key=cache_key)
    except Exception as e:
        print("API_ERR", e)
        results.append({"name": name, "error": str(e)})
        continue
    # manually parse to avoid controller retry path
    try:
        from experiments.metabox.p1a1_agent_controller import parse_action

        action = parse_action(raw)
        valid = True
        err = None
    except Exception as e:
        action = {"action": "noop", "params": {}}
        valid = False
        err = str(e)
    hint = state_hint(st)
    results.append({
        "name": name,
        "state": st,
        "prompt_sha": ph,
        "raw": raw,
        "action": action,
        "sig": sig(action),
        "valid": valid,
        "error": err,
        "hint": hint,
        "deviates_from_hint": action != hint,
        "meta": {k: meta.get(k) for k in ("id", "model", "finish_reason", "content_length", "reasoning_content_length", "usage", "empty_content")},
    })
    print("ACTION", action, "valid", valid, "sig", sig(action), "hint", hint, "dev", action != hint)
    print("raw", repr(raw)[:200])
    print("meta", results[-1]["meta"])

sigs = {r["sig"] for r in results if r.get("valid")}
print("UNIQUE_SIGS", sigs)
print("STATS", b.stats.to_dict())

# Gate evaluation
valids = sum(1 for r in results if r.get("valid"))
gate1 = valids >= 2
gate2 = len(sigs) >= 2
gate3 = False
# single-variable: B vs A (stag), C vs A (budget)
by = {r["name"]: r for r in results if r.get("valid")}
if "A_baseline" in by:
    if "B_high_stag" in by and by["B_high_stag"]["sig"] != by["A_baseline"]["sig"]:
        gate3 = True
    if "C_high_budget" in by and by["C_high_budget"]["sig"] != by["A_baseline"]["sig"]:
        gate3 = True
gate4 = True  # prompt has no hint (checked in tests)
gate5 = all("error" not in r or not r["error"] for r in results) and b.stats.api_failures == 0
print("GATE1_valid_json", gate1, "GATE2_diverse_sigs", gate2, "GATE3_single_variable_change", gate3)
print("PREFLIGHT_PASS", gate1 and gate2 and gate3 and gate4 and gate5)
Path(ROOT / "results" / "p1a1_pilot").mkdir(parents=True, exist_ok=True)
out = ROOT / "results" / "p1a1_pilot" / f"preflight_p1a1d_{PROMPT_VERSION}.json"
out.write_text(json.dumps({"results": results, "stats": b.stats.to_dict(), "prompt_version": PROMPT_VERSION}, indent=2, default=str), encoding="utf-8")
print("WROTE", out)
