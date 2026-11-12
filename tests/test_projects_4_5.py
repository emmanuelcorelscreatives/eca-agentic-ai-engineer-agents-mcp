import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module
market = load('eca_market', 'projects/04-market-intelligence/market.py')
team = load('eca_engineering', 'projects/05-sandboxed-engineering/team.py')

# Optional adapters can be imported without CrewAI or provider initialization.
sys.path.insert(0,str(ROOT/'projects/04-market-intelligence'))
market_adapter=load('eca_market_live','projects/04-market-intelligence/crewai_adapter.py')
sys.path.pop(0)
sys.path.insert(0,str(ROOT/'projects/05-sandboxed-engineering'))
engineering_adapter=load('eca_engineering_live','projects/05-sandboxed-engineering/crewai_adapter.py')
sys.path.pop(0)

class AdapterTests(unittest.TestCase):
    def test_market_model_cannot_change_score(self):
        ref={'profiles':[{'score':3}]}
        self.assertEqual(market_adapter.validate_output({'fictional':True,'profiles':[{'score':3}]},ref)['fictional'],True)
        with self.assertRaises(ValueError):market_adapter.validate_output({'fictional':True,'profiles':[{'score':2}]},ref)
    def test_generated_bundle_cannot_install_or_escape(self):
        self.assertEqual(engineering_adapter.validate_files(dict(team.FILES)),team.FILES)
        for name,content in [('requirements.txt','some-package'),('../escape.py','pass')]:
            files=dict(team.FILES);files[name]=content
            with self.assertRaises(ValueError):engineering_adapter.validate_files(files)
    def test_docker_image_cannot_supply_options_or_fake_digest(self):
        with tempfile.TemporaryDirectory() as temp:
            for image in ['python@sha256:fake','--privileged@sha256:'+'a'*64,'python:latest']:
                with self.assertRaises(ValueError): engineering_adapter.docker_qa(Path(temp),image)
    def test_generated_syntax_is_checked_without_execution(self):
        files=dict(team.FILES);files['expense_app.py']='raise RuntimeError("not executed")\ndef total_expenses(amounts):return 0'
        engineering_adapter.validate_files(files)

class MarketTests(unittest.TestCase):
    def report(self):
        return market.run(market.FixtureSource(ROOT/'projects/04-market-intelligence/companies.json'), market.Criteria())
    def test_rankings_and_supported_scores(self):
        report = self.report()
        self.assertEqual([(p['symbol'],p['score']) for p in report['profiles']],
            [('CEDAR-DEMO',3),('PINE-DEMO',2),('MAPLE-DEMO',1)])
        self.assertEqual(report['quality']['unsupported_metric_count'],1)
    def test_missing_evidence_never_earns_credit(self):
        c = market.Company('X','X fictional','software',.8,.8,.1,{},[])
        result = market.screen(c,market.Criteria())
        self.assertEqual(result['score'],0)
        self.assertEqual(len(result['uncertainties']),3)
    def test_criteria_change_not_data_change(self):
        source = market.FixtureSource(ROOT/'projects/04-market-intelligence/companies.json')
        before = source.companies()
        result = market.run(source,market.Criteria(min_growth=.2))
        self.assertEqual([p['score'] for p in result['profiles']],[2,2,1])
        self.assertEqual(before,source.companies())
    def test_invalid_metrics_and_thresholds(self):
        for value in [float('nan'),float('inf'),-1,2]:
            with self.assertRaises(ValueError): market.Criteria(min_growth=value)
        with self.assertRaises(ValueError):
            market.Company('X','X','X',float('nan'),.2,.2,{},[])
    def test_every_fixture_metric_reproduced_from_ledger(self):
        ledger=json.loads((ROOT/'projects/04-market-intelligence/synthetic-ledger.json').read_text())
        companies=market.FixtureSource(ROOT/'projects/04-market-intelligence/companies.json').companies()
        for company in companies:
            key=company.symbol.split('-')[0].lower()
            row=ledger['records'][key]
            self.assertAlmostEqual(company.growth,(row['current_revenue']-row['prior_revenue'])/row['prior_revenue'])
            self.assertAlmostEqual(company.debt_ratio,row['debt']/row['assets'])
            if row['operating_profit'] is None: self.assertIsNone(company.margin)
            else: self.assertAlmostEqual(company.margin,row['operating_profit']/row['current_revenue'])
    def test_fictional_label_required(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'data.json'; path.write_text(json.dumps({'companies':[]}))
            with self.assertRaises(ValueError): market.FixtureSource(path).companies()

class EngineeringTests(unittest.TestCase):
    def test_real_tests_and_package(self):
        with tempfile.TemporaryDirectory() as temp:
            destination=Path(temp)/'delivery.zip'
            result=team.run(team.Specification(),destination)
            self.assertTrue(result['qa']['passed'])
            self.assertIn('Ran 6 tests',result['qa']['stderr'])
            with zipfile.ZipFile(destination) as archive:
                self.assertIsNone(archive.testzip())
                self.assertEqual(set(archive.namelist()), set(team.FILES)|{'delivery-plan.json'})
    def test_traversal_absolute_and_symlinks_blocked(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            for name in ['../escape','/tmp/escape','folder/../../escape']:
                with self.assertRaises(ValueError): team.safe_path(root,name)
            (root/'link').symlink_to(root, target_is_directory=True)
            with self.assertRaises(ValueError): team.safe_path(root,'link/x')
    def test_unreviewed_code_not_executed(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); team.build(root,team.Specification())
            (root/'expense_app.py').write_text('raise RuntimeError("must never execute")')
            with self.assertRaises(ValueError): team.test(root)
    def test_extra_content_and_invalid_timeout_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); team.build(root,team.Specification())
            with self.assertRaises(ValueError): team.test(root,timeout=61)
            (root/'injected.py').write_text('')
            with self.assertRaises(ValueError): team.test(root)
    def test_symlink_delivery_plan_not_packaged(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)/'work';root.mkdir();team.build(root,team.Specification())
            (root/'delivery-plan.json').unlink()
            (root/'delivery-plan.json').symlink_to(Path(temp)/'outside.json')
            with self.assertRaises(ValueError): team.package(root,Path(temp)/'archive.zip')
    def test_unsupported_specification(self):
        with self.assertRaises(ValueError): team.Specification(feature='execute_user_code')
    def test_existing_package_not_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)/'work'; root.mkdir(); team.build(root,team.Specification())
            dest=Path(temp)/'source.zip';dest.write_bytes(b'original')
            with self.assertRaises(FileExistsError): team.package(root,dest)
            self.assertEqual(dest.read_bytes(),b'original')

if __name__=='__main__': unittest.main()
