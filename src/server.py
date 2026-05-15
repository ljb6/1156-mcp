from mcp.server.fastmcp import FastMCP
from tools import teams

mcp = FastMCP("1156-mcp")

teams.register(mcp)

if __name__ == "__main__":
    mcp.run()
