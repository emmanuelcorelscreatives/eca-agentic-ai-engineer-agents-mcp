"""Optional MCP v1 stdio adapter: model tools cannot approve or execute orders."""
from mcp.server.fastmcp import FastMCP
from services import ToolServices

mcp = FastMCP('Academy synthetic paper market')
services = ToolServices()  # Path/configuration only; no cross-thread DB connection.

@mcp.tool()
def research_company(symbol: str) -> dict:
    """Read synthetic company evidence; no real market data."""
    return services.research_company(symbol)

@mcp.tool()
def propose_order(symbol: str, quantity: int, side: str = 'BUY') -> dict:
    """Return a proposal and risk result; cannot approve or trade."""
    return services.propose_order(symbol, quantity, side)

@mcp.tool()
def portfolio() -> dict:
    """Read simulated cash, positions and equity."""
    return services.portfolio()

@mcp.tool()
def search_research(query: str, limit: int = 5) -> dict:
    """Search only the local synthetic research corpus, with evidence IDs."""
    return services.search_research(query, limit)

@mcp.tool()
def grounded_brief(query: str) -> dict:
    """Retrieve grounded extracts/citations, abstaining when no source matches."""
    return services.grounded_brief(query)

@mcp.tool()
def remember(namespace: str, key: str, value: str) -> dict:
    """Store bounded course memory. Do not send secrets or personal data."""
    return services.remember(namespace, key, value)

@mcp.tool()
def recall(namespace: str, key: str) -> dict:
    """Read memory from an exact course namespace/key."""
    return services.recall(namespace, key)

@mcp.tool()
def orchestrate(symbol: str, quantity: int) -> dict:
    """Run reference research/strategy/risk roles, stopping for human approval."""
    return services.orchestrate(symbol, quantity)

if __name__ == '__main__': mcp.run(transport='stdio')
