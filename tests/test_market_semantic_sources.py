"""Authored semantic tests. Central QA must execute; no pass is asserted here."""
from dataclasses import replace
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
BASE=Path(__file__).resolve().parents[1]/'projects/04-market-intelligence'
spec=importlib.util.spec_from_file_location('eca_semantic_research_sources',BASE/'advanced/sources.py')
sources=importlib.util.module_from_spec(spec);sys.modules[spec.name]=sources;spec.loader.exec_module(sources)

class ResearchSourceSemanticTests(unittest.TestCase):
    def setUp(self):self.path=BASE/'advanced/research_sources.json'
    def modified(self,change):
        data=json.loads(self.path.read_text());change(data)
        temporary=tempfile.TemporaryDirectory();self.addCleanup(temporary.cleanup)
        path=Path(temporary.name)/'research.json';path.write_text(json.dumps(data))
        return sources.FixtureResearchAdapter(path)
    def test_all_three_business_product_competition_profiles_are_sourced(self):
        adapter=sources.FixtureResearchAdapter(self.path)
        for symbol in ('CEDAR-DEMO','MAPLE-DEMO','PINE-DEMO'):
            result=adapter.company(symbol);self.assertEqual(result.status,'success')
            company=result.value
            self.assertIn('fictional',company.business.extract.lower())
            self.assertTrue(company.products);self.assertTrue(company.competition)
            self.assertTrue(company.fictional)
            for doc in (company.business,*company.products,*company.competition):
                self.assertEqual(doc.subject,symbol)
                self.assertEqual(doc.date,company.scenario_date)
                self.assertTrue(doc.extract);self.assertTrue(doc.id)
    def test_substantive_dated_market_conditions_and_actual_signal_arithmetic(self):
        adapter=sources.FixtureResearchAdapter(self.path)
        software=adapter.market('software').value
        self.assertEqual(software.scenario_date,'2026-01-01')
        self.assertEqual(software.signals[0].value,24/40)
        self.assertAlmostEqual(software.signals[1].value,(108-100)/100)
        hardware=adapter.market('hardware').value
        self.assertEqual(hardware.signals[0].direction,'decrease')
        self.assertAlmostEqual(hardware.signals[0].value,(95-100)/100)
        self.assertEqual(hardware.signals[1].unit,'weeks')
        self.assertEqual(adapter.market('services').value.signals[0].value,.15)
        for sector in ('software','hardware','services'):
            research=adapter.market(sector).value
            self.assertTrue(research.conditions);self.assertTrue(research.uncertainties)
            self.assertTrue(research.fictional)
    def test_absent_and_error_are_distinct_not_zero_observations(self):
        adapter=sources.FixtureResearchAdapter(self.path)
        self.assertEqual(adapter.company('NO-SUCH-COMPANY').status,'absent')
        self.assertEqual(adapter.market('absent-sector').status,'absent')
        missing=sources.FixtureResearchAdapter(BASE/'does-not-exist.json')
        self.assertEqual(missing.market('software').status,'error')
        self.assertEqual(missing.market('software').reason,'source-unavailable')
        self.assertIsNone(adapter.market('absent-sector').value)
    def test_typed_result_rejects_contradictory_status_payload(self):
        for args in [('success',None,None),('error',123,'failure'),('absent',None,None)]:
            with self.assertRaises(ValueError):sources.Result(*args)
    def test_wire_json_round_trip_preserves_exact_reference_equality(self):
        adapter=sources.FixtureResearchAdapter(self.path)
        for result in (adapter.company('CEDAR-DEMO'),adapter.market('software')):
            wire=result.json()
            self.assertEqual(json.loads(json.dumps(wire)),wire)
            if 'products' in wire['value']:self.assertIsInstance(wire['value']['products'],list)
    def test_wrong_company_citation_and_wrong_date_are_rejected(self):
        def wrong_company(data):data['companies'][0]['business']='maple.business'
        def wrong_date(data):data['documents'][0]['date']='2025-01-01'
        for change in (wrong_company,wrong_date):
            adapter=self.modified(change)
            self.assertEqual(adapter.company('CEDAR-DEMO').status,'error')
    def test_bad_signal_arithmetic_direction_and_unknown_evidence_are_rejected(self):
        changes=[lambda d:d['sectors'][0]['signals'][0].update(value=.9),
                 lambda d:d['sectors'][1]['signals'][0].update(direction='increase'),
                 lambda d:d['sectors'][0]['signals'][0].update(evidence='missing')]
        for change in changes:
            self.assertEqual(self.modified(change).market('software').status,'error')
    def test_malformed_source_and_duplicate_identifiers_fail_closed(self):
        for change in [lambda d:d['documents'].append(d['documents'][0]),
                       lambda d:d['companies'].append(d['companies'][0]),
                       lambda d:d.update(fictional=False),
                       lambda d:d.update(scenario_date='not-a-date')]:
            self.assertEqual(self.modified(change).company('CEDAR-DEMO').status,'error')
    def test_source_is_pinned_to_loaded_bytes_and_swappable_protocol(self):
        temporary=tempfile.TemporaryDirectory();self.addCleanup(temporary.cleanup)
        path=Path(temporary.name)/'research.json';path.write_bytes(self.path.read_bytes())
        pinned=sources.FixtureResearchAdapter(path);original_sha=pinned.source_sha256
        path.write_text('{}')
        self.assertEqual(pinned.company('CEDAR-DEMO').status,'success')
        self.assertEqual(pinned.source_sha256,original_sha)
        self.assertEqual(sources.FixtureResearchAdapter(path).company('CEDAR-DEMO').status,'error')
        class UnavailableResearch:
            source_sha256='fixture-unavailable-for-test'
            def company(self,symbol):return sources.Result('absent',reason='not-covered')
            def market(self,sector):return sources.Result('error',reason='test-provider-unavailable')
        class Identity:
            symbol='CEDAR-DEMO';sector='software'
        snapshot=sources.research_snapshot(UnavailableResearch(),[Identity()])
        self.assertEqual(snapshot['companies']['CEDAR-DEMO']['status'],'absent')
        self.assertEqual(snapshot['markets']['software']['status'],'error')
        self.assertEqual(snapshot['source_sha256'],'fixture-unavailable-for-test')
    def test_quota_error_is_structured(self):
        temporary=tempfile.TemporaryDirectory();self.addCleanup(temporary.cleanup)
        path=Path(temporary.name)/'large.json';path.write_bytes(b' '*256001)
        self.assertEqual(sources.FixtureResearchAdapter(path).company('CEDAR-DEMO').status,'error')
if __name__=='__main__':unittest.main()
