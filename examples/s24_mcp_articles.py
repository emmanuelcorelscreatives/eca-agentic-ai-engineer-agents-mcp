"""Actual shared MCP source for both Agno and Mastra clients."""
from fastmcp import FastMCP
from examples.s24_triage import lookup_ticket, search_articles
server=FastMCP('Academy articles')
server.tool()(lookup_ticket)
server.tool()(search_articles)
if __name__ == '__main__':
    server.run(transport='stdio')
