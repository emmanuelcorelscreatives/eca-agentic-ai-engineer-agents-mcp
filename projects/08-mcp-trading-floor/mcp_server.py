"""Optional MCP v1 stdio adapter: model tools cannot approve or execute orders."""
from mcp.server.fastmcp import FastMCP
from services import ToolServices
import json
import os

mcp = FastMCP('Academy synthetic paper market')
services = ToolServices()  # Path/configuration only; no cross-thread DB connection.

def _configured_memory_namespaces(name):
    """Operator configuration, never a model-supplied owner/authentication claim."""
    value=json.loads(os.environ.get(name,'["course-notes"]'))
    if not isinstance(value,list) or any(not isinstance(item,str) for item in value):
        raise ValueError('memory namespace configuration must be a JSON string array')
    if {'agent-runs','orchestration'} & set(value):
        raise ValueError('application checkpoint namespaces are not model-accessible')
    return frozenset(value)

_forbidden_memory=json.loads(os.environ.get('ACADEMY_MEMORY_FORBIDDEN_STRINGS','[]'))
if not isinstance(_forbidden_memory,list):
    raise ValueError('memory forbidden-string configuration must be a JSON string array')
memory_services=ToolServices(
    memory_read_namespaces=_configured_memory_namespaces('ACADEMY_MEMORY_READ_NAMESPACES'),
    memory_write_namespaces=_configured_memory_namespaces('ACADEMY_MEMORY_WRITE_NAMESPACES'),
    memory_forbidden_strings=_forbidden_memory,
)

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
    """Store within operator-configured scope. No secrets or personal data."""
    if namespace in ('agent-runs','orchestration'):
        raise ValueError('application checkpoint namespace is not model-writable')
    return memory_services.remember(namespace, key, value)

@mcp.tool()
def recall(namespace: str, key: str) -> dict:
    """Read an exact key only within operator-configured memory scope."""
    return memory_services.recall(namespace, key)

@mcp.tool()
def search_memory(namespace: str, query: str, limit: int = 5) -> dict:
    """Search a configured course namespace; bounded literal results only."""
    return memory_services.search_memory(namespace, query, limit)

@mcp.tool()
def orchestrate(symbol: str, quantity: int) -> dict:
    """Run reference research/strategy/risk roles, stopping for human approval."""
    return services.orchestrate(symbol, quantity)

if __name__ == '__main__': mcp.run(transport='stdio')
