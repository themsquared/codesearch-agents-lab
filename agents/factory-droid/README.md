# Factory Droid
Prompt: ../PROMPT.md (same for every agent). Run 3 fresh sessions per mode (standard, codeSearch), restart the gateway between modes with AGW_CONFIG=gateway/<mode>.yaml.

## Add the MCP server
droid mcp add agw "/bin/sh /ABS/PATH/codesearch-agents-lab/bridge/start.sh"  (or ~/.factory/mcp.json)

## Read token usage
droid exec -o json "$(cat ../PROMPT.md)" (usage), /cost in TUI.

Record each run in results/results.csv.
