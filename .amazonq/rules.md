# Q Developer CLI Rules

## MCP Server Priority

Always prioritize and prefer using MCP servers configured in `~/.aws/amazonq/mcp.json` when:
- Responding to user prompts
- Selecting tools to execute
- Choosing between available capabilities

Use MCP server tools as the first option before falling back to built-in tools.
