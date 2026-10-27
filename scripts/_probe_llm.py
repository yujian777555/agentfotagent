import os, json, urllib.request

key = os.environ["DEEPSEEK_API_KEY"]

def call(model, prompt, max_tokens=256):
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
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
    msg = d["choices"][0]["message"]
    print("MODEL", model, "MT", max_tokens)
    print("  content", repr(msg.get("content"))[:250])
    print("  usage", d.get("usage", {}).get("completion_tokens_details"))

call("deepseek-v4-pro", "2+2=?", 64)
call("deepseek-flash", "2+2=?", 64)
call("deepseek-v4-pro", 'You are a controller. User gives state. You reply ONLY {"action":"set_F","params":{"value":V}}. State: gen=1 F=0.5 CR=0.5 stagn=3. Pick F=0.8.', 128)
