"""Local HTTP fixture and recording-adapter checks; no browser or provider calls."""
import contextlib
import hashlib
import json
import os
from pathlib import Path
import socket
import sqlite3
import subprocess
import sys
import tempfile
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen


PROJECT = Path(__file__).resolve().parents[1] / 'projects' / '06-browser-sidekick'

with patch.object(sys, 'path', [str(PROJECT), *sys.path]):
    from advanced import SessionController, fixture_plan
    from pipeline import SidekickApplication
    from sandbox_server import ApprovedSandboxExecutor, Sandbox
    from sidekick import PlaywrightBrowser, Step


class PersistentSandboxTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='academy-student-06-')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.database = self.root / 'tasks.sqlite'
        self.token = SessionController.session()

    def application(self, sandbox, planner=None):
        return SidekickApplication(self.database, self.root / 'files', sandbox, planner)

    def test_pending_task_continues_in_a_separate_process_on_the_same_origin(self):
        script = '''
import json
from pathlib import Path
import sys
sys.path.insert(0, sys.argv[1])
from advanced import SessionController, fixture_plan
from sandbox_server import ApprovedSandboxExecutor, Sandbox
database = Path(sys.argv[2])
phase = sys.argv[3]
token = 'isolated-synthetic-course-owner-' + 'x' * 32
with Sandbox(database) as sandbox:
    control = SessionController(database)
    if phase == 'create':
        task = control.create(token, fixture_plan('Read synthetic catalog', sandbox.origin))
        print(json.dumps({'origin': sandbox.origin, 'state': control.snapshot(token, task)['steps'][0]['state']}))
    else:
        with control._store() as store:
            task = store.db.execute('SELECT task FROM sidekick_owner').fetchone()[0]
        state = control.advance(token, task, lambda store, task_id, origin: ApprovedSandboxExecutor(store, task_id, origin, sandbox.secret))
        print(json.dumps({'origin': sandbox.origin, 'state': state, 'result': control.snapshot(token, task)['steps'][0]['result']}))
'''
        environment = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
        results = []
        for phase in ('create', 'resume'):
            process = subprocess.run([sys.executable, '-c', script, str(PROJECT), str(self.database), phase],
                                     capture_output=True, text=True, timeout=15, env=environment)
            self.assertEqual(0, process.returncode, process.stderr)
            results.append(json.loads(process.stdout))
        self.assertEqual(results[0]['origin'], results[1]['origin'])
        self.assertEqual('pending', results[0]['state'])
        self.assertEqual('step_complete', results[1]['state'])
        self.assertIn('Python: $40; SQL: $35', results[1]['result'])

    def test_reopened_application_dispatches_only_to_its_persisted_sandbox(self):
        with Sandbox(self.database) as original:
            app = self.application(original)
            task = app.create_from_plan(self.token, fixture_plan('Read synthetic catalog', original.origin),
                                        {'kind': 'explicit-recording-adapter-fixture'})
            origin = original.origin
        with Sandbox(self.database) as restarted:
            app = self.application(restarted)
            dispatched = []

            def executor(store, task_id, target_origin, secret, workspace, record, executable):
                self.assertEqual(restarted.origin, target_origin)
                dispatched.append(target_origin)
                return ApprovedSandboxExecutor(store, task_id, target_origin, secret)

            with patch('pipeline.PlaywrightSandboxExecutor', side_effect=executor):
                app.advance(self.token, task)
            self.assertEqual([origin], dispatched)
            self.assertEqual('complete', app.snapshot(self.token, task)['steps'][0]['state'])

    def test_private_identity_and_synthetic_idempotency_receipts_survive_restart(self):
        payload = {'workshop': 'Python', 'note': 'Synthetic restart fixture'}
        key = hashlib.sha256(b'isolated-course-restart-test').hexdigest()

        def submit(sandbox, body):
            request = Request(sandbox.origin + '/submit', json.dumps(body).encode(), headers={
                'Content-Type': 'application/json', 'X-Academy-Authorization': sandbox.secret,
                'Idempotency-Key': key})
            with urlopen(request, timeout=3) as response:
                return json.loads(response.read())

        with Sandbox(self.database) as original:
            origin, secret = original.origin, original.secret
            first_receipt = submit(original, payload)
            self.assertEqual(1, len(original.effects))
        with Sandbox(self.database) as restarted:
            self.assertEqual(origin, restarted.origin)
            self.assertTrue(secret == restarted.secret, 'Persisted fixture authorization identity changed')
            self.assertEqual(first_receipt, restarted.receipts[key])
            self.assertEqual(1, len(restarted.effects))
            self.assertEqual(first_receipt, submit(restarted, payload))
            self.assertEqual(1, len(restarted.effects))
            with self.assertRaises(HTTPError) as rejected:
                submit(restarted, dict(payload, note='Different synthetic payload'))
            self.assertEqual(409, rejected.exception.code)
            rejected.exception.close()
            self.assertEqual(1, len(restarted.effects))

    def test_unknown_action_is_not_dispatched_after_restart(self):
        with Sandbox(self.database) as original:
            app = self.application(original)
            task = app.create(self.token, 'Synthetic fixture objective')
            with sqlite3.connect(self.database) as database:
                database.execute("UPDATE step SET state='executing' WHERE task=? AND number=0", (task,))
        with Sandbox(self.database) as restarted:
            app = self.application(restarted)
            with patch('pipeline.PlaywrightSandboxExecutor.execute', side_effect=AssertionError('Unknown action was replayed')):
                snapshot = app.advance(self.token, task)
            self.assertEqual('UNKNOWN', snapshot['status'])
            self.assertEqual('executing', snapshot['steps'][0]['state'])
            self.assertEqual([], restarted.requests)
            self.assertEqual([], restarted.effects)

    def test_unknown_planning_intent_cannot_be_bypassed_by_restart(self):
        calls = []

        class FailingPlanner:
            mode = 'explicit-failing-fixture'

            def plan(self, objective, origin):
                calls.append(objective)
                raise TimeoutError('Synthetic unknown planning outcome; no provider invoked')

        with Sandbox(self.database) as original:
            app = self.application(original, FailingPlanner())
            with self.assertRaises(TimeoutError):
                app.create(self.token, 'Synthetic unknown planning objective')
        with Sandbox(self.database) as restarted:
            app = self.application(restarted, FailingPlanner())
            with self.assertRaisesRegex(ValueError, 'unresolved'):
                app.create(self.token, 'Synthetic unknown planning objective')
            self.assertEqual(1, len(calls))
            self.assertEqual([], restarted.requests)

    def test_pending_approval_remains_unapproved_and_owner_bound(self):
        with Sandbox(self.database) as original:
            control = SessionController(self.database)
            task = control.create(self.token, fixture_plan('Synthetic draft', original.origin, submit=True))
            factory = lambda store, task_id, origin: ApprovedSandboxExecutor(store, task_id, origin, original.secret)
            self.assertEqual('step_complete', control.advance(self.token, task, factory))
            self.assertEqual('awaiting_approval', control.advance(self.token, task, factory))
        with Sandbox(self.database) as restarted:
            control = SessionController(self.database)
            factory = lambda store, task_id, origin: ApprovedSandboxExecutor(store, task_id, origin, restarted.secret)
            self.assertEqual('awaiting_approval', control.advance(self.token, task, factory))
            with self.assertRaises(PermissionError):
                control.advance(SessionController.session(), task, factory)
            self.assertEqual([], restarted.effects)
            self.assertEqual([], restarted.requests)

    def test_expired_approval_still_blocks_dispatch_after_restart(self):
        with Sandbox(self.database) as original:
            control = SessionController(self.database)
            task = control.create(self.token, fixture_plan('Expired synthetic draft', original.origin, submit=True))
            factory = lambda store, task_id, origin: ApprovedSandboxExecutor(store, task_id, origin, original.secret)
            control.advance(self.token, task, factory)
            control.advance(self.token, task, factory)
            pending = control.snapshot(self.token, task)['steps'][1]
            control.decide(self.token, task, 1, pending['revision'], 'approve')
            with sqlite3.connect(self.database) as database:
                database.execute('UPDATE sidekick_approval SET expires=0 WHERE task=?', (task,))
        with Sandbox(self.database) as restarted:
            control = SessionController(self.database)
            factory = lambda store, task_id, origin: ApprovedSandboxExecutor(store, task_id, origin, restarted.secret)
            with self.assertRaises(PermissionError):
                control.advance(self.token, task, factory)
            self.assertEqual([], restarted.requests)
            self.assertEqual([], restarted.effects)

    def test_approved_pending_submission_continues_once_with_persisted_receipt(self):
        with Sandbox(self.database) as original:
            control = SessionController(self.database)
            task = control.create(self.token, fixture_plan('Approved synthetic draft', original.origin, submit=True))
            factory = lambda store, task_id, origin: ApprovedSandboxExecutor(store, task_id, origin, original.secret)
            control.advance(self.token, task, factory)
            control.advance(self.token, task, factory)
            pending = control.snapshot(self.token, task)['steps'][1]
            control.decide(self.token, task, 1, pending['revision'], 'approve')
            self.assertEqual([], original.effects)
        with Sandbox(self.database) as restarted:
            control = SessionController(self.database)
            factory = lambda store, task_id, origin: ApprovedSandboxExecutor(store, task_id, origin, restarted.secret)
            self.assertEqual('step_complete', control.advance(self.token, task, factory))
            self.assertEqual(1, len(restarted.effects))
            self.assertEqual('complete', control.advance(self.token, task, factory))
            self.assertEqual(1, len(restarted.effects))
        with Sandbox(self.database) as inspected:
            control = SessionController(self.database)
            executor = SimpleNamespace(execute=MagicMock(side_effect=AssertionError('Completed task was dispatched again')))
            factory = lambda *args: executor
            self.assertEqual('complete', control.advance(self.token, task, factory))
            executor.execute.assert_not_called()
            self.assertEqual(1, len(inspected.effects))
            self.assertEqual([], inspected.requests)

    def test_occupied_saved_endpoint_fails_closed_without_retargeting(self):
        with Sandbox(self.database) as original:
            origin = original.origin
            port = original.http.server_port
        with socket.socket() as blocker:
            blocker.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            blocker.bind(('127.0.0.1', port))
            blocker.listen()
            with self.assertRaises(OSError):
                Sandbox(self.database)
        with Sandbox(self.database) as restarted:
            self.assertEqual(origin, restarted.origin)

    def test_second_running_instance_cannot_replace_persisted_identity(self):
        with Sandbox(self.database) as original:
            with self.assertRaises(OSError):
                Sandbox(self.database)
            with urlopen(original.origin + '/catalog', timeout=3) as response:
                self.assertEqual(200, response.status)

    def test_legacy_tasks_are_preserved_without_silent_identity_adoption(self):
        control = SessionController(self.database)
        task = control.create(self.token, fixture_plan('Legacy synthetic read', 'http://127.0.0.1:12345'))
        before = control.snapshot(self.token, task)
        with self.assertRaisesRegex(ValueError, 'lack a persisted sandbox identity'):
            Sandbox(self.database)
        self.assertEqual(before, control.snapshot(self.token, task))
        with sqlite3.connect(self.database) as database:
            self.assertIsNone(database.execute("SELECT name FROM sqlite_master WHERE name='sidekick_sandbox'").fetchone())

    def test_legacy_unknown_planning_is_not_adopted(self):
        sandbox = SimpleNamespace(origin='http://127.0.0.1:12345', secret='synthetic-fixture-only')
        app = self.application(sandbox)
        with patch.object(app.planner, 'plan', side_effect=TimeoutError('Synthetic unknown outcome')):
            with self.assertRaises(TimeoutError):
                app.create(self.token, 'Legacy unknown planning fixture')
        with self.assertRaisesRegex(ValueError, 'lack a persisted sandbox identity'):
            Sandbox(self.database)
        with sqlite3.connect(self.database) as database:
            self.assertEqual('UNKNOWN', database.execute('SELECT state FROM sidekick_planning').fetchone()[0])

    def test_missing_identity_row_does_not_silently_adopt_existing_tasks(self):
        with Sandbox(self.database) as original:
            app = self.application(original)
            task = app.create(self.token, 'Synthetic incomplete identity fixture')
        with sqlite3.connect(self.database) as database:
            database.execute('DELETE FROM sidekick_sandbox')
        with self.assertRaisesRegex(ValueError, 'lack a persisted sandbox identity'):
            Sandbox(self.database)
        self.assertEqual('PLANNED', self.application(SimpleNamespace()).snapshot(self.token, task)['status'])


