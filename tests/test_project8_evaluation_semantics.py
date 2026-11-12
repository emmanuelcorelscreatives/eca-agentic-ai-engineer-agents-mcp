"""Author-only acceptance source. Sole repository QA owner must execute/retain results."""
import asyncio
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

PROJECT=Path(__file__).resolve().parents[1]/'projects/08-mcp-trading-floor'
sys.path.insert(0,str(PROJECT))
from evaluation_lab.tracing import CorrelatedTrace, dispatch_model, dispatch_mcp
from evaluation_lab.feedback import BoundFeedbackStore
from evaluation_lab.checkpoints import Checkpoints
from evaluation_lab.research_metrics import evidence_quality, decision_consistency, explanation_clarity
from evaluation_lab.scenario_workflow import load_suite, run_case
from trading_floor import TradingFloor

class SemanticsTests(unittest.TestCase):
    def test_async_parentage_and_actual_injected_dispatch_hook(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'trace.jsonl'; trace=CorrelatedTrace(path,'r')
            async def child():
                async with trace.aspan('research','agent') as parent:
                    await asyncio.sleep(0)
                    async with trace.aspan('risk','tool') as leaf:
                        await asyncio.sleep(0)
                        return parent['span_id'],leaf['parent_span_id']
            async def run():
                async with trace.aspan('workflow','workflow'):
                    return await asyncio.gather(child(),child())
            pairs=asyncio.run(run())
            self.assertTrue(all(a==b for a,b in pairs)); self.assertNotEqual(pairs[0][0],pairs[1][0])
            calls=[]
            def invoke(**kw):
                calls.append(kw)
                return {'usage':{'prompt_tokens':7,'completion_tokens':2,'prompt_tokens_details':{'cached_tokens':1}},'text':'test double'}
            response=dispatch_model(trace,invoke,model='explicit-test-double',payload={'secret':'do not export'})
            trace.close(); rows=[json.loads(line) for line in path.read_text().splitlines()]
            self.assertEqual(len(calls),1); self.assertEqual(response['usage']['completion_tokens'],2)
            event=next(r for r in rows if r['name']=='model_dispatch' and r['phase']=='finished')
            self.assertEqual(event['cached_input_tokens'],1); self.assertNotIn('do not export',path.read_text())

    def test_mcp_hook_invokes_client_and_classifies_tool_error(self):
        class Response:
            isError=False
            def model_dump(self,mode): return {'content':[{'type':'text','text':'local test double'}]}
        class Session:
            calls=[]
            async def call_tool(self,name,arguments): self.calls.append((name,arguments)); return Response()
        with tempfile.TemporaryDirectory() as tmp:
            trace=CorrelatedTrace(Path(tmp)/'mcp.jsonl'); session=Session()
            result=asyncio.run(dispatch_mcp(trace,session,tool_name='research_market',arguments={'symbol':'ACA'}))
            trace.close(); self.assertEqual(session.calls,[('research_market',{'symbol':'ACA'})]); self.assertFalse(result.isError)

    def test_versioned_suite_enforces_research_and_retains_failed_traces(self):
        data,manifest=load_suite(); self.assertEqual(manifest['case_count'],8)
        for case in data['cases']:
            floor=TradingFloor()
            try:
                result=run_case(floor,case)
                self.assertTrue(result['passed'],case['id']); self.assertTrue(result['ledger_unchanged'])
                if case['fault'] in {'timeout','agent-error'}:
                    self.assertTrue(any(e['outcome']=='failed' for e in result['trace'].events))
            finally: floor.close()

    def test_hand_computed_research_consistency_and_clarity(self):
        evidence=[{'id':'a','facts':{'revenue_growth':8}},{'id':'b','facts':{'revenue_growth':9}}]
        claims=[{'fact':'revenue_growth','value':8,'evidence_ids':['a']},
                {'fact':'revenue_growth','value':8,'evidence_ids':['a','b']},
                {'fact':'revenue_growth','value':8,'evidence_ids':[]}]
        result=evidence_quality(claims,evidence)
        self.assertEqual(result['supported_claims'],1); self.assertEqual(result['conflicting_claims'],1)
        self.assertEqual(result['support_fraction'],1/3)
        runs=[{'scenario_id':'s','input_sha256':'x','decision':d} for d in ('BUY','BUY','HOLD',None)]
        result=decision_consistency(runs)
        self.assertEqual(result['comparable_pairs'],3); self.assertEqual(result['agreeing_pairs'],1); self.assertEqual(result['unavailable_pairs'],3)
        self.assertIsNone(decision_consistency([])['agreement'])
        self.assertTrue(explanation_clarity('Evidence: synthetic data. Limitations: stale sample.')['has_limitations_section'])

    def test_feedback_registry_auth_correction_and_persistence(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'feedback.sqlite'; store=BoundFeedbackStore(path)
            sha=store.register_output('run-1','actual registered test output')
            self.assertEqual(sha,store.register_output('run-1','actual registered test output'))
            with self.assertRaises(ValueError): store.register_output('run-1','changed')
            args=dict(submission_id='submission',run_id='run-1',output_sha256=sha,reviewer='practice',token='review-token',reviewer_tokens={'practice':'review-token'},rating=3,comment='<script>untrusted</script>',correction='Use exact evidence date')
            with self.assertRaises(PermissionError): store.submit(**{**args,'token':'operator-token'})
            with self.assertRaises(ValueError): store.submit(**{**args,'run_id':'missing'})
            result=store.submit(**args); store.submit(**args)
            self.assertFalse(result['execution_approval'])
            with self.assertRaises(ValueError): store.submit(**{**args,'correction':'changed'})
            store.close(); reopened=BoundFeedbackStore(path)
            self.assertEqual(reopened.report()['count'],1); self.assertEqual(reopened.report()['corrections'],1); reopened.close()

    def test_checkpoint_unknown_write_is_not_replayed(self):
        with tempfile.TemporaryDirectory() as tmp:
            cp=Checkpoints(Path(tmp)/'checkpoint.sqlite'); floor=TradingFloor()
            try:
                proposal=floor.propose('ACA',5)
                cp.prepare('r','request',proposal.digest()); cp.mark_dispatch('r')
                self.assertEqual(cp.reconcile('r',floor),{'state':'UNRESOLVED','dispatch_allowed':False})
                with self.assertRaises(ValueError): cp.mark_dispatch('r')
            finally: cp.close(); floor.close()

    def test_real_child_process_exit_and_read_only_reconciliation(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger=str(Path(tmp)/'paper.sqlite'); checkpoint=str(Path(tmp)/'checkpoint.sqlite')
            base=[sys.executable,'-m','evaluation_lab.checkpoint_demo']
            args=['--ledger',ledger,'--checkpoint',checkpoint]
            env={**os.environ,'PYTHONPATH':str(PROJECT)}
            first=subprocess.run([*base,'prepare-and-crash',*args],env=env,capture_output=True,text=True,timeout=20)
            self.assertEqual(first.returncode,73,first.stderr)
            for _ in range(2):
                second=subprocess.run([*base,'reconcile',*args],env=env,capture_output=True,text=True,timeout=20,check=True)
                result=json.loads(second.stdout)
                self.assertEqual(result['checkpoint']['state'],'COMMITTED'); self.assertFalse(result['checkpoint']['dispatch_allowed'])
                self.assertEqual(result['portfolio']['cash'],'9373.75'); self.assertEqual(result['portfolio']['positions']['ACA'],5)
            floor=TradingFloor(ledger)
            try: self.assertEqual(floor.db.execute('SELECT COUNT(*) FROM orders').fetchone()[0],1)
            finally: floor.close()

if __name__=='__main__': unittest.main()
