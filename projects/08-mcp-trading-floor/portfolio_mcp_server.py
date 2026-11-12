"""Trusted paper-execution MCP service, separate from research-facing tools.

Human approval is created only through the separately authenticated application
or explicit local reviewer. No MCP tool grants approval. Use a separate client
allowlist for this service; a model may request only an already-approved fill.
"""
from mcp.server.fastmcp import FastMCP
from services import ToolServices
from trading_floor import Proposal

mcp=FastMCP('Academy approved paper portfolio')
services=ToolServices()

@mcp.tool()
def portfolio_state() -> dict:
    """Read synthetic cash, marked positions and current account revision."""
    return services.portfolio()

@mcp.tool()
def paper_transactions() -> list[dict]:
    """Read actual persisted simulated fills, not suggested orders."""
    with services.connection() as floor:return floor.transactions()

@mcp.tool()
def pending_proposals() -> list[dict]:
    """Read actual proposal and human review state."""
    with services.connection() as floor:return floor.proposal_history()

@mcp.tool()
def execute_approved_order(symbol:str,side:str,quantity:int,price:str,evidence_id:str,request_id:str)->dict:
    """Execute only an exact unexpired human-approved proposal at current revision.

    Cannot create approval, alter quote or bypass deterministic risk checks.
    """
    with services.connection() as floor:
        return floor.execute(Proposal(symbol,side,quantity,price,evidence_id),request_id)

if __name__=='__main__':mcp.run(transport='stdio')
