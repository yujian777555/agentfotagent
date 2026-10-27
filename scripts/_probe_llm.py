import os, json, urllib.request

print("dashscope key", bool(os.environ.get("DASHSCOPE_API_KEY")))
# Try dashscope compatible-mode
key = os.environ.get("DASHSCOPE_API_KEY")
for base, model in [
    ("https://dashscope.aliyuncs.com/compatible-mode/v1", "qwen-turbo"),
    ("https://dashscope.aliyuncs.com/compatible-mode/v1", "qwen-plus"),
]:
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": 'Reply ONLY JSON {"action":"set_F","params":{"value":0.7}} for state gen=1 stag=2.'}],
        "max_tokens": 64,
    }).encode()
    req = urllib.request.Request(
        base + "/chat/completions",
        data=body,
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            d = json.loads(r.read())
        print(model, repr(d["choices"][0]["message"].get("content"))[:150])
    except Exception as e:
        print(model, "ERR", e)
