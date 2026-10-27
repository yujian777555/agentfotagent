import sys, os
sys.path.insert(0, ".")
from experiments.metabox.p1a1_agent_controller import LLMBackend, P1A1AgentController, render_prompt

state = {
    "generation": 1, "F": 0.5, "CR": 0.5,
    "stagnation_steps": 2, "success_fraction": 0.3,
    "budget_fraction": 0.1, "improvement_rate": 0.1,
}
print("PROMPT:", render_prompt(state))
b = LLMBackend(api_key=os.environ["DEEPSEEK_API_KEY"])
c = P1A1AgentController(b)
a = c.select_action(state)
print("ACTION", a, "valid", c.events[-1]["valid"], "hint", c.events[-1]["hint_action"], "dev", c.events[-1]["deviates_from_hint"])
print("raw", repr(c.events[-1]["raw_response"])[:120])
print("stats", b.stats)
