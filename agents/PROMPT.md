Using only the `agw` MCP server (read-only GitHub), do this for GitHub user <OWNER>:
1. Find their 8 most recently updated repos.
2. For the first 3 repos that have open pull requests, read up to 3 open PRs each.
3. Return ONLY a JSON array: [{"repo": ..., "pr": <number>, "title": ..., "files": <count of changed files>}].
Do not use web search, shell, or any other tool. Do not write anything.
