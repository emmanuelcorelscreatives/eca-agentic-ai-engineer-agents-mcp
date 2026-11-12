"""New author-only tests. Scripted providers/registries are explicitly test doubles.

Parent QA owns execution. A passing double does not establish a real model run.
"""
import asyncio
import importlib.util
import json
import os
from pathlib import Path
from types import SimpleNamespace
import sys
import tempfile
import unittest
import uuid

PROJECT=Path(__file__).resolve().parents[1]/'projects'/'08-mcp-trading-floor'
sys.path.insert(0,str(PROJECT))
from agent_harness import ToolCall,FinalAnswer,ToolObservation
from retrieval_lab.workflow import ResearchWorkflow,ResearchBudget
from retrieval_lab.core import RetrievalError,HashEmbedding
from retrieval_lab.progressive import ProgressiveRouter,ToolSpec
from retrieval_lab.secret_boundary import SecretBoundary
from retrieval_lab.rag import Principal,DocumentRAG
from retrieval_lab.solutions import grounded_rag_quotes
from retrieval_lab.search import BoundedSearch,SearchFailure

STATIC='http://127.0.0.1:8899/static-product.html'
DYNAMIC='http://127.0.0.1:8899/dynamic-product.html'

class ScriptedRegistry:
    """UNIT TEST DOUBLE; no SDK/browser/server/network execution."""
    def __init__(self): self.calls=[];self.status='ok';self.text='Paper orders require human approval before execution.'
    def descriptors(self): return [{'name':name} for name in ('fetch::fetch','browser::browser_navigate','browser::browser_snapshot','browser::browser_click')]
    async def dispatch(self,name,arguments,timeout_seconds):
        self.calls.append((name,arguments))
        return ToolObservation(name,self.status,{'content':[{'type':'text','text':self.text}],'isError':False},str(len(self.calls)))

class ScriptedProvider:
    """UNIT TEST DOUBLE, never advertised as a genuine AI-agent observation."""
    def __init__(self,actions): self.actions=iter(actions);self.history=[]
    async def next_action(self,messages,tools):
        self.history.append({'messages':messages.copy(),'tools':tools})
        return next(self.actions)

class WorkflowTests(unittest.IsolatedAsyncioTestCase):
    async def test_provider_selects_fetch_and_browser_shared_budget_and_supported_claim(self):
        registry=ScriptedRegistry()
        provider=ScriptedProvider([ToolCall('research::fetch_page',{'url':STATIC}),ToolCall('research::browse_page',{'url':DYNAMIC}),FinalAnswer(json.dumps({'claims':[{'citation':'source-2','quote':'human approval'}]}))])
        result=await ResearchWorkflow(registry,{STATIC,DYNAMIC}).run('Compare products',provider)
        self.assertEqual([name for name,_ in registry.calls],['fetch::fetch','browser::browser_navigate','browser::browser_snapshot'])
        self.assertEqual(result['actual_tool_calls'],3)
        self.assertEqual(result['evidence'][1]['source_url'],DYNAMIC)
        self.assertEqual(result['evidence'][1]['call_ids'],('2','3'))
        self.assertFalse(result['abstained'])
        self.assertTrue(all('argument_sha256' in row and 'elapsed_seconds' in row for row in result['trace']))
        self.assertNotIn('content',result['trace'][0])
    async def test_exact_policy_rejects_file_private_unenrolled_query_and_guessed_submit(self):
        for name,url in [('research::fetch_page','file:///owned-sentinel'),('research::fetch_page','http://169.254.169.254/latest/meta-data/'),('research::fetch_page',STATIC+'?secret=fixture'),('browser::browser_click',STATIC)]:
            registry=ScriptedRegistry(); workflow=ResearchWorkflow(registry,{STATIC})
            with self.assertRaises((RetrievalError,PermissionError)): await workflow.read(name,{'url':url})
            self.assertEqual(registry.calls,[])
    async def test_reviewer_cannot_browse_and_browser_needs_two_remaining_calls(self):
        registry=ScriptedRegistry(); workflow=ResearchWorkflow(registry,{STATIC},role='reviewer')
        with self.assertRaises(PermissionError): await workflow.read('research::browse_page',{'url':STATIC})
        limited=ResearchWorkflow(registry,{DYNAMIC},budget=ResearchBudget(tool_calls=1))
        with self.assertRaises(RetrievalError): await limited.read('research::browse_page',{'url':DYNAMIC})
        self.assertEqual(registry.calls,[])
    async def test_failure_unknown_no_automatic_replay(self):
        registry=ScriptedRegistry();registry.status='unknown'
        with self.assertRaises(RetrievalError): await ResearchWorkflow(registry,{STATIC}).read('research::fetch_page',{'url':STATIC})
        self.assertEqual(len(registry.calls),1)
    async def test_unsupported_citation_and_quote_and_empty_abstention(self):
        workflow=ResearchWorkflow(ScriptedRegistry(),{STATIC})
        await workflow.read('research::fetch_page',{'url':STATIC})
        for claim in [{'citation':'invented','quote':'human approval'},{'citation':'source-1','quote':'Approval is optional.'}]:
            with self.assertRaises(RetrievalError): workflow.validate_final(json.dumps({'claims':[claim]}))
        self.assertTrue(workflow.validate_final('{"claims":[]}')['abstained'])
    async def test_fake_canary_not_forwarded_in_source_evidence_or_final(self):
        registry=ScriptedRegistry();registry.text='Policy. api_key=FAKE_CANARY_ABC Bearer FAKE_TOKEN_XYZ'
        workflow=ResearchWorkflow(registry,{STATIC},secret_boundary=SecretBoundary(['FAKE_CANARY_ABC','FAKE_TOKEN_XYZ']))
        result=await workflow.read('research::fetch_page',{'url':STATIC})
        self.assertNotIn('FAKE_CANARY',json.dumps(result));self.assertNotIn('FAKE_TOKEN',json.dumps(result))
    async def test_malformed_nontext_result_fails(self):
        class Bad(ScriptedRegistry):
            async def dispatch(self,*args): return ToolObservation('fetch::fetch','ok',{'content':[{'type':'image','data':'not-real'}]},'bad')
        with self.assertRaises(RetrievalError): await ResearchWorkflow(Bad(),{STATIC}).read('research::fetch_page',{'url':STATIC})

