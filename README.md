# codesearch-agents-lab

Measures how many tokens a coding agent spends on the same read-only GitHub task when its GitHub MCP server sits behind agentgateway in `standard` mode vs `codeSearch` mode. Agents covered: Claude Code, Cursor, OpenAI Codex CLI, GitHub Copilot agent mode, Muse, Factory Droid.

Background and the first result (Grok Bot, 89,038 -> 3,809 tokens): https://webofmike.com/agentgateway-codesearch-grokbot/

Disclosure: the author works at Solo.io, which makes agentgateway. **Tool modes (`search`, `code`, `codeSearch`) are an agentgateway Enterprise feature and need a license.** Open source agentgateway does not have them; `standard` is the baseline.

## Layout
- `gateway/standard.yaml`, `gateway/codeSearch.yaml`: loopback 127.0.0.1:3110, allowlist of the 57 read-only GitHub tools.
- `bridge/start.sh`: stdio MCP server for agents. Starts the gateway if needed, then bridges to http://127.0.0.1:3110/mcp. Logs scrub secrets.
- `bridge/gh_upstream.py`: runs `github-mcp-server stdio --read-only --toolsets=all` with a clean env.
- `harness/`: gateway-side token counter (tiktoken cl100k), agent-independent baseline.
- `agents/<agent>/README.md`: how to wire that agent and read its usage. `agents/PROMPT.md`: the fixed task.
- `results/results.csv`: one row per run.

## Setup
1. Put binaries in `bin/` (or set `AGW_BIN`, `GITHUB_MCP_BIN`): Enterprise `agentgateway`, [github-mcp-server](https://github.com/github/github-mcp-server).
2. Export `ENTERPRISE_AGENTGATEWAY_LICENSE_KEY` and `GITHUB_READONLY_PAT` (fine-grained, read-only). Or put them in `secrets/license` and `secrets/github_pat` (gitignored, chmod 600).
3. Pick the mode: `export AGW_CONFIG=$PWD/gateway/codeSearch.yaml` (or `standard.yaml`). Run gateway: `bridge/start.sh --ensure`; stop: `bridge/start.sh --stop`.
4. Baseline: `cd harness && pip install requests tiktoken && GH_OWNER=<you> python3 gh_modes.py codeSearch`.
5. Point each agent at `bridge/start.sh` per `agents/<agent>/README.md`, run `agents/PROMPT.md` 3x per mode, log to `results/results.csv`.

Switching modes: `bridge/start.sh --stop`, change `AGW_CONFIG`, start again.
