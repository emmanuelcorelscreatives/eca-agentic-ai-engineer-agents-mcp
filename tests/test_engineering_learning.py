"""Executed offline control tests; no Docker, uv or provider runtime claim."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

BASE = Path(__file__).resolve().parents[1] / 'projects/05-sandboxed-engineering/learning'
def load(name):
    spec = importlib.util.spec_from_file_location('eca_learning_' + name, BASE / (name + '.py'))
    module = importlib.util.module_from_spec(spec); sys.modules[spec.name] = module
    spec.loader.exec_module(module); return module
s = load('sandbox'); w = load('workflow')

class FileTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.root = Path(self.temp.name)
        (self.root / 'src').mkdir(); (self.root / 'tests').mkdir()
        self.tools = s.FileTools(self.root)
    def tearDown(self): self.tools.close(); self.temp.cleanup()
    def test_write_read_list(self):
        sha = self.tools.write('src/app.py', 'print(1)\n')
        self.assertEqual(self.tools.read('src/app.py'), 'print(1)\n')
        self.assertEqual(self.tools.list('src'), ['app.py'])
        self.tools.write('src/app.py', 'print(2)\n', sha)
        self.assertEqual(self.tools.read('src/app.py'), 'print(2)\n')
    def test_stale_write(self):
        self.tools.write('src/app.py', 'x')
        with self.assertRaises(ValueError): self.tools.write('src/app.py', 'y', '0' * 64)
        with self.assertRaises(FileExistsError): self.tools.write('src/app.py', 'y')
    def test_traversal(self):
        for name in ('../x', '/tmp/x', 'src/../x', 'src//x', 'src\\x', 'src/./x'):
            with self.assertRaises(ValueError): self.tools.write(name, 'x')
    def test_read_only_tests(self):
        with self.assertRaises(PermissionError): self.tools.write('tests/test_app.py', 'pass')
    def test_symlink_read_and_write(self):
        (self.root / 'src/link').symlink_to('/etc/passwd')
        with self.assertRaises(OSError): self.tools.read('src/link')
        with self.assertRaises(FileExistsError): self.tools.write('src/link', 'overwrite')
        (self.root / 'src/dir').symlink_to('/tmp')
        with self.assertRaises(OSError): self.tools.write('src/dir/escape.py', 'x')
    def test_hardlink_read(self):
        import os
        (self.root / 'src/a').write_text('x'); os.link(self.root / 'src/a', self.root / 'src/b')
        with self.assertRaises(ValueError): self.tools.read('src/b')
    def test_quota(self):
        with self.assertRaises(ValueError): self.tools.write('src/large.py', 'x' * 65537)
    def test_ancestor_symlink(self):
        (self.root / 'alias').symlink_to(self.root / 'src')
        with self.assertRaises(ValueError): s.FileTools(self.root / 'alias')

class DockerPolicyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.root = Path(self.temp.name)
        self.policy = s.Policy('python@sha256:' + '1' * 64)
    def tearDown(self): self.temp.cleanup()
    def test_policy(self):
        for kwargs in ({'seconds': 61}, {'cpus': 0}, {'pids': True}, {'memory_mb': 9999}):
            with self.assertRaises(ValueError): s.Policy(self.policy.image, **kwargs)
        with self.assertRaises(ValueError): s.Policy('python:latest')
    def test_restricted_command(self):
        argv = s.docker_command(self.policy, self.root, self.root, 'tests', 'eca-learning-' + 'a' * 32)
        for flag in ('--network=none', '--read-only', '--cap-drop=ALL', '--pull=never', '--pids-limit=64', '--log-driver=none'):
            self.assertIn(flag, argv)
        self.assertEqual(sum(x.endswith(',readonly') for x in argv), 2)
        self.assertNotIn('/var/run/docker.sock', ' '.join(argv))
    def test_command_injection(self):
        for command in ('sh', 'tests; rm -rf /', 'pip install surprise', 'uv run arbitrary.py'):
            with self.assertRaises(ValueError): s.docker_command(self.policy, self.root, self.root, command, 'eca-learning-' + 'b' * 32)
    def test_bad_owner(self):
        with self.assertRaises(ValueError): s.docker_command(self.policy, self.root, self.root, 'app', 'other-container')
    def test_uv_offline(self):
        self.assertIn('--offline', s.COMMANDS['uv-sync'])
        self.assertIn('--frozen', s.COMMANDS['uv-sync'])
        self.assertEqual(s.COMMANDS['uv-venv'][-1], '/tmp/eca-venv')

class MockLifecycleTests(unittest.TestCase):
    """Injected fake Docker processes exercise wrapper branches, not Docker itself."""
    def test_success_invalid_utf8_and_cleanup(self):
        from unittest.mock import patch
        from types import SimpleNamespace
        def popen(argv, stdout, stderr, **kwargs):
            stdout.write(b"hello\xff"); stderr.write(b"diagnostic")
            return SimpleNamespace(wait=lambda timeout: 0)
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(s.subprocess, 'Popen', side_effect=popen), patch.object(s.subprocess, 'run', return_value=SimpleNamespace(returncode=0)) as cleanup:
                receipt = s.execute(s.Policy('python@sha256:' + '2' * 64), Path(temp), Path(temp), 'tests')
        self.assertTrue(receipt['passed']); self.assertIn('\ufffd', receipt['stdout'])
        self.assertEqual(cleanup.call_args.args[0][0:3], ['docker', 'rm', '-f'])
        self.assertEqual(cleanup.call_args.args[0][-1], receipt['run_id'])
    def test_missing_runtime_is_not_success(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(s.subprocess, 'Popen', side_effect=FileNotFoundError('docker')), patch.object(s.subprocess, 'run', side_effect=FileNotFoundError('docker')):
                receipt = s.execute(s.Policy('python@sha256:' + '3' * 64), Path(temp), Path(temp), 'tests')
        self.assertFalse(receipt['passed']); self.assertFalse(receipt['cleanup_confirmed'])
        self.assertIn('FileNotFoundError', receipt['infrastructure_error'])
    def test_timeout_retains_failure_and_removes_only_owner(self):
        from unittest.mock import patch
        from types import SimpleNamespace
        import subprocess
        fake = SimpleNamespace(pid=12345)
        responses = iter([subprocess.TimeoutExpired('docker', 1), 0])
        def wait(timeout):
            value = next(responses)
            if isinstance(value, Exception): raise value
            return value
        fake.wait = wait
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(s.subprocess, 'Popen', return_value=fake), patch.object(s.subprocess, 'run', return_value=SimpleNamespace(returncode=0)), patch.object(s.os, 'killpg') as kill:
                receipt = s.execute(s.Policy('python@sha256:' + '4' * 64), Path(temp), Path(temp), 'tests')
        self.assertTrue(receipt['timed_out']); self.assertFalse(receipt['passed'])
        kill.assert_called_once()

class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.req = dict(revision=1, stories=['As a learner I total expenses'], criteria={'R1': 'Empty input returns zero', 'R2': '125 + 275 gives 400'})
        self.arch = dict(requirements_sha256=w.digest(self.req), modules=[dict(path='src/expense_app.py', interface='total_expenses(amounts)', requirements=['R1','R2'])], dependencies=[])
    def test_contracts(self):
        self.assertEqual(w.requirements(self.req), self.req)
        self.assertEqual(w.architecture(self.arch, self.req), self.arch)
    def test_unknown_reference(self):
        self.arch['modules'][0]['requirements'] = ['R99']
        with self.assertRaises(ValueError): w.architecture(self.arch, self.req)
    def test_dependency_rejected(self):
        self.arch['dependencies'] = ['unreviewed']
        with self.assertRaises(ValueError): w.architecture(self.arch, self.req)
    def test_stale_architecture(self):
        self.req['revision'] = 2
        with self.assertRaises(ValueError): w.architecture(self.arch, self.req)
    def test_handoff(self):
        envelope = w.Envelope(1, 'product_manager', 1, self.req, w.digest(self.req), 'offline-human-reference')
        self.assertEqual(envelope.validate('product_manager', 1), self.req)
        with self.assertRaises(ValueError): envelope.validate('architect', 1)
        with self.assertRaises(ValueError): envelope.validate('product_manager', 2)
        self.req['revision'] = 3
        with self.assertRaises(ValueError): envelope.validate('product_manager', 1)
    def test_tasks(self):
        graph = {'product_manager': [], 'architect': ['product_manager'], 'developer': ['architect'], 'quality_assurance': ['developer']}
        self.assertEqual(w.task_order(graph), list(graph))
        self.assertFalse(w.dispatchable('developer', graph, {'architect':'failed'}, {}))
        with self.assertRaises(ValueError): w.task_order({'x':['missing']})
        with self.assertRaises(ValueError): w.task_order({'x':['y'], 'y':['x']})
    def test_actual_arithmetic_failure_and_repair(self):
        result = w.bounded_repair({'src/operator.py':'first', 'tests/fixed.txt':'unchanged'}, ['sum'],
            lambda source, patch: {**source, 'src/operator.py':patch},
            lambda source: w.expense_fixture(source['src/operator.py']))
        self.assertTrue(result['passed']); self.assertEqual(len(result['trace']), 2)
        self.assertFalse(result['trace'][0]['receipt']['passed'])
        self.assertTrue(result['trace'][1]['receipt']['passed'])
        self.assertEqual(result['trace'][0]['receipt']['evidence']['cases'][-1]['observed'], 125)
    def test_budget_exhausted(self):
        result = w.bounded_repair({'src/operator.py':'first'}, [], lambda source, patch: source,
            lambda source: w.expense_fixture(source['src/operator.py']), maximum=0)
        self.assertFalse(result['passed']); self.assertEqual(len(result['trace']), 1)
    def test_repeated_patch_stops(self):
        result = w.bounded_repair({'src/operator.py':'first'}, ['first'], lambda source, patch: source,
            lambda source: w.expense_fixture('first'))
        self.assertEqual(result['reason'], 'repeated unchanged repair')
    def test_test_weakening_denied(self):
        with self.assertRaises(ValueError):
            w.bounded_repair({'tests/fixed.txt':'fixed'}, ['x'], lambda source, patch: {'tests/fixed.txt':'weakened'}, lambda source:w.expense_fixture('first'))
    def test_fake_success_denied(self):
        with self.assertRaises(ValueError):
            w.bounded_repair({'src/operator.py':'first'}, [], lambda source, patch:source,
                lambda source:{'passed': True, 'execution':'model-says-passed', 'evidence':{}})

if __name__ == '__main__': unittest.main()
