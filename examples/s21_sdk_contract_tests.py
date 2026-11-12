"""Central-QA-only actual ADK state persistence contracts. No provider request.

Author has NOT executed this new suite. The short State context shim is clearly a
unit-test fixture; DatabaseSessionService and Event storage are genuine ADK APIs.
"""
import asyncio,json,os,subprocess,sys,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from google.adk.sessions.state import State
from examples.s21_state import set_preference,get_preference,state_roundtrip

class PreferenceToolContracts(unittest.TestCase):
    def test_state_tools_set_read_and_reject_invalid_selection(self):
        context=SimpleNamespace(state=State({},{})) # explicit context fixture, actual SDK State
        self.assertIsNone(get_preference(context)['selected_sku'])
        self.assertTrue(set_preference('ECA-KEY-01','collection',context)['ok'])
        self.assertEqual(get_preference(context),{'selected_sku':'ECA-KEY-01','delivery_preference':'collection'})
        self.assertFalse(set_preference('ECA-KEY-99','collection',context)['ok'])
        self.assertFalse(set_preference('ECA-KEY-01','invented',context)['ok'])
        self.assertEqual(get_preference(context)['delivery_preference'],'collection')

class DurableStateContracts(unittest.IsolatedAsyncioTestCase):
    async def test_two_sessions_do_not_share_preference(self):
        with tempfile.TemporaryDirectory() as directory:
            database=Path(directory)/'sessions.db'
            first=await state_roundtrip(database,'shopping-a',preference=('ECA-KEY-01','collection'))
            second=await state_roundtrip(database,'shopping-b')
            self.assertEqual(first['state']['selected_sku'],'ECA-KEY-01')
            self.assertNotIn('selected_sku',second['state'])
            reread=await state_roundtrip(database,'shopping-a')
            self.assertEqual(reread['state']['delivery_preference'],'collection')
    async def test_actual_separate_process_restart_uses_same_database(self):
        with tempfile.TemporaryDirectory() as directory:
            database=Path(directory)/'sessions.db'
            repo=Path(__file__).resolve().parents[1]
            command=[sys.executable,'-m','examples.s21_state','--database',str(database),'--session','restart-a']
            write=await asyncio.to_thread(subprocess.run,[*command,'--write'],cwd=repo,capture_output=True,text=True,timeout=30)
            self.assertEqual(write.returncode,0,write.stderr)
            read=await asyncio.to_thread(subprocess.run,command,cwd=repo,capture_output=True,text=True,timeout=30)
            self.assertEqual(read.returncode,0,read.stderr)
            self.assertEqual(json.loads(read.stdout)['state']['selected_sku'],'ECA-KEY-01')
            self.assertEqual(json.loads(read.stdout)['state']['delivery_preference'],'collection')

if __name__=='__main__':unittest.main()
