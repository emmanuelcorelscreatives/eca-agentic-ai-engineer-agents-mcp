import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'projects' / '08-mcp-trading-floor' / 'trading_floor.py'
spec = importlib.util.spec_from_file_location('academy_project8', SOURCE)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

class TradingFloorTests(unittest.TestCase):
    def setUp(self): self.floor = module.TradingFloor()
    def tearDown(self): self.floor.close()
    def test_unapproved_order_cannot_move_cash(self):
        p = self.floor.propose('ACA', 5)
        with self.assertRaises(ValueError): self.floor.execute(p, 'one')
        self.assertEqual(self.floor.state()['cash'], '10000.00')
    def test_exact_decimal_and_idempotent_retry(self):
        p = self.floor.propose('ACA', 5)
        self.floor.approve(p, 'reviewer')
        first = self.floor.execute(p, 'one')
        self.assertEqual(first, self.floor.execute(p, 'one'))
        self.assertEqual(self.floor.state()['cash'], '9373.75')
        self.assertEqual(self.floor.state()['positions']['ACA'], 5)
        with self.assertRaises(ValueError): self.floor.execute(p, 'two')
    def test_reused_key_for_changed_order_rejected(self):
        p = self.floor.propose('ACA', 5); self.floor.approve(p, 'reviewer'); self.floor.execute(p, 'one')
        with self.assertRaises(ValueError): self.floor.execute(self.floor.propose('ACA', 4), 'one')
    def test_short_sales_and_large_orders_rejected(self):
        self.assertEqual(self.floor.risk(self.floor.propose('ACA', 1, 'SELL'))['reasons'], ['short_sales_disabled'])
        self.assertIn('order_limit', self.floor.risk(self.floor.propose('ACA', 20))['reasons'])
    def test_position_limit_across_multiple_orders(self):
        p = self.floor.propose('ACA', 15); self.floor.approve(p, 'human'); self.floor.execute(p, '1')
        self.assertIn('position_limit', self.floor.risk(self.floor.propose('ACA', 6))['reasons'])
    def test_tampered_quote_and_noninteger_quantity(self):
        for p in [module.Proposal('ACA','BUY',1,'1.00','fixture-aca-001'), module.Proposal('ACA','BUY',True,'125.25','fixture-aca-001')]:
            with self.assertRaises(ValueError): self.floor.risk(p)
    def test_sell_after_buy_and_trace(self):
        buy=self.floor.propose('LAB',3); self.floor.approve(buy,'human'); self.floor.execute(buy,'buy')
        sell=self.floor.propose('LAB',2,'SELL'); self.floor.approve(sell,'human'); self.floor.execute(sell,'sell')
        self.assertEqual(self.floor.state()['cash'],'9957.90')
        self.assertEqual(len([r for r in self.floor.history() if r['event']=='paper_execution']),2)
    def test_persistent_memory(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=str(Path(tmp)/'paper.sqlite'); a=module.TradingFloor(path); p=a.propose('LAB',1); a.approve(p,'human'); a.execute(p,'persistent'); a.close()
            b=module.TradingFloor(path)
            try: self.assertEqual(b.state()['positions'],{'LAB':1})
            finally: b.close()
    def test_nonfinite_money_rejected(self):
        for value in ['NaN','Infinity','0','-1']:
            with self.assertRaises(ValueError): module.amount(value)


class ThreadedAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import importlib
        cls.project_path=str(SOURCE.parent)
        sys.path.insert(0,cls.project_path)
        cls.services_module=importlib.import_module('services')

    def test_tools_created_on_main_invoked_on_worker_threads(self):
        from concurrent.futures import ThreadPoolExecutor
        with tempfile.TemporaryDirectory() as tmp:
            service=self.services_module.ToolServices(str(Path(tmp)/'tools.sqlite'))
            with ThreadPoolExecutor(max_workers=4) as pool:
                results=list(pool.map(service.research_company,['ACA','LAB','EDU','ACA']))
                states=list(pool.map(lambda _:service.portfolio(),range(4)))
            self.assertEqual(len(results),4)
            self.assertTrue(all(row['cash']=='10000.00' for row in states))

    def test_memory_is_persistent_across_threads_and_instances(self):
        from concurrent.futures import ThreadPoolExecutor
        with tempfile.TemporaryDirectory() as tmp:
            path=str(Path(tmp)/'memory.sqlite')
            one=self.services_module.ToolServices(path)
            with ThreadPoolExecutor(max_workers=1) as pool:
                pool.submit(one.remember,'lesson','decision','paper only').result()
                result=pool.submit(self.services_module.ToolServices(path).recall,'lesson','decision').result()
            self.assertEqual(result['value'],'paper only')
            self.assertFalse(one.recall('other','decision')['found'])

    def test_retrieval_grounding_and_abstention(self):
        with tempfile.TemporaryDirectory() as tmp:
            service=self.services_module.ToolServices(str(Path(tmp)/'rag.sqlite'))
            result=service.grounded_brief('analytics')
            self.assertEqual(result['claims'][0]['citation'],'fixture-lab-001')
            self.assertTrue(service.grounded_brief('zzzznonexistent')['abstained'])
            with self.assertRaises(ValueError): service.search_research('',5)

    def test_multi_role_flow_stops_before_execution(self):
        with tempfile.TemporaryDirectory() as tmp:
            service=self.services_module.ToolServices(str(Path(tmp)/'roles.sqlite'))
            result=service.orchestrate('ACA',5)
            self.assertEqual(result['next_state'],'AWAITING_HUMAN_APPROVAL')
            self.assertFalse(result['execution_performed'])
            self.assertEqual(service.portfolio()['cash'],'10000.00')
            self.assertTrue(service.recall('orchestration',result['risk_manager']['digest'])['found'])

    def test_memory_connection_mode_rejected(self):
        with self.assertRaises(ValueError): self.services_module.ToolServices(':memory:')

class OptionalAdapterThreadBoundaryTests(unittest.TestCase):
    """Exercise actual Python callbacks with framework shells, not protocol/UI tests."""
    def load_with_stubs(self,name,filename,stubs):
        from unittest.mock import patch
        spec=importlib.util.spec_from_file_location(name,SOURCE.parent/filename)
        loaded=importlib.util.module_from_spec(spec)
        with patch.object(sys, 'path', [str(SOURCE.parent), *sys.path]):
            with patch.dict(sys.modules,stubs): spec.loader.exec_module(loaded)
        return loaded

    def test_mcp_registered_callbacks_on_worker_threads(self):
        import types
        from concurrent.futures import ThreadPoolExecutor
        from unittest.mock import patch
        class FakeMCP:
            def __init__(self,*args): self.tools={}
            def tool(self):
                def register(fn): self.tools[fn.__name__]=fn; return fn
                return register
        stub=types.ModuleType('mcp.server.fastmcp'); stub.FastMCP=FakeMCP
        with tempfile.TemporaryDirectory() as tmp:
            with patch.dict('os.environ',{'ACADEMY_PAPER_DB':str(Path(tmp)/'mcp.sqlite')}):
                adapter=self.load_with_stubs('p8_mcp_thread_test','mcp_server.py',{'mcp':types.ModuleType('mcp'),'mcp.server':types.ModuleType('mcp.server'),'mcp.server.fastmcp':stub})
            with ThreadPoolExecutor(max_workers=2) as pool:
                research=pool.submit(adapter.mcp.tools['research_company'],'ACA').result()
                state=pool.submit(adapter.mcp.tools['portfolio']).result()
            self.assertEqual(research['evidence_id'],'fixture-aca-001')
            self.assertEqual(state['cash'],'10000.00')
            self.assertNotIn('approve',adapter.mcp.tools)
            self.assertNotIn('execute',adapter.mcp.tools)

    def test_api_state_callback_and_gradio_callback_worker_threads(self):
        import types
        from concurrent.futures import ThreadPoolExecutor
        class API:
            def __init__(self,**kwargs): pass
            def get(self,*args): return lambda fn:fn
            def post(self,*args): return lambda fn:fn
        fast=types.ModuleType('fastapi'); fast.FastAPI=API; fast.Header=lambda **kwargs:None; fast.HTTPException=RuntimeError
        pyd=types.ModuleType('pydantic'); pyd.BaseModel=object; pyd.ConfigDict=dict; pyd.Field=lambda **kwargs:None
        class Component:
            def __init__(self,*args,**kwargs): pass
            def __enter__(self): return self
            def __exit__(self,*args): pass
            def click(self,*args,**kwargs): pass
        gr=types.ModuleType('gradio')
        for key in ['Blocks','Markdown','Dropdown','Number','Button','JSON']: setattr(gr,key,Component)
        api=self.load_with_stubs('p8_api_thread_test','api.py',{'fastapi':fast,'pydantic':pyd})
        gui=self.load_with_stubs('p8_gradio_thread_test','gradio_app.py',{'gradio':gr})
        with tempfile.TemporaryDirectory() as tmp:
            api.DATABASE=str(Path(tmp)/'api.sqlite')
            with ThreadPoolExecutor(max_workers=2) as pool:
                state=pool.submit(api.state).result()
                research,risk,initial=pool.submit(gui.inspect,'ACA',5).result()
            self.assertEqual(state['portfolio']['cash'],'10000.00')
            self.assertTrue(risk['allowed'])
            self.assertEqual(research['symbol'],'ACA')

if __name__ == '__main__': unittest.main()