class ProgressiveTests(unittest.IsolatedAsyncioTestCase):
    async def test_discovery_dispatch_guessed_hidden_revoked_and_two_session_isolation(self):
        permission={'rag:read'};calls=[]
        spec=ToolSpec('retrieve_documents','rag','rag:read','Read chunks',{'type':'object','properties':{'query':{'type':'string'}},'required':['query'],'additionalProperties':False},lambda query:calls.append(query) or {'matches':[]})
        first=ProgressiveRouter([spec],lambda:permission);second=ProgressiveRouter([spec],lambda:permission)
        self.assertEqual([x['name'] for x in first.descriptors()],['discover_capability'])
        with self.assertRaises(PermissionError): await first.dispatch('retrieve_documents',{'query':'approval'})
        first.discover('rag');await first.dispatch('retrieve_documents',{'query':'approval'})
        self.assertEqual([x['name'] for x in second.descriptors()],['discover_capability'])
        permission.clear()
        with self.assertRaises(PermissionError): await first.dispatch('retrieve_documents',{'query':'approval'})
        self.assertEqual(calls,['approval'])
    async def test_bad_schema_before_provider_invocation(self):
        calls=[];spec=ToolSpec('search_web','search','search:read','Search',{'type':'object','properties':{'query':{'type':'string'}},'required':['query'],'additionalProperties':False},lambda **kwargs:calls.append(kwargs))
        router=ProgressiveRouter([spec],lambda:{'search:read'});router.discover('search')
        with self.assertRaises(Exception): await router.dispatch('search_web',{'query':123})
        self.assertEqual(calls,[])

class SearchTests(unittest.TestCase):
    def test_empty_invalid_and_quota_mapping(self):
        class FixtureFetch:
            """UNIT TEST DOUBLE, not a configured provider observation."""
            origins={('https','search.academy.example',443)}
            origin=staticmethod(lambda _:('https','search.academy.example',443))
            def read(self,url): return '{"results":[]}','application/json'
        result=BoundedSearch('https://search.academy.example/search',FixtureFetch()).search('  approval   policy ')
        self.assertEqual(result['query'],'approval policy');self.assertTrue(result['empty'])
        with self.assertRaises(SearchFailure): BoundedSearch('https://search.academy.example/search',FixtureFetch()).search('')
        class Bad(FixtureFetch):
            def read(self,url): return '{"results":[{}]}','application/json'
        with self.assertRaises(SearchFailure) as context: BoundedSearch('https://search.academy.example/search',Bad()).search('policy')
        self.assertEqual(context.exception.code,'INVALID_RESPONSE')
        class Quota(FixtureFetch):
            def read(self,url):
                from urllib.error import HTTPError
                raise RetrievalError('HTTP429') from HTTPError(url,429,'fixture',{},None)
        with self.assertRaises(SearchFailure) as context: BoundedSearch('https://search.academy.example/search',Quota()).search('policy')
        self.assertEqual(context.exception.code,'RATE_LIMIT')

