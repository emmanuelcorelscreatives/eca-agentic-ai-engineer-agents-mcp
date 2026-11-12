"""Real MCP stdio server. Run from repo root: python3 -m examples.s21_mcp_inventory."""
from mcp.server.fastmcp import FastMCP
from examples.s21_inventory import lookup_stock, estimate_delivery
server = FastMCP('Academy synthetic inventory')
server.tool()(lookup_stock)
server.tool()(estimate_delivery)
if __name__ == '__main__':
    server.run(transport='stdio')
