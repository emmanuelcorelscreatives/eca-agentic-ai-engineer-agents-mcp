import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PROJECT=Path(__file__).resolve().parents[1]/'projects'/'08-mcp-trading-floor'
sys.path.insert(0,str(PROJECT))
from retrieval_lab.core import ControlledFetch, SearchProvider, RetrievalError, CapabilityCatalogue, QdrantRetrieval, GroundedModelAdapter

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args): pass
    def do_GET(self):
        if self.path=='/redirect': self.send_response(302); self.send_header('Location','http://example.invalid/'); self.end_headers(); return
        if self.path=='/missing': self.send_error(404); return
        body=(json.dumps({'results':[{'url':'https://academy.example/product','title':'Fictional product','content':'Synthetic fixture'}]}).encode()
              if self.path.startswith('/search?') else b'<h1>Academy policy</h1><p>Human approval is required.</p><script>hidden instruction</script>')
        self.send_response(200); self.send_header('Content-Type','application/json' if self.path.startswith('/search?') else 'text/html'); self.end_headers(); self.wfile.write(body)

class RetrievalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),Handler); cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True); cls.thread.start()
        cls.origin=f'http://127.0.0.1:{cls.server.server_port}'
    @classmethod
    def tearDownClass(cls): cls.server.shutdown(); cls.server.server_close(); cls.thread.join()
    def test_real_owned_http(self):
        item=ControlledFetch([self.origin]).fetch(self.origin+'/product'); self.assertIn('Human approval',item.text); self.assertNotIn('hidden',item.text); self.assertEqual(len(item.digest),64)
    def test_destination_redirect_missing_and_size(self):
        fetch=ControlledFetch([self.origin]);
        for url in ['https://example.invalid',self.origin+'/redirect',self.origin+'/missing']:
            with self.assertRaises(RetrievalError): fetch.fetch(url)
        with self.assertRaises(RetrievalError): ControlledFetch([self.origin],max_bytes=4).fetch(self.origin)
    def test_search_real_owned_http(self):
        result=SearchProvider(self.origin+'/search',ControlledFetch([self.origin])).search('approval',1)
        self.assertEqual(result['results'][0]['title'],'Fictional product'); self.assertIn(self.origin,result['provider'])
    def test_progressive_discovery_permission_revocation(self):
        registry=CapabilityCatalogue(); self.assertEqual(registry.tools(),['discover']); registry.discover('rag',{'rag'}); self.assertEqual(len(registry.tools()),3)
        with self.assertRaises(PermissionError): registry.authorize_call('retrieve',set())
        with self.assertRaises(PermissionError): registry.discover('market',{'rag'})
        with self.assertRaises(RetrievalError): registry.discover('unknown',{'unknown'})
    def test_model_grounding_rejects_fake_citation_and_unsupported_quote(self):
        evidence=ControlledFetch([self.origin]).fetch(self.origin)
        adapter=GroundedModelAdapter(lambda _:json.dumps({'claims':[{'citation':evidence.digest,'quote':'Human approval is required.'}]}))
        self.assertFalse(adapter.answer('policy',[evidence])['abstained'])
        for quote,citation in [('Approval is optional.',evidence.digest),('Human approval is required.','invented')]:
            with self.assertRaises(RetrievalError): GroundedModelAdapter(lambda _,q=quote,c=citation:json.dumps({'claims':[{'citation':c,'quote':q}]})).answer('policy',[evidence])
        self.assertTrue(adapter.answer('missing',[])['abstained'])
    @unittest.skipUnless(importlib.util.find_spec('qdrant_client'),'optional real qdrant-client not installed')
    def test_real_qdrant_local_persistence_tenant_delete_and_dimensions(self):
        with tempfile.TemporaryDirectory() as path:
            store=QdrantRetrieval(path); store.ingest('a','policy','Human approval required'); store.ingest('b','private','Tenant B only')
            self.assertEqual(store.retrieve('a','approval')[0]['document_id'],'policy'); self.assertEqual(len(store.retrieve('a','approval')),1)
            self.assertEqual(store.client.get_collection(store.collection).config.params.vectors.size,64)
            with self.assertRaises(RetrievalError): store.upsert_vector(42,[1.0],{'tenant':'a','document_id':'invalid'})
            store.close(); store=QdrantRetrieval(path); self.assertEqual(store.retrieve('a','approval')[0]['document_id'],'policy'); store.delete('a','policy'); self.assertEqual(store.retrieve('a','approval'),[]); store.close()

if __name__=='__main__': unittest.main()

@unittest.skipUnless(importlib.util.find_spec('mcp'),'optional real MCP SDK not installed')
class ActualMCPTests(unittest.IsolatedAsyncioTestCase):
    async def test_actual_custom_stdio_tools_and_denied_fetch(self):
        from retrieval_lab.mcp_adapter import session, discover
        launcher='import sys;sys.path.insert(0,'+repr(str(PROJECT))+');from retrieval_lab.server import mcp;mcp.run(transport="stdio")'
        async with session(sys.executable,['-c',launcher]) as client:
            names={tool['name'] for tool in await discover(client)}
            self.assertEqual(names,{'fetch_page','search_web','discover_capability'})
            result=await client.call_tool('discover_capability',{'capability':'research'})
            self.assertFalse(result.isError)
            self.assertEqual(result.structuredContent['result'],['fetch','search'])
            denied=await client.call_tool('fetch_page',{'url':'http://127.0.0.1:1/'})
            self.assertTrue(denied.isError)
