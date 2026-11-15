"""Static learner-document checks; no application or optional integrations run."""
import ast
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / 'projects/08-mcp-trading-floor'


class StudentProject08Tests(unittest.TestCase):
    def test_reviewer_setup_and_human_frontend_contract(self):
        readme = (PROJECT / 'README.md').read_text()
        self.assertIn('export ACADEMY_LOCAL_TOKEN=', readme)
        self.assertIn('export ACADEMY_REVIEW_TOKEN=', readme)
        self.assertIn('export ACADEMY_PAPER_DB=', readme)
        self.assertIn('X-Academy-Review-Token', readme)
        self.assertIn('npm ci', readme)
        self.assertNotIn('browser intentionally cannot approve', readme)
        architecture = (PROJECT / 'architecture.md').read_text()
        self.assertIn('/reviews', architecture)
        self.assertIn('ACADEMY_REVIEW_TOKEN', architecture)
        self.assertNotIn('Only the separately reviewed CLI can create an approval', architecture)

    def test_nine_research_tools_match_documentation(self):
        tree = ast.parse((PROJECT / 'mcp_server.py').read_text())
        tools = [node.name for node in tree.body
                 if isinstance(node, ast.FunctionDef)
                 and any(isinstance(decorator, ast.Call)
                         and isinstance(decorator.func, ast.Attribute)
                         and isinstance(decorator.func.value, ast.Name)
                         and decorator.func.value.id == 'mcp'
                         and decorator.func.attr == 'tool'
                         for decorator in node.decorator_list)]
        self.assertEqual(len(tools), 9)
        self.assertNotIn('approve', tools)
        self.assertNotIn('execute', tools)
        for filename in ['README.md', 'architecture.md']:
            text = (PROJECT / filename).read_text()
            self.assertIn('nine', text)
            self.assertNotRegex(text, r'\beight\b[^.\n]*\btools?\b')

    def test_workbook_paths_resolve_without_planned_test_tree(self):
        workbook = (PROJECT / 'workbook-stages26-30.md').read_text()
        self.assertNotRegex(workbook, r'projects/08-mcp-trading-floor/stage(?:27|29)/')
        paths = set(re.findall(r'(?:projects|tests)/[A-Za-z0-9_./-]+\.py', workbook))
        self.assertTrue(paths)
        for path in paths:
            with self.subTest(path=path):
                self.assertTrue((ROOT / path).is_file())
        self.assertIn('optional integration skips remain skips', workbook)

    def test_solution_pointers_keep_distinct_boundaries(self):
        workbook = (PROJECT / 'workbook-stages26-30.md').read_text()
        approval = workbook.split('## s27-l13', 1)[1].split('## s28-l01', 1)[0]
        self.assertIn('agent_harness.py', approval)
        self.assertIn('mcp_lab/worked-host-solutions.md', approval)
        self.assertNotIn('approve_order.py', approval)
        feedback = workbook.split('## s30-l06', 1)[1].split('## s30-l07', 1)[0]
        self.assertIn('evaluation_lab/feedback.py', feedback)
        self.assertIn('BoundFeedbackStore', feedback)
        self.assertIn('frontend/src/main.jsx', feedback)

    def test_solution_navigation_and_internal_receipts(self):
        readme = (PROJECT / 'README.md').read_text()
        for target in ['workbook-stages26-30.md', 'solutions/trading-workflows.md',
                       'mcp_lab/worked-host-solutions.md', 'evaluation_lab/WORKED-SOLUTIONS.md']:
            self.assertIn('](' + target + ')', readme)
            self.assertTrue((PROJECT / target).is_file())
        for target in ['resource-map.json', 'evaluation_lab/authoring-command-manifest-v2.json',
                       'mcp_lab/inspector/source-preparation.json',
                       'retrieval_lab/semantic-repair-source-status.json',
                       'retrieval_lab/semantic-repair-files.sha256']:
            self.assertFalse((PROJECT / target).exists(), target)
        self.assertNotIn('ready for render', readme)
        self.assertNotIn('designated QA owner', (PROJECT / 'mcp_lab/worked-host-solutions.md').read_text())


if __name__ == '__main__':
    unittest.main()
