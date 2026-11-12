import importlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

PROJECT = Path(__file__).resolve().parents[1]/'projects/08-mcp-trading-floor'
sys.path.insert(0, str(PROJECT))
from evaluation_lab.observability import Trace, usage_report
from evaluation_lab.quality import FeedbackStore, judge, digest
from evaluation_lab.recovery import retry_read, write_once, UnknownWriteOutcome
from evaluation_lab.dataset import evaluate, validate_dataset, decision_metrics

class EvaluationTests(unittest.TestCase):
    def test_parent_chain_failures_and_secret_fields(self):
        trace=Trace('run-one')
        with trace.span('workflow','workflow'):
            with trace.span('risk','tool',symbol='ACA',api_key='SECRET',prompt='PRIVATE'):
                pass
            with self.assertRaises(TimeoutError):
                with trace.span('provider','model'): raise TimeoutError('SECRET')
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'trace.jsonl'; trace.export(p); raw=p.read_text()
            self.assertNotIn('SECRET',raw); self.assertNotIn('PRIVATE',raw)
            rows=[json.loads(x) for x in raw.splitlines()]
        root=next(x for x in rows if x['parent_span_id'] is None)
        self.assertTrue(all(x['parent_span_id']==root['span_id'] for x in rows if x!=root))
        self.assertTrue(all(x['duration_seconds']>=0 for x in rows))
        self.assertEqual(sum(x['outcome']=='failed' for x in rows),1)

    def test_usage_cached_arithmetic_and_unknowns(self):
        price={'demo':{'as_of':'2026-01-01','input_per_million':'2','cached_per_million':'1','output_per_million':'4'}}
        call={'call_id':'a','model':'demo','input_tokens':1000,'cached_input_tokens':200,'output_tokens':100}
        self.assertEqual(usage_report([call],price)['total_cost'],'0.0022')
        unknown={**call,'call_id':'b','output_tokens':None}
        result=usage_report([call,unknown],price)
        self.assertIsNone(result['total_cost']); self.assertEqual(result['unknown_calls'],1)
        with self.assertRaises(ValueError): usage_report([call,call],price)
        with self.assertRaises(ValueError): usage_report([{**call,'cached_input_tokens':1001}],price)
        self.assertIsNone(usage_report([call],{})['total_cost'])

    def test_explicit_judge_valid_output_and_no_automatic_replay(self):
        output='Synthetic evidence supports a bounded paper proposal.'
        calls=[]
        def provider(**kw):
            calls.append(kw)
            return json.dumps({k:{'score':2,'evidence_quote':'Synthetic evidence'} for k in ('evidence','clarity')})
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'judge.json'
            result=judge(output,provider=provider,model='offline-test-double',run_id='run',artifact_path=p)
            self.assertEqual(result['status'],'scored'); self.assertFalse(result['can_override_risk'])
            with self.assertRaises(FileExistsError): judge(output,provider=provider,model='offline-test-double',run_id='run',artifact_path=p)
        self.assertEqual(len(calls),1)

    def test_invalid_judge_and_unknown_failure_do_not_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            for i,raw in enumerate(['{}','not json',json.dumps({k:{'score':True,'evidence_quote':'x'} for k in ('evidence','clarity')})]):
                result=judge('x',provider=lambda **kw:raw,model='test-double',run_id='r',artifact_path=Path(tmp)/str(i))
                self.assertEqual(result['status'],'evaluator_failure')
            def timeout(**kw): raise TimeoutError('private')
            result=judge('x',provider=timeout,model='test-double',run_id='r',artifact_path=Path(tmp)/'timeout')
            self.assertEqual(result['error_type'],'TimeoutError'); self.assertNotIn('private',json.dumps(result))

    def test_feedback_persists_idempotently_and_cannot_approve(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'feedback.sqlite'; store=FeedbackStore(path)
            args=dict(key='k',run_id='r',output_sha256=digest('output'),reviewer='Academy practice reviewer',rating=4,comment='<script>untrusted</script>')
            store.submit(**args); store.submit(**args)
            with self.assertRaises(ValueError): store.submit(**{**args,'rating':3})
            with self.assertRaises(ValueError): store.submit(**{**args,'rating':True})
            store.close(); reopened=FeedbackStore(path)
            self.assertEqual(len(reopened.list()),1)
            self.assertNotIn('approved',reopened.list()[0]); reopened.close()

    def test_retryable_reads_bounded_and_permanent_not_retried(self):
        calls=[]
        def read():
            calls.append(1)
            if len(calls)<3: raise ConnectionError()
            return 9
        sleeps=[]
        self.assertEqual(retry_read(read,sleep=sleeps.append),9)
        self.assertEqual(sleeps,[0.1,0.2])
        calls.clear()
        def invalid(): calls.append(1); raise ValueError()
        with self.assertRaises(ValueError): retry_read(invalid,sleep=sleeps.append)
        self.assertEqual(len(calls),1)

    def test_unknown_write_never_retried(self):
        calls=[]
        def write(): calls.append(1); raise TimeoutError()
        with self.assertRaises(UnknownWriteOutcome): write_once(write)
        self.assertEqual(len(calls),1)

    def test_complete_trace_reconciles_real_paper_ledger_and_rejection(self):
        from trading_floor import TradingFloor
        from evaluation_lab.workflow import run_paper_workflow
        floor=TradingFloor()
        try:
            pending=run_paper_workflow(floor,symbol='ACA',quantity=5,request_id='pending')
            self.assertEqual(pending['state'],'AWAITING_HUMAN_APPROVAL')
            self.assertEqual(pending['before'],pending['after'])
            result=run_paper_workflow(floor,symbol='ACA',quantity=5,request_id='test-order',reviewer='Academy unit-test reviewer')
            self.assertEqual(result['after']['cash'],'9373.75')
            self.assertEqual(result['after']['positions'],{'ACA':5})
            events=result['trace'].events
            self.assertEqual({x['kind'] for x in events},{'workflow','agent','tool','approval','order'})
            root=next(x for x in events if x['kind']=='workflow')
            self.assertTrue(all(x['parent_span_id']==root['span_id'] for x in events if x!=root))
            rejected=run_paper_workflow(floor,symbol='ACA',quantity=30,request_id='rejected',reviewer='Academy unit-test reviewer')
            self.assertEqual(rejected['state'],'RISK_REJECTED')
            self.assertEqual(rejected['before'],rejected['after'])
            self.assertNotIn('order',{x['kind'] for x in rejected['trace'].events})
        finally: floor.close()

    def test_dataset_reference_hashes_and_hand_computed_metrics(self):
        data,manifest=validate_dataset()
        self.assertEqual(manifest['cases'],4); self.assertEqual(len(manifest['market_sha256']),64)
        result=evaluate(); self.assertEqual(result['metrics']['correct'],4); self.assertEqual(result['model_calls'],0)
        metrics=decision_metrics([{'expected_allowed':True,'actual_allowed':True},{'expected_allowed':False,'actual_allowed':True},{'expected_allowed':True}])
        self.assertEqual(metrics,{'total':3,'observed':2,'unavailable':1,'correct':1,'accuracy_on_observed':0.5})
        self.assertIsNone(decision_metrics([])['accuracy_on_observed'])
        with tempfile.TemporaryDirectory() as tmp:
            bad=json.loads(json.dumps(data)); bad['cases'][1]['evidence_id']='invented'
            p=Path(tmp)/'bad.json'; p.write_text(json.dumps(bad))
            with self.assertRaises(ValueError): validate_dataset(p)

if __name__=='__main__': unittest.main()
