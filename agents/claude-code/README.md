# Claude Code
Prompt: ../PROMPT.md (same for every agent). Run 3 fresh sessions per mode (standard, codeSearch), restart the gateway between modes with AGW_CONFIG=gateway/<mode>.yaml.

## Add the MCP server
claude mcp add agw -- /bin/sh /ABS/PATH/codesearch-agents-lab/bridge/start.sh   (check with /mcp)

## Read token usage
/cost at end of session, /context for tool-definition share; or claude -p "$(cat ../PROMPT.md)" --output-format json (usage field).

Record each run in results/results.csv.
