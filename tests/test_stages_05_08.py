import importlib.util
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
def load(name,folder,file):
 spec=importlib.util.spec_from_file_location(name,ROOT/'projects'/folder/(file+'.py'));mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod);return mod
twin=load('twin','01-digital-twin','twin')
workflow=load('twin_workflow','01-digital-twin','workflow')
ingest=load('twin_ingest','01-digital-twin','pdf_ingest')
pdf=load('twin_pdf','01-digital-twin','make_pdf_fixture')
sales=load('sales','02-sales-team','sales')
orch=load('sales_orch','02-sales-team','orchestration')
class ContextAndNotificationTests(unittest.TestCase):
 def setUp(self):
  self.app=twin.DigitalTwin([dict(id='a',title='Approved',text='Python',approved=True),dict(id='b',title='Private',text='secret',approved=False)]);self.addCleanup(self.app.db.close)
 def test_context_excludes_private_and_respects_budget(self):
  result=workflow.context_for('Python?',self.app.sections,250)
  self.assertLessEqual(result['characters_used'],250);self.assertNotIn('secret',str(result))
 def test_too_small_context_fails(self):
  with self.assertRaises(ValueError):workflow.context_for('Python?',self.app.sections,10)
 def test_visible_events(self):
  result=list(workflow.answer_with_status(self.app,'Python'))
  self.assertEqual([r['status']['phase'] for r in result],['retrieving','ready'])
  self.assertEqual(result[-1]['result']['citations'],['a'])
 def test_notification_failure_does_not_lose_contact(self):
  def fail(payload):raise OSError('offline')
  result=workflow.contact_and_notify(self.app,'A','a@example.invalid','Hello',True,fail)
  self.assertEqual(result['notification'],'adapter_failed');self.assertEqual(self.app.db.execute('SELECT COUNT(*) FROM contacts').fetchone()[0],1)
 def test_notification_receives_no_personal_details(self):
  notices=[];workflow.contact_and_notify(self.app,'A','a@example.invalid','Hello',True,notices.append)
  self.assertEqual(set(notices[0]),{'contact_id'})
class PDFTests(unittest.TestCase):
 def test_generated_pdf_and_unapproved_extraction(self):
  with tempfile.TemporaryDirectory() as temp:
   path=Path(temp)/'profile.pdf';pdf.make_pdf(path)
   self.assertTrue(path.read_bytes().startswith(b'%PDF-1.4'))
   factory=lambda _:types.SimpleNamespace(is_encrypted=False,pages=[types.SimpleNamespace(extract_text=lambda:' Amara   Python ')])
   result=ingest.extract_profile(path,factory)
   self.assertEqual(result['sections'][0]['text'],'Amara Python');self.assertFalse(result['sections'][0]['approved'])
 def test_encrypted_and_empty_pdf_rejected(self):
  path=ROOT/'projects/01-digital-twin/fixtures/synthetic-resume.pdf'
  with self.assertRaises(ValueError):ingest.extract_profile(path,lambda _:types.SimpleNamespace(is_encrypted=True))
  with self.assertRaises(ValueError):ingest.extract_profile(path,lambda _:types.SimpleNamespace(is_encrypted=False,pages=[]))
class ManagerTests(unittest.TestCase):
 def test_bounded_manager_sequence(self):
  state={};self.assertEqual(orch.manager_next(state)['next'],'research')
  state.update(research=True,strategy=True,draft=True,review={'passed':False,'issues':['unsupported fact']})
  self.assertEqual(orch.manager_next(state)['next'],'writer')
  state['review']['passed']=True;self.assertEqual(orch.manager_next(state)['next'],'human_approval')
 def test_handoff_requires_context(self):
  with self.assertRaises(ValueError):orch.Handoff('p','c','research','writer',())
  result=orch.Handoff('p','c','research','writer',('source-1',));self.assertEqual(result.campaign_id,'c')
 def test_rubric_exposes_checks(self):
  result=orch.score_draft({'body':'Hi A, CSV reports for Cedar.'},'A','Cedar','CSV reports')
  self.assertEqual(result['score'],1)
 def test_sdk_manager_and_handoff_are_real_configuration_paths(self):
  class Agent:
   def __init__(self,**kw):self.__dict__.update(kw)
   def as_tool(self,**kw):return kw
  fake=types.SimpleNamespace(Agent=Agent)
  with patch.dict(sys.modules,{'agents':fake,'pydantic':types.SimpleNamespace(BaseModel=object)}):
   adapter=load('agents_adapter','02-sales-team','agents_adapter')
   self.assertEqual(len(orch.build_sdk_manager('test').tools),4)
   self.assertEqual(len(orch.build_sdk_handoff('test').handoffs),4)
class SharedDataModelTests(unittest.TestCase):
 def test_records_preserve_campaign_and_evidence(self):
  models=load('sales_models','02-sales-team','models')
  result=models.EmailDraft('p1','campaign1','Demo','A fictional demo.',('source1',))
  self.assertEqual(result.evidence_ids,('source1',))
  with self.assertRaises(ValueError):models.ResearchFinding('p1','c1','Need',())
  with self.assertRaises(ValueError):models.Company('c1','Cedar','','source1')
if __name__=='__main__':unittest.main()
