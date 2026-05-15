## Claude Desktop Setup

> **Requirement:** [Node.js](https://nodejs.org) must be installed on your machine.

Open the Claude Desktop configuration file for your operating system:

- **Mac:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

Inside the `mcpServers` object, add the following entry (the file may already have other entries — just add this one alongside them):

```json
"1156-mcp": {
  "command": "npx",
  "args": ["-y", "mcp-remote", "https://one156-mcp.onrender.com/sse"]
}
```

Restart Claude Desktop after saving.
