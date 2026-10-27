"""P1A-1E flash preflight: 3 real API requests on single-variable states, no retries."""
import sys, os, json, hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from experiments.metabox.p1a1_agent_controller import (
    LLMBackend,
    PROMPT_VERSION,
    parse_action,
    render_prompt,
    state_hint,
)

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

b = LLMBackend(api_key=os.environ["DEEPSEEK_API_KEY"], model="deepseek-flash")
results = []
for name, st in STATES:
    prompt = render_prompt(st)
    ph = hashlib.sha256(prompt.encode()).hexdigest()
    cache_key = hashlib.sha256(json.dumps([PROMPT_VERSION, b.model, prompt], separators=(",", ":")).encode()).hexdigest()
    print("====", name, "prompt_sha", ph[:12])
    try:
        raw, meta = b.complete(prompt, cache_key=cache_key)
    except Exception as e:
        print("API_ERR", type(e).__name__, e)
        results.append({"name": name, "error": str(e), "prompt_sha": ph})
        continue
    try:
        action = parse_action(raw)
        valid, err = True, None
    except Exception as e:
        action, valid, err = {"action": "noop", "params": {}}, False, str(e)
    v = action.get("params", {}).get("value")
    sig = (action.get("action"), None if v is None else round(float(v), 4))
    hint = state_hint(st)
    results.append({
        "name": name, "state": st, "prompt_sha": ph, "raw": raw,
        "action": action, "sig": sig, "valid": valid, "error": err,
        "hint": hint, "deviates_from_hint": action != hint,
        "meta": {k: meta.get(k) for k in ("id", "model", "finish_reason", "content_length", "reasoning_content_length", "usage", "empty_content")},
    })
    print("ACTION", action, "valid", valid, "sig", sig, "hint", hint)
    print("raw", repr(raw)[:180])
    print("meta", results[-1]["meta"])

sigs = {r["sig"] for r in results if r.get("valid")}
valids = sum(1 for r in results if r.get("valid"))
by = {r["name"]: r for r in results if r.get("valid")}
gate1 = valids == 3
gate2 = len(sigs) >= 2
gate3 = False
if "A_baseline" in by:
    if "B_high_stag" in by and by["B_high_stag"]["sig"] != by["A_baseline"]["sig"]:
        gate3 = True
    if "C_high_budget" in by and by["C_high_budget"]["sig"] != by["A_baseline"]["sig"]:
        gate3 = True
gate5 = b.stats.api_failures == 0 and b.stats.empty_content == 0
print("UNIQUE_SIGS", sigs)
print("STATS", b.stats.to_dict())
print("GATE1_all3_valid", gate1, "GATE2_diverse", gate2, "GATE3_single_var", gate3, "GATE5_clean", gate5)
print("PREFLIGHT_PASS", gate1 and gate2 and gate3 and gate5)
out = ROOT / "results" / "p1a1_pilot"
out.mkdir(parents=True, exist_ok=True)
path = out / f"preflight_p1a1e_flash_{PROMPT_VERSION}.json"
path.write_text(json.dumps({"results": results, "stats": b.stats.to_dict(), "prompt_version": PROMPT_VERSION, "model": "deepseek-flash"}, indent=2, default=str), encoding="utf-8")
print("WROTE", path)
