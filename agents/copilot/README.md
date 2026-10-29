# GitHub Copilot (VS Code agent mode)
Prompt: ../PROMPT.md (same for every agent). Run 3 fresh sessions per mode (standard, codeSearch), restart the gateway between modes with AGW_CONFIG=gateway/<mode>.yaml.

## Add the MCP server
.vscode/mcp.json: {"servers":{"agw":{"type":"stdio","command":"/bin/sh","args":["/ABS/PATH/codesearch-agents-lab/bridge/start.sh"]}}}

## Read token usage
No per-session token counter: use Chat: Show Chat Debug View / OTel export; note this limitation in results.

Record each run in results/results.csv.
