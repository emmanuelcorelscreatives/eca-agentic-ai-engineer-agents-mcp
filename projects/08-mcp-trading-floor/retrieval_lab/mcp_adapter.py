"""Actual MCP stdio client using a caller-pinned existing server command."""
from contextlib import asynccontextmanager
from .core import ControlledFetch, RetrievalError

@asynccontextmanager
async def session(command,args):
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    async with stdio_client(StdioServerParameters(command=command,args=list(args))) as streams:
        async with ClientSession(*streams) as client:
            await client.initialize()
            yield client

async def discover(client):
    result=await client.list_tools()
    return [{'name':tool.name,'inputSchema':tool.inputSchema,'description':tool.description} for tool in result.tools]

async def browser_extract(client,url,allowed_origins):
    """Read-only client API; caller must launch isolated browser + egress sandbox.

    The MCP server itself may offer mutation tools. This facade never dispatches
    those tools; network isolation is still required to block page subrequests.
    """
    policy=ControlledFetch(allowed_origins)
    if policy.origin(url) not in policy.origins: raise RetrievalError('browser destination denied')
    names={tool['name'] for tool in await discover(client)}
    if not {'browser_navigate','browser_snapshot'} <= names: raise RetrievalError('server lacks required browser tools')
    navigation=await client.call_tool('browser_navigate',{'url':url})
    if navigation.isError: raise RetrievalError('browser navigation failed')
    snapshot=await client.call_tool('browser_snapshot',{})
    if snapshot.isError: raise RetrievalError('browser snapshot failed')
    return {'url':url,'navigation':navigation.model_dump(mode='json'),'snapshot':snapshot.model_dump(mode='json')}
