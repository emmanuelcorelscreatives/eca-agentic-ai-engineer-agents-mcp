"""Real Agno MCP agent lifecycle. Construction/discovery is not a model run."""
from contextlib import asynccontextmanager
from pathlib import Path
import sys

READ_ONLY_TOOLS = frozenset({'lookup_ticket', 'search_articles'})


@asynccontextmanager
async def build_mcp_agent(model: str, *, api_key: str | None = None):
    """Yield an Agent only while its discovered, allowlisted MCP toolkit is open.

    Import is lazy so ordinary offline exercises do not require Agno. The child
    server receives no provider credentials: it only reads the Academy fixture.
    Use ``async with build_mcp_agent(...) as agent``; never return a disconnected
    agent from this context. Calls to agent.arun are separately authorized live
    provider calls and are deliberately absent from this factory.
    """
    if not model:
        raise ValueError('Explicit model ID required')
    from agno.agent import Agent
    from agno.models.openai import OpenAIChat
    from agno.tools.mcp import MCPTools
    from mcp import StdioServerParameters
    from examples.s24_triage import triage_schema

    root = Path(__file__).resolve().parents[1]
    toolkit = MCPTools(server_params=StdioServerParameters(
        command=sys.executable, args=['-m', 'examples.s24_mcp_articles'],
        cwd=str(root), env={'PYTHONPATH': str(root)}),
        include_tools=sorted(READ_ONLY_TOOLS))
    async with toolkit:
        # Some SDK versions discover during entry; explicitly rebuild if needed.
        if not toolkit.functions:
            await toolkit.build_tools()
        if set(toolkit.functions) != READ_ONLY_TOOLS:
            raise RuntimeError('MCP discovery does not match the read-only allowlist')
        agent = Agent(name='Academy MCP triage',
            model=OpenAIChat(id=model, api_key=api_key), tools=[toolkit],
            output_schema=triage_schema(),
            instructions='Use only retrieved synthetic ticket/article evidence. '
                         'Cite actual article IDs. Report unknowns; draft only.')
        yield agent
