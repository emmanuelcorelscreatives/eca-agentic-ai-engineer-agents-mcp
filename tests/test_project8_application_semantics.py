"""Authored actual-ASGI and local-dashboard acceptance tests; central QA executes."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

PROJECT=Path(__file__).resolve().parents[1]/'projects/08-mcp-trading-floor'
OPTIONAL=all(importlib.util.find_spec(name) is not None for name in ('fastapi','httpx'))

def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path)
 module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module

@unittest.skipUnless(OPTIONAL,'requires actual FastAPI/httpx optional runtime')
class ApplicationSemanticsTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
  self.env=patch.dict('os.environ',{'ACADEMY_PAPER_DB':str(Path(self.temp.name)/'paper.sqlite'),'ACADEMY_FEEDBACK_DB':str(Path(self.temp.name)/'feedback.sqlite'),'ACADEMY_LOCAL_TOKEN':'operator-test','ACADEMY_REVIEW_TOKEN':'reviewer-test'})
  self.env.start();self.addCleanup(self.env.stop)
  self.path=patch.object(sys,'path',[str(PROJECT),*sys.path]);self.path.start();self.addCleanup(self.path.stop)
  self.api=load('p8_semantic_api',PROJECT/'api.py')
  from fastapi.testclient import TestClient
  self.client=TestClient(self.api.app)
  self.operator={'X-Academy-Token':'operator-test'};self.reviewer={'X-Academy-Review-Token':'reviewer-test'}
 def proposal(self):
  r=self.client.post('/proposals',json={'symbol':'ACA','quantity':5,'side':'BUY'},headers=self.operator)
  self.assertEqual(r.status_code,200,r.text);return r.json()
 def test_roles_approval_execute_and_feedback_are_distinct(self):
  p=self.proposal();body={'proposal':p['proposal'],'action':'APPROVE'}
  self.assertEqual(self.client.post('/reviews',json=body,headers=self.operator).status_code,401)
  self.assertEqual(self.client.post('/execute',json={'proposal':p['proposal'],'request_id':'one'},headers=self.operator).status_code,422)
  self.assertEqual(self.client.post('/reviews',json=body,headers=self.reviewer).status_code,200)
  result=self.client.post('/execute',json={'proposal':p['proposal'],'request_id':'one'},headers=self.operator).json()
  self.assertEqual(result['cash'],'9373.75')
  self.assertEqual(self.client.post('/execute',json={'proposal':p['proposal'],'request_id':'one'},headers=self.operator).json(),result)
  feedback={'submission_id':'review-one',**{k:result['feedback'][k] for k in ('run_id','output_sha256')},'rating':4,'comment':'Evidence is clear','correction':'Clarify historical snapshot'}
  reply=self.client.post('/feedback',json=feedback,headers=self.reviewer)
  self.assertEqual(reply.status_code,200,reply.text);self.assertFalse(reply.json()['execution_approval'])
  report=self.client.get('/feedback',headers=self.operator).json()
  self.assertEqual(report['count'],1);self.assertEqual(report['corrections'],1)
 def test_unknown_feedback_and_rejected_proposal(self):
  p=self.proposal()
  rejection=self.client.post('/reviews',json={'proposal':p['proposal'],'action':'REJECT','reason':'Need stronger evidence'},headers=self.reviewer)
  self.assertEqual(rejection.status_code,200)
  state=self.client.get('/state').json();self.assertEqual(state['proposals'][0]['status'],'REJECTED');self.assertEqual(state['transactions'],[])
  bad={'submission_id':'invented','run_id':'not-a-run','output_sha256':'a'*64,'rating':5,'comment':'Invented feedback'}
  self.assertEqual(self.client.post('/feedback',json=bad,headers=self.reviewer).status_code,422)
 def test_gradio_shares_persistent_reviewed_account(self):
  if importlib.util.find_spec('gradio') is None:self.skipTest('requires actual Gradio')
  gui=load('p8_semantic_gradio',PROJECT/'gradio_app.py')
  research,decision,state=gui.inspect('ACA',5,gui.DATABASE)
  self.assertTrue(decision['allowed']);self.assertEqual(research['symbol'],'ACA')
  result,_=gui.review_and_execute({'proposal':decision['proposal']},'reviewer-test','APPROVE')
  self.assertEqual(result['status'],'APPROVED')
  fill,dashboard=gui.execute_approved({'proposal':decision['proposal']},'gradio-one')
  self.assertEqual(fill['cash'],'9373.75');self.assertEqual(dashboard['portfolio']['positions'],{'ACA':5})
  self.assertEqual(len(dashboard['transactions']),1)

if __name__=='__main__':unittest.main()
