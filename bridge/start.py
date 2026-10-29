#!/usr/bin/env python3
"""stdio MCP server for the app: ensures the loopback agentgateway is up, then bridges
stdin/stdout (newline delimited JSON-RPC) to http://127.0.0.1:3110/mcp (streamable HTTP).
stdout carries only MCP JSON-RPC; diagnostics go to stderr and logs/bridge.log.
Secrets: read from env or secrets/ files, never printed, never in argv."""
import fcntl, json, os, re, socket, subprocess, sys, threading, time, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
HOST, PORT = "127.0.0.1", 3110
URL = f"http://{HOST}:{PORT}/mcp"
ROOT = os.path.dirname(HERE)
LOGDIR, RUNDIR, SECDIR = (os.path.join(ROOT, d) for d in ("logs", "run", "secrets"))
AGW_BIN = os.environ.get("AGW_BIN") or os.path.join(ROOT, "bin", "agentgateway")
AGW_CONFIG = os.environ.get("AGW_CONFIG") or os.path.join(ROOT, "gateway", "codeSearch.yaml")

def secret(env_name, fname):
    v = os.environ.get(env_name)
    if v: return v
    with open(os.path.join(SECDIR, fname)) as f: return f.read().strip()

def blog(msg):
    line = time.strftime("%Y-%m-%d %H:%M:%S %Z ") + msg + "\n"
    try:
        with open(os.path.join(LOGDIR, "bridge.log"), "a") as f: f.write(line)
    except OSError: pass
    sys.stderr.write(line); sys.stderr.flush()

def port_open():
    try:
        with socket.create_connection((HOST, PORT), timeout=0.5): return True
    except OSError: return False

# ---------- supervisor: runs the gateway and scrubs its output into logs/gateway.log ----------
HDR = re.compile(r'(?i)((?:authorization|x-api-key|cookie|set-cookie|mcp-session-id)["\']?\s*[:=]\s*)("?)[^\s",}]+')
def supervise():
    lic, pat = secret("ENTERPRISE_AGENTGATEWAY_LICENSE_KEY", "license"), secret("GITHUB_READONLY_PAT", "github_pat")
    env = {"PATH": "/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin", "HOME": "/tmp/agw-lab-home", "ENTERPRISE_AGENTGATEWAY_LICENSE_KEY": lic, "GITHUB_READONLY_PAT": pat, "LAB_ROOT": ROOT}
    os.makedirs(env["HOME"], mode=0o700, exist_ok=True)
    p = subprocess.Popen([AGW_BIN, "-f", AGW_CONFIG],
                         env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=ROOT)
    with open(os.path.join(RUNDIR, "gateway.pid"), "w") as f: f.write(str(p.pid))
    log = open(os.path.join(LOGDIR, "gateway.log"), "a", buffering=1)
    for raw in p.stdout:
        s = raw.decode("utf-8", "replace")
        for v in (lic, pat):
            if v: s = s.replace(v, "[REDACTED]")
        log.write(HDR.sub(r"\1\2[REDACTED]", s))
    log.write(f"gateway exited with {p.wait()}\n")

def ensure_gateway():
    os.makedirs(LOGDIR, mode=0o700, exist_ok=True); os.makedirs(RUNDIR, mode=0o700, exist_ok=True)
    with open(os.path.join(RUNDIR, "start.lock"), "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        if port_open(): return
        # stale pid cleanup
        pf = os.path.join(RUNDIR, "gateway.pid")
        if os.path.exists(pf):
            try:
                pid = int(open(pf).read()); os.kill(pid, 0)
                blog(f"gateway pid {pid} alive but port closed; waiting")
            except (ValueError, ProcessLookupError, PermissionError): os.remove(pf)
        if not os.path.exists(pf):
            blog("starting agentgateway on 127.0.0.1:3110")
            subprocess.Popen([sys.executable, os.path.abspath(__file__), "--supervise"], cwd=ROOT,
                             stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                             close_fds=True, start_new_session=True)
        for _ in range(150):
            if port_open(): return
            time.sleep(0.2)
        blog("gateway did not come up within 30s; see logs/gateway.log")

# ---------- bridge ----------
out_lock = threading.Lock()
state = {"sid": None, "init": None, "inited": None}
def emit(obj):
    with out_lock:
        sys.stdout.write(json.dumps(obj, separators=(",", ":")) + "\n"); sys.stdout.flush()

def post(msg):
    h = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
    if state["sid"]: h["Mcp-Session-Id"] = state["sid"]
    req = urllib.request.Request(URL, data=json.dumps(msg).encode(), headers=h, method="POST")
    return urllib.request.urlopen(req, timeout=600)

def relay(resp):
    ctype = resp.headers.get("Content-Type", "")
    if "text/event-stream" in ctype:
        buf = []
        for raw in resp:
            line = raw.decode("utf-8").rstrip("\r\n")
            if line.startswith("data:"): buf.append(line[5:].lstrip())
            elif line == "" and buf:
                data = "\n".join(buf); buf = []
                if data.strip(): emit(json.loads(data))
        if buf and "\n".join(buf).strip(): emit(json.loads("\n".join(buf)))
    else:
        body = resp.read()
        if body.strip(): emit(json.loads(body))

def reinit():
    blog("session expired; re-initializing")
    state["sid"] = None
    r = post(state["init"]); state["sid"] = r.headers.get("Mcp-Session-Id"); r.read()
    if state["inited"]: post(state["inited"]).read()

def handle(msg):
    mid = msg.get("id") if isinstance(msg, dict) else None
    try:
        if isinstance(msg, dict) and msg.get("method") == "initialize":
            ensure_gateway(); state["init"] = msg; state["sid"] = None
            r = post(msg); state["sid"] = r.headers.get("Mcp-Session-Id"); relay(r); return
        if isinstance(msg, dict) and msg.get("method") == "notifications/initialized": state["inited"] = msg
        try: r = post(msg)
        except urllib.error.URLError as e:
            stale = isinstance(e, urllib.error.HTTPError) and e.code in (404, 400)
            down = not isinstance(e, urllib.error.HTTPError)
            if (stale or down) and state["init"] and "method" in msg:
                if not port_open(): ensure_gateway()
                reinit(); r = post(msg)
            else: raise
        relay(r)
    except Exception as e:
        blog(f"bridge error: {type(e).__name__}: {str(e)[:200]}")
        if mid is not None and "method" in msg:
            emit({"jsonrpc": "2.0", "id": mid, "error": {"code": -32603, "message": f"gateway bridge error: {type(e).__name__}"}})

def bridge():
    ensure_gateway()
    for line in sys.stdin:
        line = line.strip()
        if not line: continue
        try: msg = json.loads(line)
        except json.JSONDecodeError: blog("ignoring non JSON input line"); continue
        if isinstance(msg, dict) and msg.get("method") == "initialize": handle(msg)  # keep ordering for init
        else: threading.Thread(target=handle, args=(msg,), daemon=True).start()
    if state["sid"]:
        try: urllib.request.urlopen(urllib.request.Request(URL, headers={"Mcp-Session-Id": state["sid"]}, method="DELETE"), timeout=5)
        except Exception: pass

if __name__ == "__main__":
    if "--supervise" in sys.argv: supervise()
    elif "--ensure" in sys.argv: ensure_gateway(); print("up" if port_open() else "down", file=sys.stderr)
    elif "--stop" in sys.argv:
        pf = os.path.join(RUNDIR, "gateway.pid")
        if os.path.exists(pf):
            try: os.kill(int(open(pf).read()), 15)
            except ProcessLookupError: pass
            os.remove(pf)
    else: bridge()
