"""Source-authored regression tests; central repository QA owns execution.

Single-account SQLite scope isolation is not an authenticated multi-tenant claim.
"""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

PROJECT=Path(__file__).resolve().parents[1]/'projects'/'08-mcp-trading-floor'
sys.path.insert(0,str(PROJECT))
from services import ToolServices

class PersistentMemoryTests(unittest.TestCase):
    def test_store_update_retrieve_literal_search_persistence_and_limit(self):
        with tempfile.TemporaryDirectory() as directory:
            database=str(Path(directory)/'paper.sqlite')
            service=ToolServices(database,memory_read_namespaces={'lesson'},memory_write_namespaces={'lesson'})
            service.remember('lesson','alpha','Original paper policy')
            service.remember('lesson','alpha','Updated paper approval policy')
            service.remember('lesson','beta','Another paper note')
            reopened=ToolServices(database,memory_read_namespaces={'lesson'},memory_write_namespaces=set())
            self.assertEqual(reopened.recall('lesson','alpha')['value'],'Updated paper approval policy')
            result=reopened.search_memory('lesson','PAPER',limit=1)
            self.assertEqual([item['key'] for item in result['matches']],['alpha'])
            self.assertFalse(reopened.search_memory('lesson','Original')['matches'])
            self.assertEqual(len(reopened.search_memory('lesson','paper',10)['matches']),2)
            self.assertFalse(reopened.search_memory('lesson',"%' OR 1=1 --")['matches'])
            self.assertFalse(reopened.search_memory('lesson','%')['matches'])
            self.assertFalse(reopened.search_memory('lesson','_')['matches'])
            with self.assertRaises(PermissionError): reopened.remember('lesson','denied','read-only caller')
    def test_configured_scope_is_frozen_and_cross_scope_queries_denied(self):
        with tempfile.TemporaryDirectory() as directory:
            database=str(Path(directory)/'paper.sqlite')
            trusted=ToolServices(database)
            trusted.remember('allowed','policy','Paper-only Academy fixture')
            trusted.remember('private','policy','OTHER_SCOPE_FAKE_CANARY')
            scopes={'allowed'}
            scoped=ToolServices(database,memory_read_namespaces=scopes,memory_write_namespaces=set())
            scopes.add('private')
            self.assertEqual(len(scoped.search_memory('allowed','paper')['matches']),1)
            with self.assertRaises(PermissionError): scoped.search_memory('private','policy')
            with self.assertRaises(PermissionError): scoped.recall('private','policy')
            self.assertNotIn('OTHER_SCOPE',json.dumps(scoped.search_memory('allowed','policy')))
    def test_query_limit_namespace_key_value_validation_precedes_database_access(self):
        service=ToolServices('/missing-owned-test-parent/database.sqlite',memory_read_namespaces={'lesson'},memory_write_namespaces={'lesson'})
        for query,limit in [('',5),('   ',5),('x'*501,5),(None,5),('paper',0),('paper',11),('paper',True),('paper',1.5)]:
            with self.assertRaises(ValueError):service.search_memory('lesson',query,limit)
        for namespace in [None,'',' lesson','lesson ','x'*81]:
            with self.assertRaises(ValueError):service.search_memory(namespace,'paper')
        for key in [None,'',123,'x'*101]:
            with self.assertRaises(ValueError):service.recall('lesson',key)
        with self.assertRaises(ValueError):service.remember('lesson','key',None)
        with self.assertRaises(ValueError):service.remember('lesson','key','x'*10001)
        with self.assertRaises(PermissionError):service.search_memory('other','paper')
    def test_credentials_and_known_canaries_rejected_or_withheld_not_exposed(self):
        with tempfile.TemporaryDirectory() as directory:
            database=str(Path(directory)/'paper.sqlite')
            scoped=ToolServices(database,memory_read_namespaces={'lesson'},memory_write_namespaces={'lesson'},memory_forbidden_strings={'KNOWN_FAKE_CANARY'})
            for value in ['api_key=FAKE_CREDENTIAL','Authorization: Bearer FAKE_BEARER','KNOWN_FAKE_CANARY',
                          '{"password":"FAKE_JSON_PASSWORD"}',"{'api_key': 'FAKE_QUOTED_API_KEY'}"]:
                with self.assertRaises(ValueError):scoped.remember('lesson','unsafe',value)
            # Preserve a historical unsafe row as history; never return its value.
            with scoped.connection() as floor:
                floor.db.execute('CREATE TABLE IF NOT EXISTS tool_memory(namespace TEXT,key TEXT,value TEXT,PRIMARY KEY(namespace,key))')
                floor.db.execute('INSERT INTO tool_memory VALUES (?,?,?)',('lesson','old-unsafe','paper password=FAKE_HISTORICAL'))
                floor.db.execute('INSERT INTO tool_memory VALUES (?,?,?)',('lesson','old-unsafe-json','{"password":"FAKE_JSON_HISTORICAL","note":"paper"}'))
            scoped.remember('lesson','safe','paper approval policy')
            self.assertTrue(scoped.recall('lesson','old-unsafe')['withheld'])
            self.assertTrue(scoped.recall('lesson','old-unsafe-json')['withheld'])
            result=scoped.search_memory('lesson','paper')
            self.assertEqual([row['key'] for row in result['matches']],['safe'])
            self.assertNotIn('FAKE_HISTORICAL',json.dumps(result))
            self.assertNotIn('FAKE_JSON_HISTORICAL',json.dumps(result))
            with self.assertRaises(ValueError):scoped.search_memory('lesson','KNOWN_FAKE_CANARY')
    def test_scope_configuration_shape_rejected(self):
        with self.assertRaises(ValueError):ToolServices(memory_read_namespaces='lesson')
        with self.assertRaises(ValueError):ToolServices(memory_write_namespaces={''})
        with self.assertRaises(ValueError):ToolServices(memory_forbidden_strings='FAKE')

