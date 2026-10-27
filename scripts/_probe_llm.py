import os, json, urllib.request

key = os.environ["DEEPSEEK_API_KEY"]
prompt = (
    'You are a controller. User gives state. You reply ONLY {"action":"set_F","params":{"value":V}}. '
    "State: gen=1 F=0.5 CR=0.5 stag=0 succ=0.4. Pick F=0.5."
)
print(prompt)
body = json.dumps({
    "model": "deepseek-v4-pro",
    "messages": [{"role": "user", "content": prompt}],
    "max_tokens": 128,
    "temperature": 0.0,
}).encode()
req = urllib.request.Request(
    "https://api.deepseek.com/v1/chat/completions",
    data=body,
    headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=45) as r:
    d = json.loads(r.read())
print("content", repr(d["choices"][0]["message"].get("content")))
print("usage", d.get("usage", {}).get("completion_tokens_details"))
