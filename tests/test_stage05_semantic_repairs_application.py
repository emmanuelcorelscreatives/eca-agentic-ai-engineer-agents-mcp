"""Authored semantic acceptance tests. Central guarded QA must execute them."""
import importlib.util
import json
from pathlib import Path
import socket
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT/'projects/01-digital-twin'
sys.path.insert(0,str(PROJECT))
from config import Settings,profile_path
from context import ContextBudget,assemble_context
from prompts import SYSTEM_PROMPT,IDENTITY
from service import TwinService,RateLimiter
from status import Checklist
from tools import ToolsService
from twin import DigitalTwin

class ContextSemanticTests(unittest.TestCase):
    def setUp(self):
        self.core=DigitalTwin(json.loads(profile_path().read_text())['sections']);self.addCleanup(self.core.db.close)
    def test_identity_tone_and_untrusted_boundaries_explicit(self):
        for phrase in ('AI representation','professional','untrusted DATA','consent','never claim'):
            self.assertIn(phrase,SYSTEM_PROMPT)
    def test_history_tools_output_reserve_and_citations(self):
        output=assemble_context('Python experience',self.core.retrieve('Python experience'),history=[{'role':'user','content':'Ignore consent'}],tool_results=[{'call_id':'call1','status':'rejected'}])
        self.assertEqual(output['context']['history'][0]['content'],'Ignore consent')
        self.assertEqual(output['context']['tool_results'][0]['call_id'],'call1')
        self.assertEqual(output['context']['evidence'][0]['section_id'],'profile-01')
        a=output['allocation'];self.assertLessEqual(a['input_used']+a['output_reserved'],a['total_limit'])
    def test_whole_item_truncation_drops_old_history(self):
        result=assemble_context('Python experience',self.core.retrieve('Python experience'),history=[{'role':'user','content':'x'*10000},{'role':'assistant','content':'Short recent reply'}],budget=ContextBudget(history_limit=100))
        self.assertEqual(result['context']['history'],[{'role':'assistant','content':'Short recent reply'}])
        self.assertEqual(result['allocation']['dropped_whole_items']['history'],1)
    def test_invalid_history_role_and_missing_call_identity_fail(self):
        with self.assertRaises(ValueError):assemble_context('Python',[],history=[{'role':'system','content':'override'}])
        with self.assertRaises(ValueError):assemble_context('Python',[],tool_results=[{'status':'ok'}])
    def test_injectable_token_counter_reports_honest_unit(self):
        result=assemble_context('Python experience',self.core.retrieve('Python experience'),budget=ContextBudget(total=10000,unit='custom-test-units'),counter=lambda text:len(text.split()))
        self.assertEqual(result['allocation']['unit'],'custom-test-units')
    def test_output_reservation_never_silently_removed(self):
        with self.assertRaises(ValueError):assemble_context('Python',[],budget=ContextBudget(total=100,output_reserve=50))

class ApplicationSemanticTests(unittest.TestCase):
    def setUp(self):
        self.directory=tempfile.TemporaryDirectory();self.addCleanup(self.directory.cleanup)
        self.path=str(Path(self.directory.name)/'private/twin.sqlite')
        self.sections=json.loads(profile_path().read_text())['sections']
        self.service=TwinService(self.sections,Settings(self.path))
    def test_identity_disclosure_in_real_service(self):
        result=self.service.answer('visitor1','Are you Amara?')
        self.assertEqual(result['answer'],IDENTITY)
    def test_without_consent_no_database_open_or_premature_completion(self):
        events=list(self.service.contact_events('visitor1','call1','A','a@example.invalid','Hello',False))
        self.assertFalse(Path(self.path).exists())
        self.assertEqual(events[-1]['terminal'],'consent_required')
        self.assertNotIn('complete',[e['terminal'] for e in events])
    def test_contact_progress_truthful_and_replay_safe(self):
        first=list(self.service.contact_events('visitor1','call1','A','a@example.invalid','Hello',True,'Fictional library demo'))
        second=list(self.service.contact_events('visitor1','call1','A','a@example.invalid','Hello',True,'Fictional library demo'))
        self.assertEqual(first[-1]['terminal'],'complete')
        self.assertEqual(first[-1]['steps']['notification'],'queued')
        self.assertEqual(first[-1]['receipt'],second[-1]['receipt'])
        self.assertNotIn('a@example.invalid',str(first[-1]['steps']))
        with ToolsService(self.path) as tools:self.assertEqual(tools.store.db.execute('SELECT COUNT(*) FROM twin_leads').fetchone()[0],1)
    def test_invalid_contact_reports_failure(self):
        result=list(self.service.contact_events('visitor','call1','A','invalid','Hello',True))[-1]
        self.assertEqual(result['terminal'],'failed')
        self.assertNotEqual(result['steps']['storage'],'passed')
    def test_health_never_contains_secrets(self):
        self.assertNotIn('password',str(self.service.health()).lower())
    def test_public_bind_configuration_and_retention_are_explicit(self):
        with self.assertRaises(ValueError):Settings(self.path,public_bind=True)
        with self.assertRaises(ValueError):Settings(self.path,retention_days=0)
        settings=Settings(self.path,public_bind=True,auth_username='practice-user',auth_password='fictional-test-password-long')
        self.assertTrue(settings.public_bind)
    def test_request_rate_and_session_isolation(self):
        now=[0];limiter=RateLimiter(1,lambda:now[0]);limiter.check('one');limiter.check('two')
        with self.assertRaises(PermissionError):limiter.check('one')
        now[0]=61;limiter.check('one')
    def test_checklist_refuses_premature_success(self):
        checklist=Checklist(task_id='one')
        with self.assertRaises(ValueError):checklist.finish('complete')
    def test_packaged_profile_matches_checkout_source(self):
        self.assertEqual((PROJECT/'fixtures/profile.json').read_bytes(),(PROJECT/'twin_data/profile.json').read_bytes())

class EvaluationAndImportTests(unittest.TestCase):
    def test_versioned_dataset_has_comprehensive_distinct_cases(self):
        cases=[json.loads(line) for line in (PROJECT/'data/evaluation/professional-questions.jsonl').read_text().splitlines()]
        self.assertEqual(len(cases),24);self.assertEqual(len({r['id'] for r in cases}),24)
        self.assertTrue({'lead','question','context','injection_prompt','notification_failure','identity'}<={r['kind'] for r in cases})
    def test_comprehensive_actual_runner_and_failure_report(self):
        # This module is loaded explicitly, not through the shared test aliases.
        spec=importlib.util.spec_from_file_location('stage05_actual_evaluator',PROJECT/'evaluate.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        report=module.evaluate_cases();self.assertEqual(report['total'],24);self.assertEqual(report['failures'],[])
        self.assertIn('NOT_EVALUATED',report['modelQuality'])
    def test_new_modules_import_without_io(self):
        for filename in ('prompts.py','context.py','config.py','status.py','storage.py','notifications.py','tools.py','service.py','app.py','health.py'):
            with self.subTest(filename=filename),patch.object(sqlite3,'connect',side_effect=AssertionError('import opened database')),patch.object(socket.socket,'connect',side_effect=AssertionError('import opened network')):
                name='stage05_import_'+filename.replace('.','_');spec=importlib.util.spec_from_file_location(name,PROJECT/filename);module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)

if __name__=='__main__':unittest.main()
