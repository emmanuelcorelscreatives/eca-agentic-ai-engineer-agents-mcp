"""Real deterministic contracts; SDK integrations are deliberately separate."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

BASE=Path(__file__).resolve().parents[1]/'projects/04-market-intelligence/learning'
sys.path.insert(0,str(BASE/'src'))
from academy_market_debate.core import FactSearch,ScopedMemory,configuration,load_facts,validate_verdict
from academy_market_debate.memory_demo import probe_memory
FACTS=BASE/'fixtures/retailer-facts.json'

class MarketLearningTests(unittest.TestCase):
    def setUp(self): self.pack=load_facts(FACTS)
    def verdict(self): return dict(decision='defer',fact_ids=['F1','F3'],rationale='One short trial limits transfer.',uncertainties=['Second-region demand unknown.'],fictional=True)
    def test_context_is_dependency_ordered(self):
        agents,tasks=configuration()
        self.assertEqual(list(tasks),['support','challenge','verdict'])
        self.assertEqual(tasks['verdict']['context'],['support','challenge'])
        self.assertEqual(set(agents),{'advocate','skeptic','reviewer'})
    def test_search_has_source_and_fixed_fact(self):
        rows=FactSearch(self.pack).search('margin')
        self.assertEqual([r['id'] for r in rows],['F2'])
        self.assertEqual(rows[0]['source'],'fictional-retailer-pack')
        self.assertIn('6 percent',rows[0]['text'])
    def test_search_empty_does_not_invent(self): self.assertEqual(FactSearch(self.pack).search('unicorn'),[])
    def test_search_validation_does_not_spend_budget(self):
        tool=FactSearch(self.pack)
        for q,n in [('',1),('x'*101,1),('margin',True),('margin',5),('margin',0)]:
            with self.assertRaises(ValueError): tool.search(q,n)
        self.assertEqual(tool.calls,0)
    def test_shared_tool_budget(self):
        tool=FactSearch(self.pack,limit=1)
        tool.search('*')
        with self.assertRaises(RuntimeError): tool.search('*')
        self.assertEqual(tool.calls,1)
    def test_memory_run_isolation(self):
        m=ScopedMemory('run1');m.put('run1','support','F1')
        with self.assertRaises(PermissionError): m.context('run2',['support'])
        with self.assertRaises(PermissionError): m.put('run2','challenge','F2')
        self.assertEqual(m.context('run1',['support']),{'support':'F1'})
    def test_memory_scope_budget_reset(self):
        m=ScopedMemory('run1',max_chars=5)
        with self.assertRaises(PermissionError): m.put('run1','personal_password','bad')
        m.put('run1','support','1234')
        with self.assertRaises(ValueError): m.put('run1','challenge','67')
        self.assertEqual(m.context('run1',['support']),{'support':'1234'})
        m.reset();self.assertEqual(m.context('run1',['support']),{})
    def test_valid_verdict(self): self.assertEqual(validate_verdict(self.verdict(),self.pack)['decision'],'defer')
    def test_rejects_unknown_duplicate_and_unsupported(self):
        for key,value in [('fact_ids',['F1','F9']),('fact_ids',['F1','F1']),('decision','full_rollout'),('fictional',False),('uncertainties',[])]:
            d=self.verdict();d[key]=value
            with self.assertRaises(ValueError): validate_verdict(d,self.pack)
    def test_memory_provider_optin_before_sdk_import(self):
        with self.assertRaises(PermissionError): probe_memory('none',{},'/unused')
    def test_cli_actual_offline_no_model_output(self):
        r=subprocess.run([sys.executable,'-m','academy_market_debate.main','--facts',str(FACTS)],env=dict(__import__('os').environ,PYTHONPATH=str(BASE/'src')),capture_output=True,text=True,check=True)
        result=json.loads(r.stdout)
        self.assertEqual(result['execution'],'offline-configuration-and-search-only')
        self.assertIsNone(result['model_output'])
        self.assertEqual(len(result['facts']),4)
    def test_twenty_lesson_materials_exist(self):
        for stage in [11,12]:
            for n in range(1,11):
                for folder in ['docs','exercises','solutions']:
                    self.assertGreater((BASE/f'{folder}/s{stage}-l{n:02d}.md').stat().st_size,120)

if __name__=='__main__': unittest.main()