@unittest.skipUnless(importlib.util.find_spec('qdrant_client'),'requires actual optional qdrant-client')
class ActualLocalRAGTests(unittest.TestCase):
    def test_real_local_chunks_duplicate_replace_isolation_delete_and_citations(self):
        """Real embedded SDK, not a claim of an HTTP daemon/service run."""
        from qdrant_client import QdrantClient
        with tempfile.TemporaryDirectory() as directory:
            client=QdrantClient(path=directory)
            try:
                first=DocumentRAG(client,Principal('author-a','tenant-a',frozenset({'rag:read','rag:write'})),min_score=0)
                second=DocumentRAG(client,Principal('author-b','tenant-b',frozenset({'rag:read','rag:write'})),min_score=0)
                one=first.ingest('policy','Human approval is required.','academy://policy')
                self.assertTrue(first.ingest('policy','Human approval is required.','academy://policy')['duplicate'])
                second.ingest('private','Tenant B private document.','academy://private')
                result=first.retrieve('human approval');self.assertEqual(len(result['matches']),1)
                chunk=result['matches'][0];self.assertEqual(chunk['tenant'],'tenant-a');self.assertEqual(chunk['start'],0)
                grounded_rag_quotes(result,[{'citation':chunk['chunk_id'],'quote':'approval is required'}])
                with self.assertRaises(RetrievalError): grounded_rag_quotes(result,[{'citation':chunk['chunk_id'],'quote':'approval is optional'}])
                with self.assertRaises(RetrievalError): first.ingest('policy','Changed','academy://policy')
                first.ingest('policy','Explicit human approval remains required.','academy://policy',replace=True)
                self.assertEqual(len(first.retrieve('approval')['matches']),1)
                first.delete('policy');self.assertTrue(first.retrieve('approval')['insufficient_evidence'])
                self.assertEqual(len(second.retrieve('private')['matches']),1)
            finally:client.close()
    def test_missing_write_permission_and_invalid_encoder_preserve_old_document(self):
        from qdrant_client import QdrantClient
        with tempfile.TemporaryDirectory() as directory:
            client=QdrantClient(path=directory)
            try:
                store=DocumentRAG(client,Principal('a','tenant',frozenset({'rag:read','rag:write'})),min_score=0)
                store.ingest('policy','Original approval policy','academy://policy')
                class InvalidEncoder(HashEmbedding):
                    def encode(self,text): return [1.0]
                store.encoder=InvalidEncoder()
                with self.assertRaises(RetrievalError): store.ingest('policy','Changed policy','academy://policy',replace=True)
                store.encoder=HashEmbedding();self.assertIn('Original',store.retrieve('policy')['matches'][0]['text'])
                reader=DocumentRAG(client,Principal('reader','tenant',frozenset({'rag:read'})),min_score=0)
                with self.assertRaises(PermissionError): reader.ingest('new','Disallowed','academy://new')
            finally:client.close()

@unittest.skipUnless(os.environ.get('ACADEMY_QDRANT_TEST_URL'),'actual HTTP Qdrant service not explicitly configured')
class ActualServiceRAGTests(unittest.TestCase):
    def test_explicit_real_service_insert_search_delete(self):
        tenant='qa-'+uuid.uuid4().hex
        store=DocumentRAG.service(os.environ['ACADEMY_QDRANT_TEST_URL'],Principal('qa',tenant,frozenset({'rag:read','rag:write'})),collection='academy_qa_rag_v1')
        try:
            store.ingest('policy','Human approval required','academy://qa/policy')
            self.assertEqual(store.retrieve('approval')['matches'][0]['document_id'],'policy')
            store.delete('policy');self.assertTrue(store.retrieve('approval')['insufficient_evidence'])
        finally:store.close()

@unittest.skipUnless(importlib.util.find_spec('mcp'),'actual optional MCP SDK required')
class ActualProgressiveProtocolTests(unittest.IsolatedAsyncioTestCase):
    async def test_real_stdio_progressive_list_and_permission_denial(self):
        from mcp import ClientSession,StdioServerParameters
        from mcp.client.stdio import stdio_client
        launcher='import sys;sys.path.insert(0,'+repr(str(PROJECT))+');import asyncio;from retrieval_lab.research_server import main;asyncio.run(main())'
        env={'ACADEMY_SUBJECT':'academy-qa-reader','ACADEMY_TENANT':'academy-qa-only','ACADEMY_PERMISSIONS':'rag:read'}
        async with stdio_client(StdioServerParameters(command=sys.executable,args=['-c',launcher],env=env)) as streams:
            async with ClientSession(*streams) as client:
                await client.initialize()
                before=await client.list_tools()
                self.assertEqual([x.name for x in before.tools],['discover_capability'])
                guessed=await client.call_tool('retrieve_documents',{'query':'approval'})
                self.assertTrue(guessed.isError)
                discovered=await client.call_tool('discover_capability',{'capability':'rag'})
                self.assertFalse(discovered.isError)
                after=await client.list_tools()
                self.assertEqual({x.name for x in after.tools},{'discover_capability','retrieve_documents'})
                denied=await client.call_tool('ingest_document',{'document_id':'private','text':'denied','source_uri':'academy://denied'})
                self.assertTrue(denied.isError)

if __name__=='__main__': unittest.main()
