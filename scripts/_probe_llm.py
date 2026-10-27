import os, json, urllib.request

def try_model(model, max_tokens, extra=None):
    key = os.environ["DEEPSEEK_API_KEY"]
    body = {
        "model": model,
        "messages": [{"role": "user", "content": "Return ONLY compact JSON {\"action\":\"set_F\",\"params\":{\"value\":0.7}} without any other text."}],
        "max_tokens": max_tokens,
        "temperature": 0.0,
    }
    if extra:
        body.update(extra)
    req = urllib.request.Request(
        "https://api.deepseek.com/v1/chat/completions",
        data=json.dumps(body).encode(),
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            d = json.loads(r.read())
        ch = d["choices"][0]["message"]
        print(model, "max", max_tokens, "content=", repr(ch.get("content"))[:120],
              "usage=", d.get("usage", {}).get("completion_tokens_details"))
    except Exception as e:
        print(model, "ERR", e)

try_model("deepseek-flash", 128)
try_model("deepseek-flash", 256)
try_model("deepseek-v4-pro", 128)
try_model("deepseek-v4-pro", 128, {"reasoning_effort": "low"})
