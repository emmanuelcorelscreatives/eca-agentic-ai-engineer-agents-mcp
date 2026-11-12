"""Authored targeted trace tests. Scripted public actions are not model inference."""
import importlib.util
import json
import os
from pathlib import Path
import sys
from types import SimpleNamespace as NS
import unittest

PROJECT=Path(__file__).resolve().parents[1]/'projects/08-mcp-trading-floor'
spec=importlib.util.spec_from_file_location('academy_p8_public_trace_v2',PROJECT/'agent_harness.py')
h=importlib.util.module_from_spec(spec);sys.modules[spec.name]=h;spec.loader.exec_module(h)
HAS_SDK=importlib.util.find_spec('mcp') is not None
if os.environ.get('ACADEMY_REQUIRE_PROJECT8_TRACE_SDK')=='1' and not HAS_SDK:
 raise RuntimeError('Actual SDK trace test required; install selected runtime instead of counting a skip as PASS')

class FixtureSession:
 async def list_tools(self):return NS(tools=[NS(name='lookup',inputSchema={'type':'object'})])
 async def call_tool(self,name,arguments):
  return {'isError':arguments.get('fail',False),'content':[{'type':'text','text':'PRIVATE_RESPONSE_NOT_TRACE'}]}

class ScriptedActions:
 def __init__(self,actions):self.actions=iter(actions)
 async def next_action(self,messages,tools):return next(self.actions)

class PublicTraceTests(unittest.IsolatedAsyncioTestCase):
 async def test_public_routes_finish_correlation_response_status_and_no_private_text(self):
  registry=h.MCPRegistry({'first':FixtureSession(),'second':FixtureSession()}, {'first::lookup','second::lookup'},schema_validator=lambda args,schema:None)
  await registry.discover()
  provider=ScriptedActions([h.ToolCall('first::lookup',{'query':'PRIVATE_QUERY_NOT_TRACE'}),
                            h.ToolCall('second::lookup',{'fail':True}),h.FinalAnswer('PRIVATE_FINAL_NOT_TRACE')])
  agent=h.AgentHarness(registry,provider)
  result=await agent.run('PRIVATE_QUESTION_NOT_TRACE')
  self.assertEqual(result.status,'COMPLETE')
  self.assertEqual([row['action'] for row in agent.trace],['tool','tool','finish'])
  self.assertEqual([row['server'] for row in agent.trace[:2]],['first','second'])
  starts=[row for row in registry.trace if row['event']=='start'];ends=[row for row in registry.trace if row['event']=='end']
  for decision,start,end in zip(agent.trace,starts,ends):
   self.assertEqual(decision['run_id'],start['run_id']);self.assertEqual(decision['decision_id'],start['decision_id'])
   self.assertEqual(start['call_id'],end['call_id']);self.assertEqual(start['arguments_digest'],decision['arguments_digest'])
   self.assertGreaterEqual(end['latency_ms'],0)
  self.assertEqual([row['status'] for row in ends],['ok','error']);self.assertEqual(ends[1]['error_code'],'TOOL_ERROR')
  self.assertEqual(len(ends[0]['response_digest']),64)
  serialized=json.dumps({'agent':agent.trace,'tools':registry.trace})
  for private in ['PRIVATE_QUERY_NOT_TRACE','PRIVATE_RESPONSE_NOT_TRACE','PRIVATE_QUESTION_NOT_TRACE','PRIVATE_FINAL_NOT_TRACE']:
   self.assertNotIn(private,serialized)
  self.assertNotIn('reasoning',serialized);self.assertNotIn('chain_of_thought',serialized)
 async def test_canonical_private_digest_redacts_secret_fields_and_has_per_registry_key(self):
  one=h.MCPRegistry({},set());two=h.MCPRegistry({},set())
  a={'query':'private','password':'first-secret','nested':{'b':2,'a':1}}
  b={'nested':{'a':1,'b':2},'password':'other-secret','query':'private'}
  self.assertEqual(one.argument_trace(a)['arguments_digest'],one.argument_trace(b)['arguments_digest'])
  self.assertNotEqual(one.argument_trace(a)['arguments_digest'],two.argument_trace(a)['arguments_digest'])
  self.assertNotIn('private',json.dumps(one.argument_trace(a)))
  self.assertEqual(one.argument_trace('private'),{'argument_metadata_status':'not_an_object'})

@unittest.skipUnless(HAS_SDK,'actual optional MCP SDK required')
class ActualSdkPublicTraceTests(unittest.IsolatedAsyncioTestCase):
 async def test_actual_sdk_success_failure_join_public_decisions(self):
  from mcp import ClientSession,StdioServerParameters
  from mcp.client.stdio import stdio_client
  params=StdioServerParameters(command=sys.executable,args=[str(PROJECT/'mcp_lab/server.py')],
                              env={'ACADEMY_MCP_ROOT':str(PROJECT/'mcp_lab/fixtures')})
  async with stdio_client(params) as streams:
   async with ClientSession(*streams) as client:
    await client.initialize()
    registry=h.MCPRegistry({'course':client},{'course::quote','course::sampled_summary'})
    await registry.discover()
    # The second real server tool fails its own length check BEFORE asking for
    # sampling. No model/provider callback or inference occurs in this test.
    provider=ScriptedActions([h.ToolCall('course::quote',{'symbol':'ACME','quantity':1}),
                             h.ToolCall('course::sampled_summary',{'topic':'x'*201}),h.FinalAnswer('Observed one quote and one tool error.')])
    agent=h.AgentHarness(registry,provider);result=await agent.run('Read the synthetic quote and exercise the bounded error.')
    self.assertEqual(result.status,'COMPLETE')
    ends=[row for row in registry.trace if row['event']=='end']
    self.assertEqual([row['status'] for row in ends],['ok','error'])
    self.assertEqual(ends[1]['error_code'],'TOOL_ERROR')
    for decision in agent.trace[:2]:
     starts=[row for row in registry.trace if row['event']=='start' and row['decision_id']==decision['decision_id']]
     self.assertEqual(len(starts),1);self.assertEqual(starts[0]['server'],'course')
    self.assertEqual(agent.trace[-1]['action'],'finish')

if __name__=='__main__':unittest.main()
