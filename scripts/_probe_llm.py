"""Probe DeepSeek API contract: thinking disabled + json_object response_format."""
import os, json, urllib.request

key = os.environ["DEEPSEEK_API_KEY"]

def call(body_dict):
    body = json.dumps(body_dict).encode()
    req = urllib.request.Request(
        "https://api.deepseek.com/v1/chat/completions",
        data=body,
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            d = json.loads(r.read())
        msg = d["choices"][0]["message"]
        print("OK finish=", d["choices"][0].get("finish_reason"),
              "content=", repr(msg.get("content"))[:180],
              "reason_len=", len(msg.get("reasoning_content") or ""),
              "usage=", d.get("usage"))
    except Exception as e:
        print("ERR", type(e).__name__, e)
        if hasattr(e, "read"):
            print(" body", e.read()[:300])

# A: thinking disabled + json_object
call({
    "model": "deepseek-v4-pro",
    "messages": [{"role": "user", "content": "Choose DE parameters. State: gen=1 F=0.5 CR=0.5 stag=2 succ=0.3 budget=0.1. Return JSON with action and params."}],
    "max_tokens": 256,
    "temperature": 0.0,
    "thinking": {"type": "disabled"},
    "response_format": {"type": "json_object"},
})
