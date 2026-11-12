"""Opt-in genuine Gradio/Playwright UI integration, not a native model evaluation.

Central QA must set ECA_RUN_S20_UI=1 and ECA_CHROMIUM_EXECUTABLE to an
explicit installed Chromium executable. No browser, server or model is launched
when this module is imported or the test is skipped. The app's FixturePlanner is
explicitly visible and deterministic; only browser/tool observations are real.

Optional ECA_S20_UI_EVIDENCE_DIR retains synthetic UI PNGs, exact owned output
bytes and a receipt. No recovery secret, authenticated data or database is copied.
"""
import base64
import hashlib
import json
import os
from pathlib import Path
import secrets
import socket
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
from urllib.parse import urlparse


PROJECT = Path(__file__).resolve().parents[1] / 'projects' / '06-browser-sidekick'


@unittest.skipUnless(os.environ.get('ECA_RUN_S20_UI') == '1',
                     'Central QA must explicitly enable real Gradio browser integration')
class RealGradioSidekickIntegration(unittest.TestCase):
    def test_actual_ui_revision_approval_outputs_and_session_isolation(self):
        executable = os.environ.get('ECA_CHROMIUM_EXECUTABLE')
        self.assertTrue(executable, 'Explicit ECA_CHROMIUM_EXECUTABLE is required')
        self.assertTrue(Path(executable).is_file(), 'Configured Chromium executable must exist')
        self.assertTrue(os.access(executable, os.X_OK), 'Configured Chromium must be executable')

        # Sole project modules use intentional local imports. Restore sys.path.
        with patch.object(sys, 'path', [str(PROJECT), *sys.path]), patch.dict(
                os.environ, {'GRADIO_ANALYTICS_ENABLED': 'False',
                             'LANGSMITH_TRACING': 'false', 'LANGCHAIN_TRACING_V2': 'false'}):
            from advanced import SessionController
            from pipeline import FixturePlanner, SidekickApplication
            from sandbox_server import Sandbox
            from ui_gradio import build_ui
            from playwright.sync_api import sync_playwright, expect

            with tempfile.TemporaryDirectory(prefix='academy-s20-ui-') as temporary, Sandbox() as sandbox:
                root = Path(temporary)
                app = SidekickApplication(root/'tasks.sqlite', root/'workspaces', sandbox,
                                          planner=FixturePlanner(), executable_path=executable)
                with socket.socket() as candidate:
                    candidate.bind(('127.0.0.1', 0))
                    port = candidate.getsockname()[1]
                origin = 'http://127.0.0.1:' + str(port)
                demo = build_ui(root/'tasks.sqlite', sandbox, application=app)
                # API stays open for a deliberate browser-session authorization
                # negative test; production callbacks themselves remain unchanged.
                demo.queue(default_concurrency_limit=1, api_open=True)
                try:
                    demo.launch(server_name='127.0.0.1', server_port=port,
                                share=False, prevent_thread_lock=True, quiet=True,
                                strict_cors=True, show_error=True)
                    with sync_playwright() as playwright:
                        browser = playwright.chromium.launch(headless=True, executable_path=executable)
                        try:
                            context = browser.new_context(service_workers='block', accept_downloads=False)
                            foreign = browser.new_context(service_workers='block', accept_downloads=False)
                            allowed = {urlparse(origin).netloc, urlparse(sandbox.origin).netloc}
                            blocked = []

                            def route(request_route):
                                parsed = urlparse(request_route.request.url)
                                if parsed.scheme in {'data', 'blob'}:
                                    return request_route.continue_()
                                if parsed.scheme == 'http' and parsed.netloc in allowed:
                                    return request_route.continue_()
                                blocked.append(parsed.scheme + '://' + parsed.netloc)
                                return request_route.abort()

                            context.route('**/*', route)
                            foreign.route('**/*', route)
                            page, other = context.new_page(), foreign.new_page()
                            joins = {page: [], other: []}

                            def remember_join(request, owner_page):
                                if urlparse(request.url).path.endswith('/queue/join'):
                                    payload = request.post_data_json
                                    if isinstance(payload, dict):
                                        joins[owner_page].append(payload)

                            page.on('request', lambda request: remember_join(request, page))
                            other.on('request', lambda request: remember_join(request, other))
                            token = SessionController.session()
                            foreign_token = SessionController.session()

                            def enter_owner(target, secret):
                                target.goto(origin, wait_until='domcontentloaded')
                                expect(target.get_by_text('deterministic-fixture', exact=False)).to_be_visible()
                                target.get_by_text('Restore a previously owned lab session', exact=True).click()
                                target.get_by_label('Your private session recovery secret (at least 32 characters)').fill(secret)
                                target.get_by_role('button', name='Use this private session', exact=True).click()
                                # State-only recovery callbacks must settle before
                                # a create click can consume the browser's state.
                                wait_until(lambda: bool(joins[target]), target)
                                expect(target.get_by_role('button', name='Use this private session', exact=True)).to_be_enabled()

                            def wait_until(predicate, target=page, timeout=20):
                                deadline = time.monotonic() + timeout
                                while time.monotonic() < deadline:
                                    value = predicate()
                                    if value:
                                        return value
                                    target.wait_for_timeout(50)
                                self.fail('Bounded UI/application condition did not become true')

                            def owned_tasks(secret):
                                with app.control._store() as store:
                                    return [row['task'] for row in store.db.execute(
                                        'SELECT task FROM sidekick_owner WHERE owner_hash=? ORDER BY rowid',
                                        (app.control._owner(secret),))]

                            def create(target, secret, objective):
                                before = set(owned_tasks(secret))
                                target.get_by_label('Task objective').fill(objective)
                                target.get_by_role('button', name='Plan new task', exact=True).click()
                                task = wait_until(lambda: next((item for item in owned_tasks(secret)
                                                               if item not in before), None), target)
                                expect(target.locator('body')).to_contain_text(task)
                                result = app.snapshot(secret, task)
                                self.assertEqual(result['objective'], objective)
                                self.assertEqual(result['status'], 'PLANNED')
                                self.assertEqual(result['planning_receipts'][0]['kind'], 'deterministic-fixture')
                                self.assertEqual(result['planning_receipts'][0]['actual_model_calls'], 0)
                                return task

                            def advance(target, secret, task, expected_status, complete=None):
                                target.get_by_role('button', name='Advance one bounded browser/tool step', exact=True).click()
                                def changed():
                                    snap = app.snapshot(secret, task)
                                    return snap if snap['status'] == expected_status and (
                                        complete is None or snap['complete'] == complete) else None
                                result = wait_until(changed, target)
                                expect(target.locator('body')).to_contain_text(expected_status)
                                return result

                            def approve(target, secret, task, number):
                                target.get_by_role('button', name='Approve exact displayed action', exact=True).click()
                                wait_until(lambda: app.snapshot(secret, task)['steps'][number]['approved_hash'], target)

                            enter_owner(page, token)
                            task = create(page, token, 'Synthetic UI regression: research Academy workshops and save a report')
                            first = advance(page, token, task, 'RUNNING', complete=1)
                            self.assertEqual(first['observations'][0]['actual_browser'], 'playwright-chromium')
                            pending = advance(page, token, task, 'WAITING_APPROVAL', complete=1)
                            self.assertEqual(sandbox.effects, [])
                            self.assertEqual(pending['total'], 3)
                            current = pending['steps'][1]
                            proposal = json.loads(current['payload'])
                            form = json.loads(proposal['value'])
                            form['note'] = 'Synthetic Academy request edited in the real Gradio UI'
                            proposal['value'] = json.dumps(form)
                            editor = page.locator('.cm-content[contenteditable="true"]')
                            self.assertEqual(editor.count(), 1, 'Exactly one actual proposal editor is required')
                            editor.fill(json.dumps(proposal, indent=2))
                            page.get_by_role('button', name='Save edited proposal (not approval)', exact=True).click()
                            edited = wait_until(lambda: (
                                lambda row: row if row['revision'] != current['revision'] else None
                            )(app.snapshot(token, task)['steps'][1]))
                            self.assertIsNone(edited['approved_hash'])
                            self.assertIsNone(edited['approval_expires'])
                            self.assertEqual(json.loads(json.loads(edited['payload'])['value'])['note'], form['note'])
                            self.assertEqual(sandbox.effects, [])
                            # Edited payload cannot execute until its new exact
                            # revision is explicitly approved through the UI.
                            advance(page, token, task, 'WAITING_APPROVAL', complete=1)
                            self.assertEqual(sandbox.effects, [])
                            approve(page, token, task, 1)
                            advance(page, token, task, 'RUNNING', complete=2)
                            self.assertEqual(len(sandbox.effects), 1)
                            self.assertIn(form['note'], json.dumps(sandbox.effects))
                            advance(page, token, task, 'WAITING_APPROVAL', complete=2)
                            approve(page, token, task, 2)
                            final = advance(page, token, task, 'COMPLETED', complete=3)
                            self.assertEqual(final['evaluation']['decision'], 'COMPLETE')
                            self.assertEqual(final['metrics']['attributed_predicates'], 3)
                            self.assertEqual(final['metrics']['actual_model_starts'], 0)
                            self.assertEqual(len(sandbox.effects), 1)

                            captures = [item for item in final['observations'] if item.get('screenshot')]
                            self.assertEqual(len(captures), 2)
                            latest = captures[-1]
                            png = app.owned_file(token, task, latest['screenshot'], latest['screenshot_sha256']).read_bytes()
                            self.assertTrue(png.startswith(b'\x89PNG\r\n\x1a\n'))
                            image = page.get_by_alt_text('Actual owned Playwright browser viewport', exact=True)
                            expect(image).to_be_visible()
                            image_src = image.get_attribute('src')
                            self.assertTrue(image_src.startswith('data:image/png;base64,'))
                            self.assertEqual(base64.b64decode(image_src.split(',', 1)[1]), png)
                            self.assertTrue(image.evaluate('(image) => image.complete && image.naturalWidth > 0'))
                            artifact = next(item for item in final['observations'] if item.get('artifact'))
                            report = app.owned_file(token, task, artifact['artifact'], artifact['body_sha256']).read_bytes()
                            link = page.locator('a[download="report.md"]')
                            expect(link).to_be_visible()
                            self.assertEqual(base64.b64decode(link.get_attribute('href').split(',', 1)[1]), report)
                            self.assertIn(b'deterministic lab report', report)
                            self.assertTrue(artifact['source_evidence'])

                            # A genuinely separate browser context owns another
                            # server-side session, not merely a different token in
                            # a direct Python test.
                            enter_owner(other, foreign_token)
                            expect(other.locator('body')).not_to_contain_text(task)
                            self.assertEqual(owned_tasks(foreign_token), [])
                            foreign_task = create(other, foreign_token, 'Separate synthetic foreign browser task')
                            self.assertNotEqual(task, foreign_task)
                            foreign_snapshot = app.snapshot(foreign_token, foreign_task)
                            self.assertEqual(foreign_snapshot['observations'], [])
                            with self.assertRaises(PermissionError):
                                app.owned_file(foreign_token, task, artifact['artifact'], artifact['body_sha256'])
                            wait_until(lambda: len(joins[other]) >= 2, other)
                            foreign_session_hash = joins[other][-1]['session_hash']
                            config = other.request.get(origin+'/config').json()
                            select_fn = next(dependency for dependency in config['dependencies']
                                             if dependency.get('api_name') == 'select')
                            # Deliberately forge ONLY a task ID. The token input
                            # remains the foreign browser's server-owned State.
                            response = other.request.post(origin+'/gradio_api/run/select', data={
                                'data': [task, None], 'fn_index': select_fn['id'],
                                'session_hash': foreign_session_hash})
                            self.assertEqual(response.status, 500,
                                             'Foreign callback must execute authorization and fail, not 404/200')
                            self.assertNotIn('observations', response.text())
                            self.assertNotIn(base64.b64encode(report).decode(), response.text())
                            self.assertEqual(app.snapshot(token, task)['status'], 'COMPLETED')
                            expect(other.locator('body')).not_to_contain_text(task)

                            # A new task is rejected through the actual UI. It
                            # cannot produce a second external sandbox effect.
                            rejected_task = create(page, token, 'Synthetic UI rejection lifecycle task')
                            advance(page, token, rejected_task, 'RUNNING', complete=1)
                            advance(page, token, rejected_task, 'WAITING_APPROVAL', complete=1)
                            page.get_by_role('button', name='Reject', exact=True).click()
                            rejected = wait_until(lambda: (
                                lambda snap: snap if snap['status'] == 'CANCELLED' else None
                            )(app.snapshot(token, rejected_task)))
                            self.assertEqual(rejected['steps'][1]['state'], 'rejected')
                            self.assertEqual(len(sandbox.effects), 1)
                            self.assertEqual(rejected['observations'][0]['actual_browser'], 'playwright-chromium')

                            evidence_root = os.environ.get('ECA_S20_UI_EVIDENCE_DIR')
                            if evidence_root:
                                evidence = Path(evidence_root)/('s20-ui-'+secrets.token_hex(8))
                                evidence.mkdir(parents=True, mode=0o700)
                                (evidence/'owned-browser.png').write_bytes(png)
                                (evidence/'owned-report.md').write_bytes(report)
                                page.screenshot(path=str(evidence/'actual-gradio-ui.png'))
                                receipt = {
                                    'scope': 'ACTUAL_FIXTURE_MODE_GRADIO_BROWSER_CALLBACK_INTEGRATION',
                                    'native_model_execution_claimed': False,
                                    'task': task, 'rejected_task': rejected_task,
                                    'foreign_task': foreign_task, 'final_status': final['status'],
                                    'attributed_predicates': final['metrics']['attributed_predicates'],
                                    'sandbox_effects': len(sandbox.effects),
                                    'browser_version': browser.version,
                                    'png_sha256': hashlib.sha256(png).hexdigest(),
                                    'artifact_sha256': hashlib.sha256(report).hexdigest(),
                                    'foreign_callback_status': response.status,
                                    'blocked_external_browser_origins': sorted(set(blocked)),
                                    'recovery_secrets_and_database_exported': False,
                                }
                                (evidence/'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
                        finally:
                            browser.close()
                finally:
                    demo.close()


if __name__ == '__main__':
    unittest.main()
