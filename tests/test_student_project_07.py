"""Run the project07 student examples offline in disposable copies."""
import ast
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest


PROJECT = Path(__file__).resolve().parents[1] / 'projects' / '07-agent-factory'


class StudentProject07(unittest.TestCase):
    def run_solution(self, index):
        blocks = re.findall(r'```python\n(.*?)```', (PROJECT / 'SOLUTIONS.md').read_text(), re.S)
        self.assertEqual(len(blocks), 2)
        temporary = tempfile.TemporaryDirectory(prefix='student-project07-')
        self.addCleanup(temporary.cleanup)
        workspace = Path(temporary.name) / 'project'
        shutil.copytree(PROJECT, workspace, ignore=shutil.ignore_patterns('__pycache__', 'student-work'))
        result = subprocess.run(
            [sys.executable, '-B', '-c', blocks[index]], cwd=workspace,
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return workspace, result

    def test_catalog_solution_has_real_tests_and_cli_output(self):
        workspace, result = self.run_solution(0)
        self.assertIn('Ran 5 tests', result.stdout)
        self.assertIn('"title": "Agent Engineering"', result.stdout)
        receipt = json.loads((workspace / 'student-work/catalog-example/validation-receipt.json').read_text())
        self.assertTrue(receipt['passed'])
        self.assertEqual(receipt['kind'], 'trusted-fixed-template-tests')
        self.assertEqual(receipt['returncode'], 0)

    def test_repair_solution_preserves_real_failure_and_separate_success(self):
        workspace, result = self.run_solution(1)
        root = workspace / 'student-work/repair-example'
        failure = json.loads((root / 'failed/failure-diagnostics.json').read_text())
        self.assertEqual(failure['status'], 'failed')
        self.assertEqual(failure['error_type'], 'ValueError')
        self.assertIn('FAIL: test_word_count', failure['diagnostic'])
        self.assertFalse((root / 'failed/validation-receipt.json').exists())
        self.assertIn('return {"words": 0}', (root / 'failed/agent.py').read_text())
        receipt = json.loads((root / 'repaired/validation-receipt.json').read_text())
        self.assertEqual(receipt['returncode'], 0)
        self.assertIn('Ran 4 tests', receipt['stderr'])
        self.assertIn('repaired/agent.py', (root / 'repair.diff').read_text())
        self.assertIn('Ran 4 tests', result.stdout)
        blocks = re.findall(r'```python\n(.*?)```', (PROJECT / 'SOLUTIONS.md').read_text(), re.S)
        repeated = subprocess.run(
            [sys.executable, '-B', '-c', blocks[1]], cwd=workspace,
            capture_output=True, text=True, timeout=30,
        )
        self.assertNotEqual(repeated.returncode, 0)
        self.assertIn('FileExistsError', repeated.stderr)
        self.assertEqual(failure, json.loads((root / 'failed/failure-diagnostics.json').read_text()))

    def test_model_example_is_parseable_and_explicitly_opt_in(self):
        guide = (PROJECT / 'MODEL-PIPELINE-AUTHORING.md').read_text()
        blocks = re.findall(r'```python\n(.*?)```', guide, re.S)
        self.assertEqual(len(blocks), 1)
        ast.parse(blocks[0])
        self.assertIn("!= 'CALL'", blocks[0])
        self.assertIn('max_retries=0', blocks[0])
        self.assertIn('max_calls=1', blocks[0])
        self.assertIn('launch_performed: false', guide)
        self.assertIn('No ready-made launch callback is shipped', guide)

    def test_student_navigation_retains_correct_schema_and_filename(self):
        readme = (PROJECT / 'README.md').read_text()
        self.assertIn('cd projects/07-agent-factory', readme)
        self.assertIn('MODEL-PIPELINE-AUTHORING.md', readme)
        self.assertIn('templates/catalog_research-spec.json', readme)
        self.assertIn('instructions.json', readme)
        self.assertIn('failure diagnostics', readme)
        self.assertIn('not a security sandbox', (PROJECT / 'MODEL-PIPELINE-AUTHORING.md').read_text())
        for name in ('README.md', 'EXERCISES.md', 'SOLUTIONS.md', 'FRAMEWORKS.md', 'MODEL-PIPELINE-AUTHORING.md'):
            text = (PROJECT / name).read_text()
            for target in re.findall(r'\]\(([^)]+)\)', text):
                if target.startswith(('https://', 'http://', '#')):
                    continue
                path = target.split('#', 1)[0]
                self.assertTrue((PROJECT / path).exists(), f'{name}: {target}')

    def test_public_project_prose_is_student_facing(self):
        for name in ('MODEL-PIPELINE-AUTHORING.md', 'tests/test_s25_pipeline_semantics.py', 'tests/test_s25_docker_bridge.py'):
            text = (PROJECT / name).read_text().lower()
            for retired in ('author-only', 'central qa', 'original pdf', 'project-specific admitted helper', 'pinned repository virtual environment'):
                self.assertNotIn(retired, text)


if __name__ == '__main__':
    unittest.main()
