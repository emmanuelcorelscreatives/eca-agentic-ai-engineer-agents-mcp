"""Authored semantic regression tests. Central QA owns execution and results.

Adapter-double tests establish contracts only. ECA_RUN_S20_BROWSER=1 enables
actual installed Playwright sandbox integration; no test makes paid model calls.
"""
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import sys
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from advanced import Plan, PlannedStep, SessionController, fixture_plan
from pipeline import NativePlanner, SidekickApplication, Workspace
from sandbox_server import Sandbox
from sidekick import Step

# Only the native adapter contract needs these optional SDK imports. Keep the
# persisted lifecycle, workspace, policy and replay tests available in bare Python.
# A missing optional dependency is an explicit skip, never a semantic PASS.
try:
    from langchain_core.callbacks import BaseCallbackHandler as _NativeCallback
    from langgraph.checkpoint.memory import InMemorySaver as _NativeCheckpointer
except ModuleNotFoundError as _sdk_missing:
    _NATIVE_SDK_AVAILABLE = False
    _NATIVE_SDK_SKIP = ('Optional native SDK dependency unavailable: '
                        + str(_sdk_missing) + '; skipped, not semantic verification')
else:
    _NATIVE_SDK_AVAILABLE = True
    _NATIVE_SDK_SKIP = ''


def native_messages(steps,both=True):
    # Explicit SDK message-shape double; never evidence of actual specialist work.
    rows=[SimpleNamespace(tool_calls=[{'name':'task','id':'one','args':{'subagent_type':'catalog-researcher'}},
                                     {'name':'task','id':'two','args':{'subagent_type':'evidence-auditor'}}],content='')]
    rows.append(SimpleNamespace(tool_call_id='one',status='success',content='catalog result fixture'))
    if both:rows.append(SimpleNamespace(tool_call_id='two',status='success',content='audit result fixture'))
    rows.append(SimpleNamespace(tool_calls=[],content=json.dumps({'steps':steps})))
    return rows


def row_dict():
    return {'id':'catalog','dependencies':[],'action':'extract','target':'/catalog',
            'criterion':'contains:Academy','value':'','sensitive':False}


@unittest.skipUnless(_NATIVE_SDK_AVAILABLE, _NATIVE_SDK_SKIP)
class NativeAdapterContract(unittest.TestCase):
    def test_objective_invocation_strict_result_and_native_receipt(self):
        class AgentDouble:
            def invoke(self,payload,config):
                self.payload,self.config=payload,config
                return {'messages':native_messages([row_dict()])}
        fake=AgentDouble()
        with patch('pipeline.build_deep_agent',return_value=fake):
            plan,receipt=NativePlanner(object()).plan('Find the Academy catalog','http://127.0.0.1:9999')
        self.assertIn('Find the Academy catalog',fake.payload['messages'][0]['content'])
        self.assertEqual(24,fake.config['recursion_limit'])
        self.assertEqual(['catalog-researcher','evidence-auditor'],receipt['native_specialists'])
        self.assertEqual('/catalog',plan.steps[0].target)
        self.assertEqual([],receipt['actual_model_starts']) # test double, not a provider call
    def test_unobserved_specialist_cannot_be_claimed(self):
        agent=SimpleNamespace(invoke=lambda *a,**k:{'messages':native_messages([row_dict()],both=False)})
        with patch('pipeline.build_deep_agent',return_value=agent):
            with self.assertRaises(ValueError):NativePlanner(object()).plan('Read catalog','http://127.0.0.1:9999')
    def test_external_plan_and_changed_missing_predicate_rejected(self):
        bad={**row_dict(),'target':'https://example.com'}
        agent=SimpleNamespace(invoke=lambda *a,**k:{'messages':native_messages([bad])})
        with patch('pipeline.build_deep_agent',return_value=agent):
            with self.assertRaises(ValueError):NativePlanner(object()).plan('Read','http://127.0.0.1:9999')
        agent=SimpleNamespace(invoke=lambda *a,**k:{'messages':native_messages([row_dict()])})
        with patch('pipeline.build_deep_agent',return_value=agent):
            with self.assertRaises(ValueError):NativePlanner(object()).plan('Read','http://127.0.0.1:9999',missing={'catalog':'Different original predicate'})


