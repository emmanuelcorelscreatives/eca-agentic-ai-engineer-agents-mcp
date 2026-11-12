"""Authored real trading-service SDK tests; central QA must execute without skips."""
import asyncio
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

PROJECT=Path(__file__).resolve().parents[1]/'projects/08-mcp-trading-floor'
HAS_SDK=importlib.util.find_spec('mcp') is not None
if os.environ.get('ACADEMY_REQUIRE_PROJECT8_SDK')=='1' and not HAS_SDK:
 raise RuntimeError('Required SDK runtime missing; cannot count skipped tests as PASS')

def object_result(result):
 if result.isError:raise AssertionError(str(result))
 if result.structuredContent is not None:return result.structuredContent
 return json.loads('\n'.join(item.text for item in result.content if hasattr(item,'text')))

@unittest.skipUnless(HAS_SDK,'requires official optional MCP SDK')
class TradingMcpTests(unittest.IsolatedAsyncioTestCase):
 async def test_actual_research_server_fixture_and_reserved_checkpoint_guard(self):
  from mcp import ClientSession,StdioServerParameters
  from mcp.client.stdio import stdio_client
  with tempfile.TemporaryDirectory() as tmp:
   args=StdioServerParameters(command=sys.executable,args=[str(PROJECT/'mcp_server.py')],env={'ACADEMY_PAPER_DB':str(Path(tmp)/'account.sqlite')})
   async with stdio_client(args) as streams:
    async with ClientSession(*streams) as session:
     await session.initialize();names={x.name for x in (await session.list_tools()).tools}
     self.assertIn('research_company',names);self.assertNotIn('approve',names)
     research=object_result(await session.call_tool('research_company',{'symbol':'ACA'}))
     self.assertEqual(research['evidence_id'],'fixture-aca-001');self.assertTrue(research['synthetic'])
     proposal=object_result(await session.call_tool('propose_order',{'symbol':'ACA','quantity':5}))
     self.assertEqual(proposal['proposal']['price'],'125.25')
     denied=await session.call_tool('remember',{'namespace':'agent-runs','key':'forged','value':'approved'})
     self.assertTrue(denied.isError)
 async def test_trusted_portfolio_tool_requires_actual_account_approval(self):
  from mcp import ClientSession,StdioServerParameters
  from mcp.client.stdio import stdio_client
  with tempfile.TemporaryDirectory() as tmp:
   database=str(Path(tmp)/'account.sqlite')
   sys.path.insert(0,str(PROJECT))
   try:
    from trading_floor import TradingFloor
    floor=TradingFloor(database);proposal=floor.propose('ACA',5);floor.close()
    args=StdioServerParameters(command=sys.executable,args=[str(PROJECT/'portfolio_mcp_server.py')],env={'ACADEMY_PAPER_DB':database})
    async with stdio_client(args) as streams:
     async with ClientSession(*streams) as session:
      await session.initialize();payload={**proposal.__dict__,'request_id':'sdk-order-1'}
      denied=await session.call_tool('execute_approved_order',payload);self.assertTrue(denied.isError)
      floor=TradingFloor(database)
      try:floor.approve(proposal,'explicit automated-test reviewer')
      finally:floor.close()
      first=object_result(await session.call_tool('execute_approved_order',payload))
      second=object_result(await session.call_tool('execute_approved_order',payload))
      self.assertEqual(first,second);self.assertEqual(first['cash'],'9373.75')
      state=object_result(await session.call_tool('portfolio_state',{}))
      self.assertEqual(state['positions'],{'ACA':5});self.assertEqual(state['revision'],1)
   finally:sys.path.remove(str(PROJECT))

if __name__=='__main__':unittest.main()
