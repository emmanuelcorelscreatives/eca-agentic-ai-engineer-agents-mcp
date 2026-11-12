"""Genuine MCP research -> model specialist -> paper-review workflow.

Source authored for central QA. Explicit --run permits configured model charges;
no request occurs on import. Execution/approval remains a separate human action.
"""
import argparse
import asyncio
import json
import os
from pathlib import Path
import sys
import uuid

async def run(args):
    from mcp import ClientSession,StdioServerParameters
    from mcp.client.stdio import stdio_client
    from capstone_agents import TradingAgents
    from services import ToolServices
    from sdk_role_provider import SDKRoleProvider
    from evaluation_lab.tracing import CorrelatedTrace,dispatch_mcp
    root=Path(__file__).resolve().parent
    run_id=uuid.uuid4().hex
    args.artifact_dir.mkdir(parents=True,exist_ok=True,mode=0o700)
    trace=CorrelatedTrace(args.artifact_dir/(run_id+'.jsonl'),run_id=run_id)
    provider=SDKRoleProvider(args.model,args.artifact_dir)
    params=StdioServerParameters(command=sys.executable,args=[str(root/'mcp_server.py')],
                                env={'ACADEMY_PAPER_DB':str(Path(args.database).resolve())})
    try:
        async with stdio_client(params) as streams:
            async with ClientSession(*streams) as session:
                await session.initialize()
                async def research(symbol):
                    result=await dispatch_mcp(trace,session,tool_name='research_company',arguments={'symbol':symbol})
                    if result.structuredContent is not None:return result.structuredContent
                    return json.loads('\n'.join(x.text for x in result.content if hasattr(x,'text')))
                workflow=TradingAgents(ToolServices(args.database),provider,trace=trace,research_tool=research)
                result=await workflow.run(args.symbol,run_id=run_id)
                print(json.dumps(result,indent=2))
    finally:
        trace.close()
        await provider.close()

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',action='store_true');parser.add_argument('--model',required=True)
    parser.add_argument('--database',required=True);parser.add_argument('--artifact-dir',required=True,type=Path)
    parser.add_argument('--symbol',default='ACA');args=parser.parse_args()
    if not args.run:parser.error('Nothing sent. Explicit --run required; configured model calls may incur charges.')
    asyncio.run(run(args))
