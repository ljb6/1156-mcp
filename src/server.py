import os
from mcp.server.fastmcp import FastMCP
from tools import teams

port = int(os.environ.get("PORT", 8000))
mcp = FastMCP("1156-mcp", host="0.0.0.0", port=port)

teams.register(mcp)

if __name__ == "__main__":
    mcp.run(transport="sse")
