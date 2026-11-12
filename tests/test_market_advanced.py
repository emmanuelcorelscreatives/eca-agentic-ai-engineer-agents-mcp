from dataclasses import replace
import importlib.util
from pathlib import Path
import sys
import unittest
BASE=Path(__file__).resolve().parents[1]/'projects/04-market-intelligence'
spec=importlib.util.spec_from_file_location('eca_market_research_lab',BASE/'advanced/research_lab.py')
lab=importlib.util.module_from_spec(spec);sys.modules[spec.name]=lab;spec.loader.exec_module(lab)
class AdvancedMarketTests(unittest.TestCase):
    def setUp(self):
        self.source=lab.market.FixtureSource(BASE/'companies.json')
        self.reference=lab.market.run(self.source,lab.market.Criteria())
    def test_all_metrics_reconcile_against_real_fixture_ledger(self):
        self.assertEqual(lab.review_numeric_claims(self.source.companies(),lab.evidence_registry()),[])
    def test_injected_number_and_wrong_company_evidence_fail(self):
        rows=self.source.companies();rows[0]=replace(rows[0],growth=.9)
        self.assertTrue(lab.review_numeric_claims(rows,lab.evidence_registry()))
        rows=self.source.companies();rows[0]=replace(rows[0],evidence={**rows[0].evidence,'growth':'synthetic-ledger/pine/revenue-year-comparison'})
        self.assertTrue(lab.review_numeric_claims(rows,lab.evidence_registry()))
    def test_explicit_units_missing_zero_nonfinite(self):
        self.assertEqual(lab.fraction(25,'percent'),.25)
        self.assertEqual(lab.fraction(.25,'fraction'),.25)
        for a,b in [(None,2),(1,0),(float('nan'),2),(True,3)]:
            with self.assertRaises(ValueError):lab.ratio(a,b)
        with self.assertRaises(ValueError):lab.fraction(25,'unknown')
    def test_missing_and_zero_distinct(self):
        company=self.source.companies()[2]
        self.assertIsNone(company.margin)
        self.assertFalse(lab.market.screen(company,lab.market.Criteria())['checks'][1]['supported'])
    def test_dates_and_evidence_types(self):
        with self.assertRaises(ValueError):lab.Evidence('a','2026-13-01','cedar','growth',.2)
        with self.assertRaises(ValueError):lab.Evidence('a','2026-01-01','cedar','growth',.2,fictional=False)
    def test_cache_invalidates_on_source_and_criteria(self):
        memory=lab.ResearchMemory();criteria=self.reference['criteria']
        memory.put('source-a',criteria,self.reference,self.reference)
        self.assertEqual(memory.get('source-a',criteria),self.reference)
        self.assertIsNone(memory.get('source-b',criteria))
        self.assertIsNone(memory.get('source-a',{**criteria,'min_growth':.9}))
        with self.assertRaises(ValueError):memory.put('source-a',criteria,{},self.reference)
        copy=memory.get('source-a',criteria);copy['profiles'].clear()
        self.assertEqual(len(memory.get('source-a',criteria)['profiles']),3)
    def test_profiles_markdown_retains_risks_unknowns_citations(self):
        text=lab.markdown(self.reference)
        for profile in self.reference['profiles']:
            self.assertIn(profile['symbol'],text)
            for risk in profile['risks']:self.assertIn(risk,text)
        self.assertIn('unknown',text)
        self.assertNotIn('<script>',lab.escaped('<script>|'))
    def test_quality_detects_each_seeded_defect(self):
        self.assertTrue(lab.evaluate(self.reference,self.reference)['passed'])
        invented=dict(self.reference,recommendation='Buy a real stock now')
        self.assertFalse(lab.evaluate(invented,self.reference)['passed'])
        for field in ['criteria','profiles','quality','fictional','scope','market_context']:
            wrong=dict(self.reference);wrong.pop(field)
            self.assertFalse(lab.evaluate(wrong,self.reference)['passed'])
if __name__=='__main__':unittest.main()
