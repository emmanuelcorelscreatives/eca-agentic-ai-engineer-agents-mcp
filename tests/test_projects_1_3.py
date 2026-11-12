"""Offline acceptance tests for course projects 1–3; no paid providers."""
import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
def load(name, project, module):
    path = ROOT / 'projects' / project / (module + '.py')
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result

twin = load('academy_twin', '01-digital-twin', 'twin')
sales = load('academy_sales', '02-sales-team', 'sales')
research = load('academy_research', '03-deep-research', 'research')

def fixture(project, name):
    return json.loads((ROOT/'projects'/project/'fixtures'/name).read_text())

class TwinTests(unittest.TestCase):
    def setUp(self):
        self.app = twin.DigitalTwin(fixture('01-digital-twin','profile.json')['sections'])
        self.addCleanup(self.app.db.close)
    def test_supported_answer_cites(self):
        answer = self.app.answer('Python experience')
        self.assertIn('profile-01',answer['citations'])
        self.assertIn('SQLite',answer['answer'])
    def test_unapproved_never_returned(self):
        answer = self.app.answer('Salary and personal contact details')
        self.assertEqual(answer['status'],'insufficient_evidence')
        self.assertEqual(answer['citations'],[])
    def test_string_approval_is_not_trusted(self):
        with self.assertRaises(ValueError): twin.DigitalTwin([{'id':'x','title':'A','text':'Secret','approved':'false'}])
    def test_unknown_question_no_invention(self):
        self.assertEqual(self.app.answer('national astronaut award')['status'],'insufficient_evidence')
    def test_contact_requires_explicit_consent(self):
        with self.assertRaises(PermissionError): self.app.record_contact('A','a@example.invalid','Hello')
        with self.assertRaises(PermissionError): self.app.record_contact('A','a@example.invalid','Hello',1)
        self.assertEqual(self.app.db.execute('SELECT COUNT(*) FROM contacts').fetchone()[0],0)
    def test_contact_validation_and_deletion(self):
        with self.assertRaises(ValueError): self.app.record_contact('A','bad','Hello',True)
        result=self.app.record_contact('A','a@example.invalid','Hello',True)
        self.assertEqual(result['notification'],'not_sent')
        self.assertTrue(self.app.delete_contact(result['contact_id']))
        self.assertFalse(self.app.delete_contact(result['contact_id']))
    def test_tools_are_explicit_and_ordered(self):
        results=self.app.run_tools([{'name':'shell','arguments':{}},{'name':'retrieve','arguments':{'question':'Python'}}])
        self.assertEqual([r['status'] for r in results],['rejected','ok'])

class SalesTests(unittest.TestCase):
    def setUp(self):
        self.team=sales.SalesTeam()
        self.addCleanup(self.team.db.close)
        self.prospect=sales.Prospect(**fixture('02-sales-team','prospect.json')['prospect'])
        self.ident=self.team.create_draft(self.prospect)
    def test_draft_carries_provenance(self):
        self.assertEqual(self.team.draft(self.ident)['source_id'],self.prospect.source_id)
    def test_unapproved_is_blocked(self):
        with self.assertRaises(PermissionError): self.team.deliver(self.ident)
    def test_approved_simulated_once(self):
        self.team.approve(self.ident,'Human reviewer')
        self.assertEqual(self.team.deliver(self.ident)['external_messages_sent'],0)
        with self.assertRaises(PermissionError): self.team.deliver(self.ident)
        self.assertEqual(self.team.db.execute('SELECT COUNT(*) FROM outbox').fetchone()[0],1)
    def test_edit_revokes_approval(self):
        self.team.approve(self.ident,'Human reviewer')
        self.team.edit(self.ident,'New subject','A revised practice message')
        self.assertIsNone(self.team.draft(self.ident)['approved_hash'])
        with self.assertRaises(PermissionError): self.team.deliver(self.ident)
    def test_hash_blocks_direct_payload_tamper(self):
        self.team.approve(self.ident,'Human reviewer')
        with self.team.db: self.team.db.execute("UPDATE drafts SET body='tampered' WHERE id=?",(self.ident,))
        with self.assertRaises(PermissionError): self.team.deliver(self.ident)
    def test_live_is_always_blocked(self):
        self.team.approve(self.ident,'Human reviewer')
        with self.assertRaises(PermissionError): self.team.deliver(self.ident,live=True)
    def test_review_blocks_selected_unsupported_claim(self):
        self.team.edit(self.ident,'Offer','Guaranteed 100% ROI')
        self.assertFalse(self.team.review(self.ident)['passed'])
        with self.assertRaises(ValueError): self.team.approve(self.ident,'Human reviewer')

