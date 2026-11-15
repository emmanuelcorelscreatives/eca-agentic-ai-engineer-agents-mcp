"""Local learner activities and documentation; no container or provider calls."""
import ast
from contextlib import ExitStack, redirect_stderr, redirect_stdout
from copy import deepcopy
import importlib
import io
import json
from pathlib import Path
import re
import sys
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / 'projects/05-sandboxed-engineering'
LEARNING = PROJECT / 'learning'


class StudentProject05Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(LEARNING))
        try:
            cls.lab = importlib.import_module('student_lab')
        finally:
            sys.path.pop(0)

    def setUp(self):
        self.guards = ExitStack()
        self.addCleanup(self.guards.close)
        for target in ('subprocess.run', 'subprocess.Popen', 'socket.socket'):
            self.guards.enter_context(patch(target, side_effect=AssertionError('No external effects allowed')))

    def test_file_activity_uses_owned_temporary_workspace_and_boundaries(self):
        result = self.lab.file_activity()
        self.assertEqual(result['content'], 'amount = 400\n')
        self.assertEqual(result['files'], ['app.py', 'link.py'])
        self.assertTrue(result['temporary_workspace_removed'])
        self.assertFalse(result['application_executed'])
        self.assertNotEqual(result['original_sha256'], result['updated_sha256'])
        self.assertEqual(result['rejected']['traversal'], 'ValueError')
        self.assertEqual(result['rejected']['absolute'], 'ValueError')
        self.assertEqual(result['rejected']['readonly_tests'], 'PermissionError')
        self.assertEqual(result['rejected']['stale_write'], 'ValueError')
        self.assertIn(result['rejected']['symlink_read'], ('OSError', 'ValueError'))

    def test_repair_keeps_failed_observation_and_unchanged_test_marker(self):
        activity = self.lab.repair_activity()
        result = activity['result']
        self.assertEqual(activity['provenance'], 'offline-functional-fixture')
        self.assertFalse(activity['application_executed'])
        self.assertFalse(activity['provider_called'])
        self.assertTrue(result['passed'])
        self.assertEqual(len(result['trace']), 2)
        first, final = (attempt['receipt'] for attempt in result['trace'])
        self.assertFalse(first['passed'])
        self.assertTrue(final['passed'])
        self.assertEqual(first['evidence']['cases'][-1]['observed'], 125)
        self.assertEqual(final['evidence']['cases'][-1]['observed'], 400)
        self.assertEqual(result['source']['tests/fixed.txt'], activity['initial_source']['tests/fixed.txt'])
        self.assertNotEqual(result['trace'][0]['source_sha256'], result['trace'][1]['source_sha256'])
        self.assertIn('no R3', activity['limits'])

    def test_handoff_uses_local_reference_not_invented_provider_evidence(self):
        activity = self.lab.handoff_activity()
        self.assertEqual(activity['provenance'], 'offline-human-reference')
        self.assertFalse(activity['provider_called'])
        self.assertEqual(set(activity['rejected']), {'changed_content', 'obsolete_revision'})
        requirements = activity['artifact']['content']
        self.assertEqual(requirements['priorities'], ['R1', 'R2', 'R3'])
        self.assertEqual(self.lab.semantic_team.validate_requirements(requirements), requirements)
        local_response = {'provenance': 'offline-human-reference', 'content': requirements}
        self.assertEqual(activity['artifact']['response_sha256'], self.lab.semantic_team.sha(local_response))
        changed = deepcopy(requirements)
        del changed['criteria']['R3']
        with self.assertRaises(ValueError):
            self.lab.semantic_team.validate_requirements(changed)

    def test_main_outputs_valid_json_for_each_documented_activity(self):
        for activity in ('files', 'repair', 'handoffs'):
            with self.subTest(activity=activity), patch.object(sys, 'argv', ['student_lab.py', activity]):
                output = io.StringIO()
                with redirect_stdout(output):
                    self.lab.main()
                self.assertIn('provenance', json.loads(output.getvalue()))

    def test_unknown_activity_is_rejected_before_file_operations(self):
        with patch.object(sys, 'argv', ['student_lab.py', 'run-shell']), redirect_stdout(io.StringIO()):
            with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                self.lab.main()

    def test_relative_markdown_links_resolve(self):
        for document in PROJECT.rglob('*.md'):
            for target in re.findall(r'\]\(([^)]+)\)', document.read_text()):
                if ':' in target or target.startswith('#'):
                    continue
                with self.subTest(document=document.name, target=target):
                    self.assertTrue((document.parent / target.split('#')[0]).exists())

    def test_detailed_integrated_verification_methods_exist(self):
        definitions = set()
        for source in (ROOT / 'tests').glob('test_engineering_*.py'):
            for node in ast.walk(ast.parse(source.read_text())):
                if isinstance(node, ast.ClassDef):
                    definitions.update(node.name + '.' + child.name for child in node.body
                                       if isinstance(child, ast.FunctionDef))
        for document in (LEARNING / 'stage-14-exercises.md', LEARNING / 'stage-15-exercises.md'):
            for reference in re.findall(r'\b([A-Z]\w*\.test_\w+)', document.read_text()):
                with self.subTest(reference=reference):
                    self.assertIn(reference, definitions)

    def test_guide_does_not_require_unavailable_private_recordings(self):
        exercises = (LEARNING / 'stage-15-exercises.md').read_text()
        self.assertNotIn('recorded first 22-test', exercises)
        self.assertNotIn('Reuse the same coherent recorded', exercises)
        self.assertIn('WORKED-EXAMPLE.md', exercises)
        guide = (LEARNING / 'CONTAINER.md').read_text()
        self.assertIn('Provider transport is not configured; no request sent', guide)
        self.assertIn('uv.lock` is already supplied', guide)
        self.assertIn('cache is **not** committed', guide)


if __name__ == '__main__':
    unittest.main()
