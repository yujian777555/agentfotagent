from pathlib import Path

p = Path("experiments/metabox/p1a1_agent_controller.py")
t = p.read_text(encoding="utf-8")
t = t.replace('model: str = "deepseek-v4-pro"', 'model: str = "deepseek-flash"')
t = t.replace('PROMPT_VERSION = "p1a1d-agent-v1"', 'PROMPT_VERSION = "p1a1d-agent-v1-flash"')
t = t.replace(
    'json.dumps([PROMPT_VERSION, prompt], separators=(",", ":")).encode()',
    'json.dumps([PROMPT_VERSION, self.model, prompt], separators=(",", ":")).encode()',
)
p.write_text(t, encoding="utf-8")
print("ok")
