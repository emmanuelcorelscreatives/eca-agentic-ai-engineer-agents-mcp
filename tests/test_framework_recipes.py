"""Offline boundaries and real fixture behavior; not vendor/live integration certification."""
import ast
import contextlib
import importlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from frameworks.common import line_total, require_run
from frameworks.ollama_chat import request_body

class FrameworkRecipesTests(unittest.TestCase):
    def test_exact_decimal_totals(self):
        self.assertEqual(line_total('12.50', 3), '37.50')
        self.assertEqual(line_total('0.10', 3), '0.30')
        self.assertEqual(line_total('5.00', 0), '0.00')
        self.assertEqual(line_total('1000000.00', 10000), '10000000000.00')

    def test_rejects_invalid_financial_inputs(self):
        for price, quantity in [('NaN', 1), ('Infinity', 1), ('-0.01', 1), ('1.005', 1),
                                ('1000000.01', 1), ('hello', 1), ('10', True), ('10', 1.5),
                                ('10', -1), ('10', 10001), ('10', '3')]:
            with self.subTest(price=price, quantity=quantity), self.assertRaises(ValueError):
                line_total(price, quantity)

    def test_live_opt_in_required_even_with_credentials(self):
        with patch.object(sys, 'argv', ['recipe']), patch.dict('os.environ', {'COURSE_MODEL': 'fixture'}, clear=True), contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as result:
                require_run('COURSE_MODEL')
        self.assertEqual(result.exception.code, 2)

    def test_missing_config_refused_after_opt_in(self):
        with patch.object(sys, 'argv', ['recipe', '--run']), patch.dict('os.environ', {}, clear=True), contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                require_run('COURSE_MODEL')

    def test_explicit_config_preserved(self):
        with patch.object(sys, 'argv', ['recipe', '--run']), patch.dict('os.environ', {'COURSE_MODEL': 'chosen-model'}, clear=True):
            self.assertEqual(require_run('COURSE_MODEL'), {'COURSE_MODEL': 'chosen-model'})

    def test_all_python_examples_parse_and_import_without_vendor_sdk(self):
        # Imported examples must not instantiate SDK clients, make calls, or require credentials.
        for path in sorted((ROOT / 'frameworks').glob('*.py')):
            ast.parse(path.read_text(), filename=str(path))
            with patch('urllib.request.urlopen', side_effect=AssertionError('network during import')):
                importlib.import_module('frameworks.' + path.stem)

    def test_catalog_is_resolved_and_primary_sources_are_https(self):
        catalog = json.loads((ROOT / 'frameworks/catalog.json').read_text())
        self.assertEqual(len(catalog['recipes']), 13)
        for entry in catalog['recipes']:
            self.assertTrue((ROOT / 'frameworks' / entry['path']).is_file())
            self.assertTrue(entry['official_url'].startswith('https://'))
            self.assertTrue(all(1 <= stage <= 30 for stage in entry['stages']))
            if entry['requirements_key']:
                self.assertTrue((ROOT / 'frameworks/requirements' / (entry['requirements_key'] + '.txt')).is_file())

    def test_ollama_nonstreaming_fixture_and_invalid_model(self):
        self.assertFalse(request_body('local-tag:latest')['stream'])
        self.assertEqual(request_body('local-tag:latest')['model'], 'local-tag:latest')
        for bad in ['', 'with spaces', '\n', 'x' * 201]:
            with self.assertRaises(ValueError):
                request_body(bad)

    def test_graph_calculation_is_exact_without_sdk(self):
        from frameworks.langgraph_state import calculate
        self.assertEqual(calculate({'price': '12.50', 'quantity': 3}), {'total': '37.50'})

    def test_n8n_inactive_manual_workflow_has_no_external_action(self):
        workflow = json.loads((ROOT / 'frameworks/n8n/order-workflow.json').read_text())
        self.assertFalse(workflow['active'])
        self.assertEqual([n['type'] for n in workflow['nodes']], ['n8n-nodes-base.manualTrigger', 'n8n-nodes-base.code'])
        self.assertNotIn('credentials', workflow['nodes'][1])
        if not shutil.which('node'):
            self.skipTest('Node unavailable; JavaScript execution not verified')
        source = workflow['nodes'][1]['parameters']['jsCode']
        result = subprocess.run(['node', '-e', 'console.log(JSON.stringify((new Function(' + json.dumps(source) + '))()))'], capture_output=True, text=True, check=True, timeout=10)
        data = json.loads(result.stdout)[0]['json']
        self.assertEqual(data['totalCents'], 3750)
        self.assertTrue(data['fixture'])
        self.assertFalse(data['externalAction'])

if __name__ == '__main__':
    unittest.main()
