"""AUTHOR-ONLY new tests; central QA must execute them and retain real results.

Transport doubles test application boundaries, not actual HTTPS/provider success.
SDK construction checks use real optional CrewAI when central QA installs it.
"""
from email.message import Message
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch, Mock

BASE = Path(__file__).resolve().parents[1] / 'projects/04-market-intelligence/learning'
sys.path.insert(0, str(BASE / 'src'))
from academy_market_debate.external_research import ExternalResearch, ResearchQuery, NoRedirect, SOURCES, run_research
from academy_market_debate.memory_integration import build_memory_crew

class ResponseDouble:
    def __init__(self, source='crewai-tools', body=b'<html><body>Custom tools need typed input.</body></html>', content_type='text/html', status=200, url=None):
        self.body = body; self.status = status
        self.url = url or SOURCES[source]
        self.headers = Message(); self.headers['Content-Type'] = content_type
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def geturl(self): return self.url
    def read(self, maximum): return self.body[:maximum]

class ExternalResearchSemanticTests(unittest.TestCase):
    def test_typed_query_rejects_empty_boolean_and_excess(self):
        for args in [('', 1), ('x'*101, 1), ('tools', True), ('tools', 4)]:
            with self.assertRaises(ValueError): ResearchQuery(*args)
    def test_construction_does_no_io(self):
        with patch('academy_market_debate.external_research.build_opener') as opener:
            ExternalResearch()
        opener.assert_not_called()
    def test_domain_collection_rejects_user_url(self):
        with self.assertRaises(ValueError): ExternalResearch(source_ids=('https://localhost/private',))
    def test_redirect_denied(self):
        with self.assertRaises(ValueError): NoRedirect().redirect_request(None,None,302,'redirect',{},'http://localhost')
    def test_transport_double_provenance_and_cache(self):
        opener = Mock(); opener.open.return_value = ResponseDouble()
        search = ExternalResearch(source_ids=('crewai-tools',), request_limit=1)
        with patch('academy_market_debate.external_research.build_opener', return_value=opener):
            first = search.search('typed'); second = search.search('tools')
        self.assertEqual(search.requests, 1)
        opener.open.assert_called_once()
        self.assertEqual(opener.open.call_args.kwargs['timeout'], 8.0)
        self.assertEqual(first[0]['url'], SOURCES['crewai-tools'])
        self.assertIsNone(first[0]['published_at'])
        self.assertEqual(len(first[0]['body_sha256']),64)
        self.assertIn('typed input', first[0]['excerpt'])
        self.assertEqual(second[0]['source_id'], 'crewai-tools')
    def test_hidden_scripts_are_not_research(self):
        response = ResponseDouble(body=b'<html><script>invented benefit</script><body>Tools only.</body></html>')
        opener = Mock(); opener.open.return_value = response
        with patch('academy_market_debate.external_research.build_opener', return_value=opener):
            self.assertEqual(ExternalResearch(source_ids=('crewai-tools',)).search('invented'), [])
    def test_timeout_charged_no_automatic_replay(self):
        opener = Mock(); opener.open.side_effect = TimeoutError('transport double timeout')
        search = ExternalResearch(source_ids=('crewai-tools',))
        with patch('academy_market_debate.external_research.build_opener', return_value=opener):
            with self.assertRaises(TimeoutError): search.search('tools')
            with self.assertRaises(RuntimeError): search.search('tools')
        self.assertEqual(search.requests,1); opener.open.assert_called_once()
    def test_bad_response_types_and_destination_hold(self):
        for response in [ResponseDouble(content_type='application/json'), ResponseDouble(status=201),
                         ResponseDouble(url='https://example.com/foreign'),ResponseDouble(body=b'\xff')]:
            opener=Mock();opener.open.return_value=response
            with patch('academy_market_debate.external_research.build_opener',return_value=opener):
                with self.assertRaises((ValueError,UnicodeDecodeError)):
                    ExternalResearch(source_ids=('crewai-tools',)).search('tools')
    def test_oversize_and_empty_hold(self):
        for body in [b'x'*1025, b'<html><script>only hidden</script></html>']:
            opener=Mock();opener.open.return_value=ResponseDouble(body=body)
            with patch('academy_market_debate.external_research.build_opener',return_value=opener):
                with self.assertRaises(ValueError): ExternalResearch(source_ids=('crewai-tools',),max_bytes=1024).search('tools')
    def test_request_budget_applies_across_documents(self):
        opener=Mock();opener.open.return_value=ResponseDouble()
        with patch('academy_market_debate.external_research.build_opener',return_value=opener):
            search=ExternalResearch(request_limit=1)
            with self.assertRaises(RuntimeError): search.search('missingterm')
        self.assertEqual(search.requests,1)
    def test_provider_and_memory_optins_before_sdk(self):
        with self.assertRaises(PermissionError): run_research('unused','tools')
        with self.assertRaises(PermissionError): build_memory_crew('unused',BASE/'fixtures/retailer-facts.json',{},'/unused','run')

@unittest.skipUnless(importlib.util.find_spec('crewai') is not None,
                     'Optional CrewAI SDK unavailable: run these actual SDK cases in the pinned environment; a skip is not a pass')
class ActualSDKSemanticConstructionTests(unittest.TestCase):
    """Must be run by central QA under PrivateNetwork/socket deny; no kickoffs."""
    def test_real_research_tool_exposure_and_typed_schema(self):
        from academy_market_debate.external_research import build_research_crew
        crew=build_research_crew('openai/gpt-4o-mini',ExternalResearch())
        self.assertEqual(len(crew.agents[0].tools),1)
        self.assertEqual(crew.agents[1].tools,[])
        self.assertEqual(crew.tasks[1].context,[crew.tasks[0]])
        schema=crew.agents[0].tools[0].args_schema.model_json_schema()
        self.assertEqual(schema['properties']['query']['type'],'string')
        self.assertIsNotNone(crew.tasks[1].output_pydantic)

    def test_actual_memory_scope_wiring_without_backend_calls(self):
        with tempfile.TemporaryDirectory(prefix='academy-memory-structural-') as directory:
            store=Path(directory)/'fresh-store'
            crew,pack,search,memory,scope=build_memory_crew(
                'openai/gpt-4o-mini',BASE/'fixtures/retailer-facts.json',
                {'provider':'openai','config':{'model_name':'text-embedding-3-large'}},
                store,'structural-run',authorize_provider=True)
            self.assertEqual(scope,'/academy/structural-run/approved')
            self.assertEqual(crew.memory.root_path,scope)
            self.assertTrue(all(agent.memory.root_path==scope for agent in crew.agents))
            # This proves references only; no remember, recall, reset or kickoff is invoked.
            self.assertEqual(search.calls,0)

if __name__=='__main__': unittest.main()
