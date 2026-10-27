"""P1A-1C preflight: max 3 real API requests on 3 distinct public states."""
import sys, os, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from experiments.metabox.p1a1_agent_controller import LLMBackend, P1A1AgentController, render_prompt

STATES = [
    ("A_low_succ", {"generation": 2, "F": 0.4, "CR": 0.5, "stagnation_steps": 1,
                    "success_fraction": 0.02, "budget_fraction": 0.15, "improvement_rate": 0.2}),
    ("B_stag", {"generation": 8, "F": 0.5, "CR": 0.5, "stagnation_steps": 8,
                "success_fraction": 0.2, "budget_fraction": 0.25, "improvement_rate": 0.0}),
    ("C_late_improve", {"generation": 12, "F": 0.6, "CR": 0.4, "stagnation_steps": 0,
                        "success_fraction": 0.35, "budget_fraction": 0.85, "improvement_rate": 0.15}),
]

b = LLMBackend(api_key=os.environ["DEEPSEEK_API_KEY"])
c = P1A1AgentController(b)
results = []
for name, st in STATES:
    prompt = render_prompt(st)
    print("====", name)
    print(prompt)
    a = c.select_action(st)
    ev = c.events[-1]
    print("ACTION", a, "valid", ev["valid"], "dev", ev.get("deviates_from_hint"),
          "finish", ev["meta"].get("finish_reason"), "reason_len", ev["meta"].get("reasoning_content_length"))
    print("raw", repr(ev.get("raw_response"))[:160])
    results.append((name, a, ev["valid"], ev.get("deviates_from_hint")))

sigs = {(a["action"], tuple(sorted(a.get("params", {}).items()))) for _, a, v, _ in results if v}
print("UNIQUE_VALID_SIGS", sigs)
print("STATS", b.stats.to_dict())
print("VALID", sum(1 for *_, v, __ in [(n,a,v,d) for n,a,v,d in results] if v), "/3")
