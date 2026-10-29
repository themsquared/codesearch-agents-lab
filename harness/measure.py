import json, requests, sys, tiktoken
enc = tiktoken.get_encoding("cl100k_base")
URL = sys.argv[1] if len(sys.argv)>1 else "http://localhost:3000/mcp"
H = {"Content-Type":"application/json","Accept":"application/json, text/event-stream"}
def parse(r):
    t = r.text
    if "data:" not in t: return json.loads(t)
    out=None
    for ev in t.replace("\r\n","\n").split("\n\n"):
        data="\n".join(l[5:].lstrip() if l.startswith("data:") else "" for l in ev.split("\n") if l.startswith("data:"))
        if data.strip():
            o=json.loads(data)
            if "id" in o: return o
            out=o
    return out
def init():
    r = requests.post(URL, headers=H, json={"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"m","version":"1"}}})
    sid = r.headers.get("mcp-session-id"); h = dict(H); h["Mcp-Session-Id"]=sid
    requests.post(URL, headers=h, json={"jsonrpc":"2.0","method":"notifications/initialized"})
    return h
i=[10]
def rpc(h, method, params):
    i[0]+=1
    return parse(requests.post(URL, headers=h, json={"jsonrpc":"2.0","id":i[0],"method":method,"params":params}))
def tok(o): s=json.dumps(o,separators=(",",":")); return len(s), len(enc.encode(s))
h = init()
tl = rpc(h,"tools/list",{})
tools = tl["result"]["tools"]
c,t = tok(tl["result"])
print(f"tools/list standard: {len(tools)} tools, {c} chars, {t} cl100k tokens")
for x in tools:
    print(f"  {x['name']}: {tok(x)[1]} tok")
json.dump(tl["result"], open("tools-standard.json","w"), indent=1)
