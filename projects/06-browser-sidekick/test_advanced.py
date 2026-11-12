"""Offline contracts plus genuine loopback HTTP effects. No SDK/model claims."""
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile
import threading
import time
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from advanced import (Decision, Finding, Plan, PlannedStep, SessionController,
                      coordinate_research, evaluate, fixture_plan, parse_model_plan)
from sandbox_server import ApprovedSandboxExecutor, Sandbox, finding_from_response
from sidekick import Step


class PlannerTests(unittest.TestCase):
    def setUp(self): self.plan = fixture_plan('Compare Academy workshops', 'http://127.0.0.1:9999', True)
    def test_duplicate_ids_and_cycle_rejected(self):
        with self.assertRaises(ValueError): replace(self.plan, steps=(self.plan.steps[0], self.plan.steps[0])).validate()
        with self.assertRaises(ValueError): replace(self.plan, steps=(replace(self.plan.steps[0], dependencies=('draft',)), self.plan.steps[1])).validate()
    def test_external_targets_and_bad_tools_rejected(self):
        for target in ['https://example.com', '//example.com', '/%2e%2e/private', '/x?redirect=evil', '/../secret']:
            with self.assertRaises(ValueError): replace(self.plan, steps=(replace(self.plan.steps[0], target=target),)).validate()
        with self.assertRaises(ValueError): replace(self.plan, steps=(replace(self.plan.steps[0], action='shell'),)).validate()
    def test_invalid_predicate_and_sensitivity_rejected(self):
        with self.assertRaises(ValueError): replace(self.plan, steps=(replace(self.plan.steps[0], criterion='do well'),)).validate()
        with self.assertRaises(ValueError): replace(self.plan, steps=(self.plan.steps[0], replace(self.plan.steps[1], sensitive=False))).validate()
    def test_model_plan_strict_types_and_trusted_origin(self):
        row = {'id':'read','dependencies':[],'action':'extract','target':'/catalog','criterion':'contains:Academy','value':'','sensitive':False}
        result = parse_model_plan({'steps':[row]}, 'Read catalog', self.plan.origin)
        self.assertEqual('model-output-requires-run-receipt', result.evidence_kind)
        with self.assertRaises(ValueError): parse_model_plan({'steps':[dict(row, sensitive='false')]}, 'Read', self.plan.origin)
        with self.assertRaises(ValueError): parse_model_plan({'steps':[row], 'allowed_hosts':['evil']}, 'Read', self.plan.origin)
    def test_limits_and_submission_schema(self):
        with self.assertRaises(ValueError): replace(self.plan, step_limit=1).validate()
        with self.assertRaises(ValueError): replace(self.plan, replan_limit=6).validate()
        with self.assertRaises(ValueError): replace(self.plan, steps=(replace(self.plan.steps[1], dependencies=(), value='{"password":"no"}'),)).validate()


class EvaluatorTests(unittest.TestCase):
    def finding(self, value='40'):
        return Finding('price', value, 'http://127.0.0.1:9999/detail', time.time(), hashlib.sha256(b'actual response fixture').hexdigest())
    def evaluate(self, findings=(), **changes):
        values = dict(steps_used=1, step_limit=3, replans_used=0, replan_limit=1, steps_remaining=False)
        values.update(changes)
        return evaluate({'price':'40'}, findings, **values)
    def test_missing_evidence_never_complete(self):
        self.assertEqual(Decision.REVISE, self.evaluate().decision)
        self.assertEqual(Decision.STOP, self.evaluate(replans_used=1).decision)
        self.assertEqual(Decision.STOP, self.evaluate(steps_used=3).decision)
        self.assertEqual(Decision.CONTINUE, self.evaluate(steps_remaining=True).decision)
    def test_complete_requires_matching_attributed_facts(self):
        self.assertEqual(Decision.COMPLETE, self.evaluate((self.finding(),)).decision)
        self.assertNotEqual(Decision.COMPLETE, self.evaluate((self.finding('999'),)).decision)
        with self.assertRaises(ValueError): self.evaluate((replace(self.finding(), content_sha256=''),))


class SandboxTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.database = Path(self.tmp.name)/'tasks.sqlite'
        self.control = SessionController(self.database)
        self.token = self.control.session()
        self.sandbox = Sandbox().start()
        self.task = self.control.create(self.token, fixture_plan('Compare workshops', self.sandbox.origin, True))
    def tearDown(self):
        self.sandbox.close(); self.tmp.cleanup()
    def factory(self, store, task, origin):
        return ApprovedSandboxExecutor(store, task, origin, self.sandbox.secret)
    def advance(self): return self.control.advance(self.token, self.task, self.factory)
    def pending(self):
        self.assertEqual('step_complete', self.advance())
        self.assertEqual('awaiting_approval', self.advance())
        return self.control.snapshot(self.token, self.task)['steps'][1]
    def approve(self):
        row = self.pending()
        self.control.decide(self.token, self.task, 1, row['revision'], 'approve')
        return row
    def test_unapproved_has_zero_server_side_effects(self):
        self.pending()
        self.assertEqual([], self.sandbox.effects)
        self.assertEqual([], [r for r in self.sandbox.requests if r[0]=='POST'])
    def test_exact_approval_once_and_restart_progress(self):
        self.approve()
        self.assertEqual('step_complete', self.advance())
        self.control = SessionController(self.database)
        self.assertEqual('complete', self.advance())
        self.assertEqual(1, len(self.sandbox.effects))
        self.assertEqual(2, self.control.snapshot(self.token, self.task)['complete'])
    def test_edit_requires_fresh_approval_and_blocks_external_destination(self):
        row = self.pending()
        old = Step(**json.loads(row['payload']))
        with self.assertRaises(ValueError):
            self.control.decide(self.token, self.task, 1, row['revision'], 'edit', replace(old, target='http://example.com'))
        edited = replace(old, value=json.dumps({'workshop':'SQL','note':'Human-edited synthetic request'}))
        self.control.decide(self.token, self.task, 1, row['revision'], 'edit', edited)
        self.assertEqual('awaiting_approval', self.advance())
        self.assertEqual([], self.sandbox.effects)
        with self.assertRaises(ValueError): self.control.decide(self.token, self.task, 1, row['revision'], 'approve')
        self.control.decide(self.token, self.task, 1, edited.digest(), 'approve')
        self.assertEqual('step_complete', self.advance())
        self.assertEqual('SQL', self.sandbox.effects[0]['payload']['workshop'])
    def test_reject_and_foreign_session_have_no_effect(self):
        row = self.pending()
        stranger = self.control.session()
        with self.assertRaises(PermissionError): self.control.snapshot(stranger, self.task)
        with self.assertRaises(PermissionError): self.control.decide(stranger, self.task, 1, row['revision'], 'approve')
        with self.assertRaises(PermissionError): self.control.advance(stranger, self.task, self.factory)
        self.control.decide(self.token, self.task, 1, row['revision'], 'reject')
        self.assertEqual('rejected', self.advance())
        self.assertEqual([], self.sandbox.effects)
    def test_expired_approval_never_reaches_http(self):
        self.approve()
        with sqlite3.connect(self.database) as db: db.execute('UPDATE sidekick_approval SET expires=0')
        with self.assertRaises(PermissionError): self.advance()
        self.assertEqual([], self.sandbox.effects)
        self.assertEqual('failed', self.advance())
    def test_approved_payload_tamper_is_blocked(self):
        self.approve()
        altered = Step('submit','/submit',json.dumps({'workshop':'SQL','note':'Changed outside approval'}),'contains:accepted')
        with sqlite3.connect(self.database) as db:
            db.execute('UPDATE step SET payload=? WHERE task=? AND number=1', (json.dumps(altered.__dict__), self.task))
        self.assertEqual('awaiting_approval', self.advance())
        self.assertEqual([], self.sandbox.effects)
    def test_direct_executor_and_unauthorized_http_denied(self):
        with self.control._store() as store:
            executor = self.factory(store, self.task, self.sandbox.origin)
            with self.assertRaises(PermissionError): executor.execute(Step('submit','/submit','{"workshop":"Python","note":"Bypass"}','contains:accepted'))
        with self.assertRaises(HTTPError) as error:
            urlopen(Request(self.sandbox.origin+'/submit', data=b'{}'),timeout=2)
        self.assertEqual(403, error.exception.code)
        self.assertEqual([], self.sandbox.effects)
    def test_concurrent_approve_reject_serializes(self):
        row = self.pending()
        barrier = threading.Barrier(2)
        outcomes = []
        def decide(choice):
            barrier.wait()
            try:
                self.control.decide(self.token, self.task, 1, row['revision'], choice)
                outcomes.append(choice)
            except ValueError: outcomes.append('stale')
        threads = [threading.Thread(target=decide,args=(c,)) for c in ('approve','reject')]
        for thread in threads: thread.start()
        for thread in threads: thread.join()
        self.assertIn('stale', outcomes)
        self.advance()
        self.assertLessEqual(len(self.sandbox.effects),1)
    def test_crash_after_real_effect_not_automatically_replayed(self):
        self.approve()
        def crashing_factory(store, task, origin):
            executor = self.factory(store, task, origin)
            class Crash:
                def execute(self, step):
                    executor.execute(step)
                    raise SystemExit('injected crash after real effect before receipt')
            return Crash()
        with self.assertRaises(SystemExit): self.control.advance(self.token, self.task, crashing_factory)
        self.assertEqual(1,len(self.sandbox.effects))
        resumed = SessionController(self.database)
        self.assertEqual('executing', resumed.advance(self.token, self.task, self.factory))
        self.assertEqual(1,len(self.sandbox.effects))
    def test_step_budget_is_durable(self):
        plan = replace(fixture_plan('Read',self.sandbox.origin),step_limit=1)
        task = self.control.create(self.token,plan)
        self.control.advance(self.token,task,self.factory)
        with self.assertRaises(ValueError): SessionController(self.database).advance(self.token,task,self.factory)
    def test_replan_bound_and_history(self):
        plan = fixture_plan('Read revised catalog',self.sandbox.origin)
        self.control.revise(self.token,self.task,plan)
        self.control.revise(self.token,self.task,plan)
        with self.assertRaises(ValueError): self.control.revise(self.token,self.task,plan)
        self.assertEqual(2,sum(r['event']=='replan' for r in self.control.snapshot(self.token,self.task)['events']))
    def test_real_response_finding_provenance(self):
        with urlopen(self.sandbox.origin+'/detail',timeout=2) as response: body=response.read()
        finding=finding_from_response('price','40',self.sandbox.origin+'/detail',body)
        finding.validate()
        self.assertEqual(hashlib.sha256(body).hexdigest(),finding.content_sha256)
        self.assertIn(b'Price: $40',body)


class SpecialistTests(unittest.TestCase):
    def test_actual_concurrency_and_failure_isolation(self):
        barrier=threading.Barrier(2)
        identities=[]
        def success():
            identities.append(threading.get_ident());barrier.wait(timeout=1)
            return (Finding('price','40','http://127.0.0.1:1/detail',time.time(),'a'*64),)
        result=coordinate_research({'catalog':success,'audit':success},workers=2)
        self.assertEqual(2,len(set(identities)))
        self.assertEqual(['complete','complete'],[r.status for r in result])
        def fail(): raise OSError('synthetic network failure')
        result=coordinate_research({'catalog':lambda:(),'broken':fail})
        self.assertEqual('failed',result[0].status)
        self.assertEqual('OSError',result[0].error_type)
    def test_timeout_and_finite_worker_policy(self):
        result=coordinate_research({'slow':lambda:time.sleep(.05) or ()},timeout=.001)
        self.assertEqual('timeout',result[0].status)
        with self.assertRaises(ValueError): coordinate_research({'a':lambda:()},workers=50)


if __name__ == '__main__': unittest.main()
