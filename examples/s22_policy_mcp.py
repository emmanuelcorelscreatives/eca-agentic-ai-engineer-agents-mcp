"""Read-only actual MCP server for shared policy fixtures."""
from mcp.server.fastmcp import FastMCP
from examples.s22_policy import PolicyService
server = FastMCP('Academy policies')
@server.tool()
def lookup_policy(product_id: str) -> dict:
    """Lookup synthetic product policy."""
    return PolicyService().lookup(product_id)
if __name__ == '__main__':
    server.run(transport='stdio')