class BrowserPolicyRecordingTests(unittest.TestCase):
    def test_policy_records_allow_and_abort_without_sensitive_url_parts(self):
        """A mocked route callback, not a real Playwright/browser observation."""
        context = MagicMock()
        browser = MagicMock()
        browser.new_context.return_value = context
        page = context.new_page.return_value
        page.locator.return_value.inner_text.return_value = 'Synthetic fixture body'
        routes = []

        def navigate(*args, **kwargs):
            callback = context.route.call_args.args[1]
            for url in ('http://127.0.0.1:8765/workshops.html',
                        'http://127.0.0.1:8766/not-allowed.png?synthetic-private-field=hidden',
                        'http://private-fixture-user:do-not-log@127.0.0.1:8766/private.png'):
                route = MagicMock()
                route.request.url, route.request.method = url, 'GET'
                callback(route)
                routes.append(route)

        page.goto.side_effect = navigate

        @contextlib.contextmanager
        def playwright():
            yield SimpleNamespace(chromium=SimpleNamespace(launch=lambda **kwargs: browser))

        package = ModuleType('playwright')
        sync_api = ModuleType('playwright.sync_api')
        sync_api.sync_playwright = playwright
        with patch.dict(sys.modules, {'playwright': package, 'playwright.sync_api': sync_api}):
            reader = PlaywrightBrowser('http://127.0.0.1:8765')
            self.assertEqual('Synthetic fixture body', reader.execute(Step('extract', 'workshops.html', criterion='fixture')))
        self.assertEqual([True, False, False], [row['allowed'] for row in reader.requests])
        self.assertNotIn('synthetic-private-field', json.dumps(reader.requests))
        self.assertNotIn('private-fixture-user', json.dumps(reader.requests))
        self.assertNotIn('do-not-log', json.dumps(reader.requests))
        routes[0].continue_.assert_called_once()
        routes[1].abort.assert_called_once()
        routes[2].abort.assert_called_once()
        browser.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
