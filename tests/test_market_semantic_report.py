"""Authored-only tests for the complete report; central QA owns execution."""
import importlib.util
from pathlib import Path
import sys
import unittest
BASE=Path(__file__).resolve().parents[1]/'projects/04-market-intelligence/advanced'
sys.path.insert(0,str(BASE))
try:
    spec=importlib.util.spec_from_file_location('eca_full_semantic_report',BASE/'full_report.py')
    report_module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=report_module;spec.loader.exec_module(report_module)
finally:sys.path.pop(0)

class CompleteResearchReportTests(unittest.TestCase):
    def test_complete_report_has_all_authored_research_dimensions(self):
        report=report_module.make_report()
        self.assertEqual(report['schema_version'],2)
        self.assertEqual(len(report['company_research']),3)
        self.assertEqual(len(report['market_research']),3)
        text=report_module.render(report)
        for company in report['company_research'].values():
            self.assertEqual(company['status'],'success')
            for document in [company['value']['business'],*company['value']['products'],*company['value']['competition']]:
                self.assertIn(document['id'],text)
                self.assertIn(report_module.escaped(document['extract']),text)
        self.assertIn('fictional',text)
        self.assertIn('software-demand-share',str(report))
        self.assertIn('hardware-component-lead-time',str(report))
    def test_changed_criteria_do_not_change_business_or_sector_facts(self):
        normal=report_module.make_report()
        changed=report_module.make_report(criteria=report_module.market.Criteria(min_growth=.2))
        self.assertEqual(normal['company_research'],changed['company_research'])
        self.assertEqual(normal['market_research'],changed['market_research'])
        self.assertNotEqual(normal['profiles'],changed['profiles'])
if __name__=='__main__':unittest.main()
