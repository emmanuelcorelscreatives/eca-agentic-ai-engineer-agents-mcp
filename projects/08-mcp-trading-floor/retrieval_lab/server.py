"""Custom research MCP server. Launch explicitly; does not replace existing servers."""
import os
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from .core import ControlledFetch, SearchProvider, QdrantRetrieval, CapabilityCatalogue

mcp=FastMCP('Academy controlled research')
fetcher=ControlledFetch([item for item in os.environ.get('ACADEMY_FETCH_ORIGINS','').split(',') if item])
catalogue=CapabilityCatalogue()

@mcp.tool()
def fetch_page(url: str) -> dict:
    """Fetch an explicitly allowlisted HTTP page; return provenance."""
    from dataclasses import asdict
    return asdict(fetcher.fetch(url))

@mcp.tool()
def search_web(query: str, limit: int = 5) -> dict:
    """Query an explicitly configured real SearxNG-compatible endpoint."""
    endpoint=os.environ.get('ACADEMY_SEARCH_ENDPOINT')
    if not endpoint: raise ValueError('No search provider configured; live search unavailable')
    return SearchProvider(endpoint,fetcher).search(query,limit)

@mcp.tool()
def discover_capability(capability: str) -> list[str]:
    """Discover tools within operator-granted capabilities."""
    permissions=set(os.environ.get('ACADEMY_CAPABILITIES','research').split(','))
    return catalogue.discover(capability,permissions)

if __name__=='__main__': mcp.run(transport='stdio')
