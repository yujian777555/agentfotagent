"""Verify deepseek-flash availability (one request). Records metadata, no secrets."""
import os, json, urllib.request

key = os.environ["DEEPSEEK_API_KEY"]
body = json.dumps({
    "model": "deepseek-flash",
    "messages": [{"role": "user", "content": "Reply with JSON {\"ok\":true}"}],
    "max_tokens": 32,
    "temperature": 0.0,
    "thinking": {"type": "disabled"},
    "response_format": {"type": "json_object"},
}).encode()
req = urllib.request.Request(
    "https://api.deepseek.com/v1/chat/completions",
    data=body,
    headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
    method="POST",
)
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.loads(r.read())
    msg = d["choices"][0]["message"]
    print("AVAILABLE model=", d.get("model"), "content=", repr(msg.get("content")),
          "finish=", d["choices"][0].get("finish_reason"), "usage=", d.get("usage"))
except Exception as e:
    print("UNAVAILABLE", type(e).__name__, e)
    if hasattr(e, "read"):
        print("body", e.read()[:400])
