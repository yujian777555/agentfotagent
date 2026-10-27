from pathlib import Path

p = Path("experiments/metabox/p1a1_agent_controller.py")
t = p.read_text(encoding="utf-8")
old_start = t.find("PROMPT_VERSION =")
old_end = t.find("class AgentAPIError")
new = '''PROMPT_VERSION = "p1a1d-agent-v1"
MAX_OUTPUT_TOKENS = 256
MAX_REQUESTS = 140
MAX_RETRIES = 1

# Pure text protocol: NO concrete parameter-value examples (P1A-1D).
PROMPT_TEMPLATE = (
    "You control Differential Evolution parameters. "
    "Output one JSON object and nothing else. "
    "The object has exactly two fields: action and params. "
    "action must be one of: set_F, set_CR, noop. "
    "If action is set_F, params must contain value in [0.1, 1.0]. "
    "If action is set_CR, params must contain value in [0.0, 1.0]. "
    "If action is noop, params must be an empty object. "
    "Choose the action only from the current public state. "
    "Do not output explanations, code, or extra fields. "
    "State: gen={gen} F={cur_F} CR={cur_Cr} stag={stag} succ={succ} budget={budget} improve={imp}."
)


'''
assert old_start >= 0 and old_end > old_start
p.write_text(t[:old_start] + new + t[old_end:], encoding="utf-8")
print("replaced ok")
