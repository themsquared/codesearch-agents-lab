import os
import json, sys
exec(open("measure.py").read().split("h = init()")[0])
URL = os.environ.get("AGW_URL","http://127.0.0.1:3110/mcp"); mode = sys.argv[1]
h = init(); tl = rpc(h,"tools/list",{})["result"]
names=[t["name"] for t in tl["tools"]]
print(f"[{mode}] tools/list: {len(names)} tools {names if len(names)<4 else ''} {tok(tl)[0]} chars {tok(tl)[1]} tok")
OWNER = os.environ.get("GH_OWNER","octocat")
CODE = f"const OWNER = {json.dumps(OWNER)};\n" + r"""
const P = (x) => { if (typeof x === "string") { try { return JSON.parse(x); } catch (e) { return x; } } return x; };
const arr = (x, keys) => { x = P(x); if (Array.isArray(x)) return x; for (const k of keys) if (x && Array.isArray(x[k])) return x[k]; return []; };
const repos = arr(await search_repositories({query: "user:" + OWNER, sort: "updated", order: "desc", perPage: 10}), ["items"]);
const out = []; let withPrs = 0;
for (const r of repos.slice(0, 8)) {
  const name = r.name || (r.full_name || "").split("/").pop();
  const prs = arr(await list_pull_requests({owner: OWNER, repo: name, state: "open", perPage: 10}), ["items", "pull_requests"]);
  if (!prs.length) continue;
  withPrs++;
  for (const p of prs.slice(0, 3)) {
    const d = P(await pull_request_read({method: "get", owner: OWNER, repo: name, pullNumber: p.number}));
    const f = arr(await pull_request_read({method: "get_files", owner: OWNER, repo: name, pullNumber: p.number, perPage: 100}), ["files", "items"]);
    out.push({repo: name, pr: p.number, title: d.title, files: f.length});
  }
  if (withPrs >= 3) break;
}
out
"""
if mode in ("code","codeSearch"):
    tot=[0,0]
    if mode=="codeSearch":
        for n in ["search_repositories","list_pull_requests","pull_request_read"]:
            r=rpc(h,"tools/call",{"name":"get_tool","arguments":{"name":n}})["result"]; c,t=tok(r); tot[0]+=c; tot[1]+=t
        print(f"[{mode}] 3x get_tool lookups: {tot[0]} chars {tot[1]} tok")
    r = rpc(h,"tools/call",{"name":"run_code","arguments":{"code":CODE}})["result"]
    c,t = tok(r); print(f"[{mode}] run_code result: {c} chars {t} tok :: {json.dumps(r.get('structuredContent'))[:700]}")
    print(f"[{mode}] chain total returned: {c+tot[0]} chars {t+tot[1]} tok")
    print(f"[{mode}] script size: {len(CODE)} chars {len(enc.encode(CODE))} tok")
if mode=="search":
    tot=[0,0]
    for n in ["search_repositories","list_pull_requests","pull_request_read"]:
        r=rpc(h,"tools/call",{"name":"get_tool","arguments":{"name":n}})["result"]; c,t=tok(r); tot[0]+=c; tot[1]+=t
    print(f"[{mode}] 3x get_tool lookups: {tot[0]} chars {tot[1]} tok")
