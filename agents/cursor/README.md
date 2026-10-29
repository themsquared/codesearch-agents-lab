# Cursor
Prompt: ../PROMPT.md (same for every agent). Run 3 fresh sessions per mode (standard, codeSearch), restart the gateway between modes with AGW_CONFIG=gateway/<mode>.yaml.

## Add the MCP server
.cursor/mcp.json: {"mcpServers":{"agw":{"command":"/bin/sh","args":["/ABS/PATH/codesearch-agents-lab/bridge/start.sh"]}}}  Agent mode, other MCP servers off.

## Read token usage
Per-request tokens in cursor.com dashboard Usage; screenshot the context meter.

Record each run in results/results.csv.
