import sys, os, json
sys.path.insert(0, ".")
from experiments.metabox.p1a1_agent_controller import LLMBackend, P1A1AgentController, render_prompt

# typical first-gen state from controlled_de
state = {
    "generation": 0.0,
    "improvement_rate": 0.0,
    "stagnation_steps": 0.0,
    "population_diversity": 45.123456789,
    "success_fraction": 0.0,
    "budget_fraction": 0.06666666666,
    "best": 1234567.89123,
    "F": 0.5,
    "CR": 0.5,
}
print("PROMPT:", render_prompt(state))
b = LLMBackend(api_key=os.environ["DEEPSEEK_API_KEY"])
c = P1A1AgentController(b)
try:
    a = c.select_action(state)
    print("ACTION", a, c.events[-1].get("deviates_from_hint"))
except Exception as e:
    print("ERR", e)
    print("raw", c.events[-1].get("raw_response") if c.events else None)
print("stats", b.stats)
