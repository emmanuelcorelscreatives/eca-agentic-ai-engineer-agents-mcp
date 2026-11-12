"""Authored role-contract tests; scripted replies are not real model observations."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

PROJECT=Path(__file__).resolve().parents[1]/'projects/08-mcp-trading-floor'
class CapstoneRoleTests(unittest.IsolatedAsyncioTestCase):
 async def asyncSetUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
  self.path=patch.object(sys,'path',[str(PROJECT),*sys.path]);self.path.start();self.addCleanup(self.path.stop)
  from capstone_agents import TradingAgents,AgentContractError
  from services import ToolServices
  self.Agent=TradingAgents;self.Error=AgentContractError;self.services=ToolServices(str(Path(self.temp.name)/'paper.sqlite'))
  self.calls=[]
 async def scripted_model(self,role,payload):
  self.calls.append(role)
  if role=='researcher':return {'evidence_id':'fixture-aca-001','exact_quote':'Fictional component maker','uncertainty':0.3}
  if role=='strategist':return {'action':'BUY','quantity':5,'rationale':'Bounded fictional practice proposal','uncertainty':0.4}
  return {'explanation':'Current deterministic risk permits this bounded simulated order; human approval is still required.'}
 async def test_real_roles_stop_for_approval_and_resume_exact_once(self):
  agent=self.Agent(self.services,self.scripted_model)
  result=await agent.run('ACA',run_id='one')
  self.assertEqual(self.calls,['researcher','strategist','risk_explainer'])
  self.assertEqual(result['status'],'AWAITING_HUMAN_APPROVAL')
  self.assertEqual(self.services.portfolio()['cash'],'10000.00')
  with self.assertRaises(ValueError):agent.resume_approved('one','order-one')
  from trading_floor import Proposal
  with self.services.connection() as floor:floor.approve(Proposal(**result['proposal']),'human')
  filled=agent.resume_approved('one','order-one')
  self.assertEqual(filled['execution']['cash'],'9373.75')
  self.assertEqual(agent.resume_approved('one','order-one')['execution'],filled['execution'])
  await agent.run('ACA',run_id='one');self.assertEqual(len(self.calls),3)
 async def test_unsupported_research_blocks_downstream_roles(self):
  async def bad(role,payload):return {'evidence_id':'invented','exact_quote':'unsupported','uncertainty':0.1}
  agent=self.Agent(self.services,bad)
  with self.assertRaises(self.Error):await agent.run('ACA',run_id='unsupported')
  prior=await agent.run('ACA',run_id='unsupported')
  self.assertEqual(prior['status'],'FAILED_REQUIRES_REVIEW')
  self.assertEqual(prior['model_calls'],1)
 async def test_human_hold_is_explicit_without_paper_execution(self):
  async def hold(role,payload):
   if role=='researcher':return await self.scripted_model(role,payload)
   return {'action':'HOLD','quantity':0,'rationale':'Evidence is insufficient','uncertainty':0.9}
  result=await self.Agent(self.services,hold).run('ACA')
  self.assertEqual(result['status'],'HOLD_INSUFFICIENT_CONVICTION')
  with self.services.connection() as floor:self.assertEqual(floor.transactions(),[])

if __name__=='__main__':unittest.main()
