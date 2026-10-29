# OpenAI Codex CLI
Prompt: ../PROMPT.md (same for every agent). Run 3 fresh sessions per mode (standard, codeSearch), restart the gateway between modes with AGW_CONFIG=gateway/<mode>.yaml.

## Add the MCP server
~/.codex/config.toml:\n[mcp_servers.agw]\ncommand = "/bin/sh"\nargs = ["/ABS/PATH/codesearch-agents-lab/bridge/start.sh"]

## Read token usage
codex exec --json "$(cat ../PROMPT.md)" and sum token_count events; /status in TUI.

Record each run in results/results.csv.
