#!/usr/bin/env python3
# Starts github-mcp-server (read only, all toolsets) with a clean env: PATH, HOME and the PAT only.
# PAT from env GITHUB_READONLY_PAT or <repo>/secrets/github_pat. Binary from GITHUB_MCP_BIN or <repo>/bin/github-mcp-server.
import os
root = os.environ.get("LAB_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pat = os.environ.get("GITHUB_READONLY_PAT") or open(os.path.join(root, "secrets", "github_pat")).read().strip()
env = {"PATH": "/usr/bin:/bin", "HOME": "/tmp/agw-lab-gh-home", "GITHUB_PERSONAL_ACCESS_TOKEN": pat, "GITHUB_READ_ONLY": "1"}
os.makedirs(env["HOME"], mode=0o700, exist_ok=True)
b = os.environ.get("GITHUB_MCP_BIN") or os.path.join(root, "bin", "github-mcp-server")
os.execve(b, [b, "stdio", "--read-only", "--toolsets=all"], env)