class ResearchTests(unittest.TestCase):
    def setUp(self):
        self.corpus=[research.Evidence(**e) for e in fixture('03-deep-research','evidence.json')['evidence']]
    def test_conflict_preserves_citations(self):
        report=research.investigate('Cedar Library reporting time',self.corpus)
        self.assertEqual(report['status'],'conflicts_present')
        conflict=next(f for f in report['findings'] if f['status']=='conflicting')
        self.assertEqual({v['value'] for v in conflict['alternatives']},{'45 minutes','70 minutes'})
        self.assertTrue(all(v['citations'] for v in conflict['alternatives']))
    def test_excerpts_exist_verbatim_in_sources(self):
        for evidence in self.corpus:
            source=(ROOT/'projects/03-deep-research'/evidence.location).read_text()
            self.assertIn(evidence.excerpt,source)
            self.assertIn('SYNTHETIC',source)
    def test_no_evidence_no_conclusions(self):
        report=research.investigate('galactic asteroid mineral royalties',self.corpus)
        self.assertEqual(report['status'],'insufficient_evidence')
        self.assertEqual(report['findings'],[])
    def test_parallel_result_is_deterministic(self):
        self.assertEqual(research.investigate('Cedar Library reporting',self.corpus,1),research.investigate('Cedar Library reporting',self.corpus,3))
    def test_duplicate_sources_rejected(self):
        with self.assertRaises(ValueError): research.investigate('Cedar',self.corpus+[self.corpus[0]])
    def test_markdown_has_actual_local_sources(self):
        output=research.markdown(research.investigate('Cedar Library reporting',self.corpus))
        self.assertIn('fixtures/pilot-memo.txt',output)
        self.assertIn('synthetic local corpus',output)


class OptionalAdapterTests(unittest.TestCase):
    def setUp(self):
        import types
        from unittest.mock import patch
        self.types=types
        self.patch=patch
        self.calls=[]
        class Agent:
            def __init__(inner, **kwargs): inner.__dict__.update(kwargs)
        self.Agent=Agent
        class Schema:
            def __init__(inner, **kwargs): inner.__dict__.update(kwargs)
            def model_dump(inner): return inner.__dict__
            def model_dump_json(inner): return json.dumps(inner.__dict__)
        self.Schema=Schema
        sys.modules['sales']=sales
        sys.modules['research']=research
    def fake_modules(self, run):
        return {'agents':self.types.SimpleNamespace(Agent=self.Agent,Runner=self.types.SimpleNamespace(run=run),RunConfig=lambda **kw:kw),'pydantic':self.types.SimpleNamespace(BaseModel=self.Schema)}
    def test_sales_actual_orchestration_preserves_unapproved_state(self):
        import asyncio
        async def run(agent,payload,**kwargs):
            self.calls.append(agent.name)
            values={'Prospect researcher':dict(need='CSV summaries',source_id='synthetic-brief-cedar-001',limitations='synthetic'), 'Outreach strategist':dict(value_proposition='Demo',source_id='synthetic-brief-cedar-001'),'Email writer':dict(subject='Demo',body='A sourced practice demonstration.',source_id='synthetic-brief-cedar-001'),'Quality reviewer':dict(passed=True,issues=[])}
            return self.types.SimpleNamespace(final_output=self.Schema(**values[agent.name]))
        with self.patch.dict(sys.modules,self.fake_modules(run)):
            adapter=load('academy_sales_adapter','02-sales-team','agents_adapter')
            result=asyncio.run(adapter.run_pipeline(sales.Prospect(**fixture('02-sales-team','prospect.json')['prospect']),'test-model'))
        self.assertEqual(len(self.calls),4)
        self.assertEqual(result['status'],'human_approval_required')
        self.assertEqual(result['draft']['status'],'draft')
        self.assertEqual(result['external_messages_sent'],0)
    def test_research_rejects_invented_model_citation(self):
        import asyncio
        async def run(agent,payload,**kwargs):
            value=self.Schema(objectives=['reporting'],questions=['time']) if agent.name=='Research planner' else self.Schema(summary='Claim',cited_source_ids=['invented'],uncertainties=[])
            return self.types.SimpleNamespace(final_output=value)
        with self.patch.dict(sys.modules,self.fake_modules(run)):
            adapter=load('academy_research_adapter','03-deep-research','agents_adapter')
            corpus=[research.Evidence(**e) for e in fixture('03-deep-research','evidence.json')['evidence']]
            with self.assertRaises(ValueError): asyncio.run(adapter.run_pipeline('Cedar reporting',corpus,'test-model'))
    def test_gradio_build_and_chat_without_shared_database(self):
        class Blocks:
            def __enter__(inner): return inner
            def __exit__(inner,*args): return False
        recorded={}
        def chatinterface(**kw): recorded.update(kw)
        fake=self.types.SimpleNamespace(Blocks=Blocks,Markdown=lambda text:None,ChatInterface=chatinterface)
        sys.modules['twin']=twin
        with self.patch.dict(sys.modules,{'gradio':fake}):
            app=load('academy_twin_app','01-digital-twin','app')
            app.build_app()
            result=recorded['fn']('Python experience',[])
        self.assertIn('profile-01',result)

if __name__=='__main__': unittest.main()