@unittest.skipUnless(importlib.util.find_spec('mcp'),'actual optional MCP SDK required')
class ActualMemoryMCPTests(unittest.IsolatedAsyncioTestCase):
    async def test_actual_stdio_store_update_recall_search_restart_and_scope_denial(self):
        from mcp import ClientSession,StdioServerParameters
        from mcp.client.stdio import stdio_client
        def payload(result):
            self.assertFalse(result.isError)
            if result.structuredContent is not None:return result.structuredContent
            return json.loads(result.content[0].text)
        with tempfile.TemporaryDirectory() as directory:
            database=str(Path(directory)/'memory.sqlite')
            ToolServices(database).remember('private','outside','OUTSIDE_SCOPE_FAKE_CANARY')
            env={'ACADEMY_PAPER_DB':database,'ACADEMY_MEMORY_READ_NAMESPACES':'["lesson"]','ACADEMY_MEMORY_WRITE_NAMESPACES':'["lesson"]'}
            launcher='import sys;sys.path.insert(0,'+repr(str(PROJECT))+');from mcp_server import mcp;mcp.run(transport="stdio")'
            params=StdioServerParameters(command=sys.executable,args=['-c',launcher],env=env)
            async with stdio_client(params) as streams:
                async with ClientSession(*streams) as client:
                    await client.initialize()
                    self.assertIn('search_memory',{tool.name for tool in (await client.list_tools()).tools})
                    payload(await client.call_tool('remember',{'namespace':'lesson','key':'policy','value':'Original paper policy'}))
                    payload(await client.call_tool('remember',{'namespace':'lesson','key':'policy','value':'Updated paper approval policy'}))
                    self.assertTrue((await client.call_tool('recall',{'namespace':'private','key':'outside'})).isError)
                    self.assertTrue((await client.call_tool('search_memory',{'namespace':'private','query':'OUTSIDE'})).isError)
            # New real server/client process reads the same persisted SQLite file.
            async with stdio_client(params) as streams:
                async with ClientSession(*streams) as client:
                    await client.initialize()
                    recalled=payload(await client.call_tool('recall',{'namespace':'lesson','key':'policy'}))
                    self.assertEqual(recalled['value'],'Updated paper approval policy')
                    searched=payload(await client.call_tool('search_memory',{'namespace':'lesson','query':'approval','limit':1}))
                    self.assertEqual(searched['matches'],[{'key':'policy','value':'Updated paper approval policy'}])
                    self.assertNotIn('OUTSIDE_SCOPE',json.dumps(searched))
                    self.assertTrue((await client.call_tool('search_memory',{'namespace':'lesson','query':'x','limit':0})).isError)
                    self.assertTrue((await client.call_tool('remember',{'namespace':'agent-runs','key':'forged','value':'approved'})).isError)

if __name__=='__main__':unittest.main()