class IntegratedContract(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.sandbox=SimpleNamespace(origin='http://127.0.0.1:9999',secret='synthetic-test-token')
        self.app=SidekickApplication(self.root/'tasks.sqlite',self.root/'workspaces',self.sandbox)
        self.token=SessionController.session()
    def tearDown(self):self.tmp.cleanup()
    def test_planning_intent_prevents_unknown_native_replay(self):
        class FailingPlanner:
            mode='explicit-failing-test-double'
            def __init__(self):self.calls=0
            def plan(self,*args,**kwargs):self.calls+=1;raise TimeoutError('unknown provider outcome fixture')
        planner=FailingPlanner();self.app.planner=planner
        with self.assertRaises(TimeoutError):self.app.create(self.token,'Read catalog')
        with self.assertRaises(ValueError):self.app.create(self.token,'Read catalog')
        self.assertEqual(1,planner.calls)
        with sqlite3.connect(self.root/'tasks.sqlite') as db:
            self.assertEqual('UNKNOWN',db.execute('SELECT state FROM sidekick_planning').fetchone()[0])
    def test_completed_planning_intent_returns_same_task(self):
        one=self.app.create(self.token,'Read catalog')
        two=self.app.create(self.token,'Read catalog')
        self.assertEqual(one,two)
    def test_evaluator_not_generated_prose_controls_completion(self):
        task=self.app.create_from_plan(self.token,fixture_plan('Read',self.sandbox.origin),{'kind':'deterministic-test'})
        with sqlite3.connect(self.root/'tasks.sqlite') as db:
            db.execute("UPDATE step SET state='complete',result='The model says success' WHERE task=?",(task,))
        result=self.app.evaluate(self.token,task)
        self.assertEqual('REVISE',result['decision'])
        self.assertEqual('REVISION_AVAILABLE',self.app.snapshot(self.token,task)['status'])
    def test_attributable_actual_observation_is_required(self):
        task=self.app.create_from_plan(self.token,fixture_plan('Read',self.sandbox.origin),{'kind':'deterministic-test'})
        body=b'Academy synthetic response fixture'
        self.app._record(task,{'number':0,'step_sha256':fixture_plan('Read',self.sandbox.origin).steps[0].as_step().digest(),
                             'url':self.sandbox.origin+'/catalog','body_sha256':hashlib.sha256(body).hexdigest(),
                             'body_text':body.decode(),'captured_at':time.time(),'criterion_met':True})
        with sqlite3.connect(self.root/'tasks.sqlite') as db:db.execute("UPDATE step SET state='complete' WHERE task=?",(task,))
        self.assertEqual('COMPLETE',self.app.evaluate(self.token,task)['decision'])
        self.assertEqual(1,self.app.snapshot(self.token,task)['metrics']['attributed_predicates'])
    def test_unknown_execution_cannot_be_replayed_or_completed(self):
        task=self.app.create_from_plan(self.token,fixture_plan('Read',self.sandbox.origin),{'kind':'deterministic-test'})
        with sqlite3.connect(self.root/'tasks.sqlite') as db:db.execute("UPDATE step SET state='executing' WHERE task=?",(task,))
        self.assertEqual('STOP',self.app.evaluate(self.token,task)['decision'])
        self.assertEqual('UNKNOWN',self.app.snapshot(self.token,task)['status'])
        with self.assertRaises(ValueError):self.app.advance(self.token,task)
    def test_foreign_session_and_unrecorded_file_forbidden(self):
        task=self.app.create(self.token,'Read')
        with self.assertRaises(PermissionError):self.app.snapshot(SessionController.session(),task)
        with self.assertRaises(PermissionError):self.app.owned_file(self.token,task,'invented.md','a'*64)
    def test_approved_artifact_plan_and_workspace_escape(self):
        plan=Plan('Save approved evidence',self.sandbox.origin,(PlannedStep('report',(),'save','report.md','contains:Academy','Academy observed evidence',True),)).validate()
        task=self.app.create_from_plan(self.token,plan,{'kind':'deterministic-test'})
        self.assertEqual('save',json.loads(self.app.snapshot(self.token,task)['steps'][0]['payload'])['action'])
        workspace=Workspace(self.root/'workspaces',task)
        with self.assertRaises(ValueError):workspace.save('../escape.md',b'no')
        workspace.save('report.md',b'Academy')
        with self.assertRaises(FileExistsError):workspace.save('report.md',b'overwrite denied')
    def test_human_edit_atomically_updates_expected_predicate(self):
        task=self.app.create_from_plan(self.token,fixture_plan('Read',self.sandbox.origin),{'kind':'deterministic-test'})
        current=self.app.snapshot(self.token,task)['steps'][0]
        self.app.decide(self.token,task,0,current['revision'],'edit',Step('extract','/detail','','contains:Python'))
        with sqlite3.connect(self.root/'tasks.sqlite') as db:
            expected=json.loads(db.execute('SELECT expected FROM sidekick_run WHERE task=?',(task,)).fetchone()[0])
            criterion=db.execute('SELECT criterion FROM sidekick_binding WHERE task=?',(task,)).fetchone()[0]
        self.assertEqual('Python',expected['catalog']);self.assertEqual('contains:Python',criterion)
    def test_trace_redacts_injected_secret(self):
        task=self.app.create(self.token,'Read catalog with SYNTHETIC_SECRET_123')
        trace=self.app.export_trace(self.token,task,redactions=('SYNTHETIC_SECRET_123',))
        self.assertNotIn('SYNTHETIC_SECRET_123',json.dumps(trace))


@unittest.skipUnless(os.environ.get('ECA_RUN_S20_BROWSER')=='1','Central QA must explicitly enable genuine browser integration')
class RealBrowserIntegration(unittest.TestCase):
    def test_full_read_approved_browser_submit_and_artifact(self):
        with tempfile.TemporaryDirectory() as tmp,Sandbox() as sandbox:
            root=Path(tmp);app=SidekickApplication(root/'tasks.sqlite',root/'files',sandbox,
                executable_path=os.environ.get('ECA_CHROMIUM_EXECUTABLE'))
            token=SessionController.session()
            steps=(PlannedStep('catalog',(),'extract','/catalog','contains:Academy'),
                   PlannedStep('submit',('catalog',),'submit','/submit','contains:accepted',json.dumps({'workshop':'Python','note':'Synthetic browser exercise'}),True),
                   PlannedStep('report',('submit',),'save','report.md','contains:Academy','Academy Python workshop request; see retained source observations.',True))
            task=app.create_from_plan(token,Plan('Research and submit synthetic Academy request, preserving report',sandbox.origin,steps),{'kind':'explicit-integration-test-plan'})
            self.assertEqual('RUNNING',app.advance(token,task)['status'])
            self.assertEqual('WAITING_APPROVAL',app.advance(token,task)['status'])
            self.assertEqual([],sandbox.effects)
            current=app.snapshot(token,task)['steps'][1]
            app.decide(token,task,1,current['revision'],'approve')
            app.advance(token,task)
            self.assertEqual(1,len(sandbox.effects))
            self.assertEqual('WAITING_APPROVAL',app.advance(token,task)['status'])
            current=app.snapshot(token,task)['steps'][2]
            app.decide(token,task,2,current['revision'],'approve')
            final=app.advance(token,task)
            self.assertEqual('COMPLETED',final['status'])
            self.assertEqual('COMPLETE',final['evaluation']['decision'])
            self.assertEqual(2,len([r for r in final['observations'] if r.get('screenshot')]))
            artifact=next(r for r in final['observations'] if r.get('artifact'))
            self.assertIn('Academy',app.owned_file(token,task,artifact['artifact'],artifact['body_sha256']).read_text())
            reopened=SidekickApplication(root/'tasks.sqlite',root/'files',sandbox)
            self.assertEqual('COMPLETED',reopened.snapshot(token,task)['status'])
            with self.assertRaises(ValueError):reopened.advance(token,task)
            self.assertEqual(1,len(sandbox.effects))


if __name__=='__main__':unittest.main()
