"""Offline behavioural checks; never perform a provider request."""
import asyncio
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from research_lab.planning import make_plan, validate_plan, queries_for
from research_lab.search import FixtureSearch, LiveSearch, parallel_search, normalize
from research_lab.evidence import EvidenceStore, validate_findings
from research_lab.runtime import run, save_checkpoint, resume_checkpoint, bounded_retry
from research_lab.reporting import markdown, export_bundle, SimulatedOutbox, deliver_approved, delivery_digest
from research_lab.evaluation import evaluate
from research_lab.interface import progress

class ResearchStagesTests(unittest.TestCase):
    def setUp(self):
        self.records = json.loads((ROOT/'data/s09-workshop-sources.json').read_text())["records"]
    def bundle(self, records=None):
        return asyncio.run(run('Community workshop scheduling', FixtureSearch(self.records if records is None else records)))
    def test_empty_question(self):
        with self.assertRaises(ValueError): make_plan('  ')
    def test_dependency_cycle_rejected(self):
        p=make_plan('q'); p['tasks'][0]['dependencies']=['task-1']
        with self.assertRaises(ValueError): validate_plan(p)
    def test_queries_cover_each_task_and_counterevidence(self):
        p=make_plan('q'); q=queries_for(p)
        self.assertEqual({t['id'] for t in p['tasks']}, {r['task_id'] for r in q})
        self.assertEqual(3, sum(r['intent']=='counterevidence' for r in q))
    def test_invalid_source_url(self):
        with self.assertRaises(ValueError): normalize({**self.records[0],'url':'file:///etc/passwd'},'q','fixture')
    def test_explicit_live_consent_required(self):
        with self.assertRaises(ValueError): LiveSearch(None)
    def test_fake_live_transport_and_no_automatic_retry(self):
        calls=[]
        async def transport(text): calls.append(text); return self.records[:1]
        backend=LiveSearch(transport,enabled=True)
        rows=asyncio.run(backend.search({'id':'q','text':'accessibility'}))
        self.assertEqual(['accessibility'],calls); self.assertEqual('configured-live-provider',rows[0]['provider'])
    def test_parallel_bound_and_input_order(self):
        class Backend:
            active=0; peak=0
            async def search(self,q):
                self.active+=1; self.peak=max(self.peak,self.active)
                await asyncio.sleep(.001)
                self.active-=1; return []
        backend=Backend(); queries=queries_for(make_plan('q'))
        rows=asyncio.run(parallel_search(queries,backend,workers=2))
        self.assertEqual(2,backend.peak); self.assertEqual(queries,[r['query'] for r in rows])
    def test_exact_excerpt_and_deduplication(self):
        store=EvidenceStore(); source=self.records[0]
        a=store.append(source,source['text']); b=store.append(source,source['text'])
        self.assertEqual(a,b); self.assertEqual(1,len(store.records))
        with self.assertRaises(ValueError): store.append(source,'invented quote')
    def test_missing_dates_are_unknown(self):
        self.assertIsNone(self.bundle()['evidence'][0]['published'])
    def test_conflicts_retained_and_citations_checked(self):
        bundle=self.bundle(); self.assertEqual(['cost'],bundle['quality']['conflicts'])
        bundle['findings'][0]['alternatives'][0]['evidence_ids']=['fabricated']
        with self.assertRaises(ValueError): validate_findings(bundle['findings'],bundle['evidence'])
    def test_missing_evidence_is_not_success(self):
        self.assertEqual('insufficient_evidence',self.bundle([])['quality']['decision'])
    def test_export_roundtrip_and_manifest(self):
        import hashlib
        bundle=self.bundle()
        with tempfile.TemporaryDirectory() as tmp:
            manifest=export_bundle(bundle,tmp)
            self.assertEqual(bundle,json.loads((Path(tmp)/'research.json').read_text()))
            for name,sha in manifest.items(): self.assertEqual(sha,hashlib.sha256((Path(tmp)/name).read_bytes()).hexdigest())
    def test_delivery_exact_approval(self):
        outbox=SimulatedOutbox(); report=markdown(self.bundle()); recipient='student@example.invalid'
        with self.assertRaises(ValueError): deliver_approved(recipient,report,'wrong',outbox)
        approved=delivery_digest(recipient,report)
        self.assertEqual('simulated_only',deliver_approved(recipient,report,approved,outbox)['status'])
        with self.assertRaises(ValueError): deliver_approved(recipient,report+'changed',approved,outbox)
    def test_checkpoint_request_binding(self):
        bundle=self.bundle()
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'checkpoint.json'; save_checkpoint(bundle,path)
            self.assertEqual(bundle,resume_checkpoint('Community workshop scheduling',path))
            with self.assertRaises(ValueError): resume_checkpoint('other question',path)
    def test_unknown_paid_outcome_not_retried(self):
        calls=[]
        async def operation(): calls.append(1); raise TimeoutError('unknown response')
        with self.assertRaises(TimeoutError): asyncio.run(bounded_retry(operation))
        self.assertEqual(1,len(calls))
    def test_connection_refusal_bounded_retry(self):
        calls=[]
        async def operation():
            calls.append(1)
            if len(calls)==1: raise ConnectionRefusedError()
            return 'ok'
        self.assertEqual('ok',asyncio.run(bounded_retry(operation))); self.assertEqual(2,len(calls))
    def test_metrics_honest_unknown_tokens(self):
        metrics=evaluate(self.bundle()); self.assertEqual(1,metrics['citation_validity'])
        self.assertIsNone(metrics['tokens']); self.assertTrue(metrics['human_review_required'])
    def test_interface_events_only_from_executed_work(self):
        events=list(progress('Community workshop scheduling',self.records))
        self.assertEqual('Complete',events[-1][0]); self.assertIn('References',events[-1][1])
        self.assertEqual('completed',json.loads(events[-2][0])['phase'])


    def test_http_transport_contract_without_network(self):
        from research_lab.transports import JsonSearchTransport
        class Response:
            def __enter__(self): return self
            def __exit__(self,*args): pass
            def read(self,limit): return json.dumps({'records':[]}).encode()
        class Opener:
            calls=[]
            def open(self,request,timeout):
                self.calls.append(request); return Response()
        opener=Opener(); transport=JsonSearchTransport('https://search.example.invalid/api','fake-lab-token',enabled=True,opener=opener)
        self.assertEqual([],asyncio.run(transport('question')))
        self.assertEqual({'query':'question','limit':10},json.loads(opener.calls[0].data))
        with self.assertRaises(ValueError): JsonSearchTransport('http://search.example.invalid','fake',enabled=True)
    def test_real_smtp_adapter_with_fake_tls_client(self):
        from research_lab.transports import SmtpDelivery
        calls=[]
        class SMTP:
            def __init__(self,*args,**kwargs): calls.append(('connect',args,kwargs))
            def __enter__(self): return self
            def __exit__(self,*args): pass
            def login(self,*args): calls.append(('login',))
            def send_message(self,message): calls.append(('message',message)); return {}
        adapter=SmtpDelivery('smtp.example.invalid',465,'academy@example.invalid','fake-user','fake-password',enabled=True,factory=SMTP)
        result=deliver_approved('student@example.invalid','report',delivery_digest('student@example.invalid','report'),adapter)
        self.assertEqual('accepted_by_configured_mail_server',result['status'])
        self.assertIsNone(result['delivered_to_inbox'])
        self.assertEqual('student@example.invalid',calls[-1][1]['To'])

if __name__ == '__main__': unittest.main()
