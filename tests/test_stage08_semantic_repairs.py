"""New Stage8 acceptance tests. Author-created; execution belongs to guarded central QA.
No external SMTP/provider is used. The SMTP server below is an actual owned loopback sink.
"""
import asyncio
from dataclasses import replace
from email import policy
from email.parser import BytesParser
import importlib.util
import json
from pathlib import Path
import socketserver
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

PROJECT = Path(__file__).resolve().parents[1] / 'projects/02-sales-team'
sys.path.insert(0, str(PROJECT))
import sales
import transport
import context_wire
import evaluations
from application import SalesApplication


def prospect():
    return sales.Prospect(**json.loads((PROJECT/'fixtures/prospect.json').read_text())['prospect'])


class SMTPHandler(socketserver.StreamRequestHandler):
    def handle(self):
        self.wfile.write(b'220 owned Academy test sink\r\n')
        while True:
            line = self.rfile.readline()
            if not line:
                break
            command = line.split(b' ', 1)[0].strip().upper()
            if command in {b'EHLO', b'HELO'}:
                self.wfile.write(b'250 owned-academy-sink\r\n')
            elif command in {b'MAIL', b'RCPT', b'RSET'}:
                self.wfile.write(b'250 OK\r\n')
            elif command == b'DATA':
                self.wfile.write(b'354 send DATA\r\n')
                chunks = []
                while True:
                    part = self.rfile.readline()
                    if part in {b'.\r\n', b'.\n', b''}:
                        break
                    chunks.append(part[1:] if part.startswith(b'..') else part)
                self.server.messages.append(b''.join(chunks))
                self.wfile.write(b'250 accepted by owned sink\r\n')
            elif command == b'QUIT':
                self.wfile.write(b'221 bye\r\n')
                break
            else:
                self.wfile.write(b'500 unsupported test command\r\n')


class OwnedSink(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


class Stage08PayloadTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.database = str(Path(self.tmp.name)/'drafts.sqlite')
        self.team = sales.SalesTeam(self.database)
        self.addCleanup(self.team.db.close)
        self.ident = self.team.create_draft(prospect())

    def test_recipient_revision_and_each_payload_field_bound(self):
        for column, value in [('recipient', 'other@example.invalid'), ('subject', 'Changed'),
                              ('body', 'Changed\n'), ('revision', 88)]:
            team = sales.SalesTeam()
            try:
                ident = team.create_draft(prospect())
                team.approve(ident, 'Local test reviewer')
                with team.db:
                    team.db.execute(f'UPDATE drafts SET {column}=? WHERE id=?', (value, ident))
                with self.assertRaises(PermissionError):
                    team.deliver(ident)
            finally:
                team.db.close()

    def test_edit_recipient_revokes_approval_and_stale_revision_rejected(self):
        shown = self.team.preview(self.ident)
        self.team.approve(self.ident, 'Local test', shown['payload_hash'])
        self.team.edit(self.ident, shown['subject'], shown['body'], 'new@example.invalid', shown['revision'])
        self.assertIsNone(self.team.draft(self.ident)['approved_hash'])
        self.assertEqual(self.team.draft(self.ident)['revision'], 2)
        with self.assertRaises(ValueError):
            self.team.edit(self.ident, 'Other', 'Other', expected_revision=1)
        with self.assertRaises(PermissionError):
            self.team.approve(self.ident, 'Local test', shown['payload_hash'])

    def test_actual_smtp_exact_received_approved_payload_and_duplicate_block(self):
        with OwnedSink(('127.0.0.1', 0), SMTPHandler) as sink:
            sink.messages = []
            thread = threading.Thread(target=sink.serve_forever, daemon=True)
            thread.start()
            try:
                configured = transport.OwnedSinkSMTP(sink.server_address[1], ownership_acknowledged=True)
                with self.assertRaises(PermissionError):
                    self.team.submit_approved(self.ident, configured)
                shown = self.team.preview(self.ident)
                self.team.approve(self.ident, 'Local test reviewer', shown['payload_hash'])
                receipt = self.team.submit_approved(self.ident, configured)
                self.assertEqual(receipt['outcome'], 'accepted_by_owned_smtp_sink')
                self.assertEqual(len(sink.messages), 1)
                message = BytesParser(policy=policy.default).parsebytes(sink.messages[0])
                self.assertEqual(str(message['To']), shown['recipient'])
                self.assertEqual(str(message['Subject']), shown['subject'])
                self.assertEqual(message.get_content().replace('\r\n', '\n'), shown['body'])
                self.assertEqual(str(message['X-Academy-Revision']), str(shown['revision']))
                self.assertEqual(transport.verify_received_payload_hash(message, shown['payload_hash']), shown['payload_hash'])
                # A long unstructured SMTP header can legitimately fold before the
                # intact token. Normalize only its surrounding protocol whitespace.
                folded = BytesParser(policy=policy.default).parsebytes(
                    b'X-Academy-Payload-SHA256:\r\n\t' + shown['payload_hash'].encode('ascii') + b'\r\n\r\n')
                self.assertEqual(transport.verify_received_payload_hash(folded, shown['payload_hash']), shown['payload_hash'])
                wrong_hex = ('0' if shown['payload_hash'][0] != '0' else '1') + shown['payload_hash'][1:]
                for bad_value in [wrong_hex, 'g' * 64, shown['payload_hash'][:20] + ' ' + shown['payload_hash'][20:]]:
                    invalid = BytesParser(policy=policy.default).parsebytes(
                        b'X-Academy-Payload-SHA256: ' + bad_value.encode('ascii') + b'\r\n\r\n')
                    with self.assertRaises(ValueError):
                        transport.verify_received_payload_hash(invalid, shown['payload_hash'])
                duplicate = BytesParser(policy=policy.default).parsebytes(
                    (f'X-Academy-Payload-SHA256: {shown["payload_hash"]}\r\n' * 2 + '\r\n').encode('ascii'))
                with self.assertRaises(ValueError):
                    transport.verify_received_payload_hash(duplicate, shown['payload_hash'])
                with self.assertRaises(PermissionError):
                    self.team.submit_approved(self.ident, configured)
                self.assertEqual(len(sink.messages), 1)
            finally:
                sink.shutdown()
                thread.join(timeout=5)
                self.assertFalse(thread.is_alive())

    def test_unknown_outcome_is_durable_and_never_replayed(self):
        configured = transport.OwnedSinkSMTP(25252, ownership_acknowledged=True)
        self.team.approve(self.ident, 'Local test reviewer')
        with patch.object(transport.OwnedSinkSMTP, 'send', side_effect=TimeoutError('unknown after DATA')) as send:
            with self.assertRaises(TimeoutError):
                self.team.submit_approved(self.ident, configured)
            self.assertEqual(send.call_count, 1)
            reopened = sales.SalesTeam(self.database)
            try:
                self.assertEqual(reopened.draft(self.ident)['status'], 'unknown_outcome')
                with self.assertRaises(PermissionError):
                    reopened.submit_approved(self.ident, configured)
                with self.assertRaises(ValueError):
                    reopened.edit(self.ident, 'Retry', 'Retry')
                self.assertEqual(send.call_count, 1)
            finally:
                reopened.db.close()

    def test_transport_refuses_external_hosts_unowned_sink_and_header_injection(self):
        for args in [dict(port=25252, host='smtp.example.com', ownership_acknowledged=True),
                     dict(port=25252), dict(port=25, ownership_acknowledged=True)]:
            with self.assertRaises(ValueError):
                transport.OwnedSinkSMTP(**args)
        with self.assertRaises(ValueError):
            replace(prospect(), email='attacker@example.invalid\r\nBcc: other@example.invalid')
        with self.assertRaises(ValueError):
            self.team.edit(self.ident, 'subject\r\nInjected: yes', 'Body')
        self.team.reject(self.ident)
        with self.assertRaises(PermissionError):
            self.team.deliver(self.ident)

    def test_typed_foreign_identity_and_known_evidence(self):
        spec = importlib.util.spec_from_file_location('stage08_models_owned', PROJECT/'models.py')
        m = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = m
        spec.loader.exec_module(m)
        p = prospect()
        c = m.Company(**json.loads((PROJECT/'fixtures/company.json').read_text()))
        finding = m.ResearchFinding(p.prospect_id, c.id, p.verified_need, (p.source_id,), ('budget',))
        strategy = m.OutreachStrategy(p.campaign_id, p.prospect_id, 'Small reporting demo', (p.source_id,))
        draft = m.EmailDraft(p.prospect_id, p.campaign_id, 'Demo', 'Practice demo', (p.source_id,))
        self.assertTrue(m.validate_identity_graph(p, c, finding, strategy, draft)['valid'])
        for bad in [replace(finding, company_id='company-foreign'), replace(finding, source_ids=('invented',))]:
            with self.assertRaises(ValueError):
                m.validate_identity_graph(p, c, bad)
        with self.assertRaises(ValueError):
            m.validate_identity_graph(p, c, finding, replace(strategy, campaign_id='foreign'))
        for value in ['bad', '', 'A <a@example.invalid>', 'a@example.invalid,b@example.invalid']:
            with self.assertRaises(ValueError):
                replace(p, email=value)

    def test_evaluation_reference_labels_and_mechanical_failure_modes(self):
        report = evaluations.evaluation_report(prospect())
        cases = {case['id']: case for case in report['cases']}
        self.assertFalse(report['model_scoring_performed'])
        invented = cases['invented-revenue-mechanical-false-positive']
        self.assertEqual(invented['reference_scores']['factual_accuracy'], 0)
        self.assertTrue(invented['mechanical']['no_selected_guarantee_phrases'])
        self.assertTrue(invented['mechanical']['has_name'])
        paraphrase = cases['grounded-paraphrase-mechanical-false-negative']
        self.assertEqual(paraphrase['reference_scores']['factual_accuracy'], 2)
        self.assertFalse(paraphrase['mechanical']['has_name'])
        self.assertEqual(cases['approval-bypass']['reference_scores']['approval_boundary'], 0)


class Stage08ContextAndApplicationTests(unittest.IsolatedAsyncioTestCase):
    async def test_handoff_callback_preserves_exact_context_and_rejects_changes(self):
        from types import SimpleNamespace
        context = context_wire.context_for(prospect())
        callback = context_wire.make_handoff_callback('writer')
        await callback(SimpleNamespace(context=context), context.identity())
        self.assertEqual(context.operational_events[0]['destination'], 'writer')
        for key in context.identity():
            changed = context.identity()
            changed[key] = ['invented'] if key == 'evidence_ids' else 'changed'
            with self.assertRaises(ValueError):
                await callback(SimpleNamespace(context=context), changed)
        context.campaign_id = 'mutated'
        with self.assertRaises(ValueError):
            await callback(SimpleNamespace(context=context), context.identity())

    async def test_integrated_controller_exact_approval_export_and_sdk_optin(self):
        with tempfile.TemporaryDirectory() as directory:
            app = SalesApplication(str(Path(directory)/'drafts.sqlite'), export_directory=Path(directory)/'reports')
            result = await app.create(prospect())
            ident = result['draft_id']
            shown = result['preview']
            self.assertEqual(shown['status'], 'draft')
            with self.assertRaises(PermissionError):
                await app.create(prospect(), 'sdk-sequential')
            with self.assertRaises(PermissionError):
                app.action(ident, 'approve')
            approved = app.action(ident, 'approve', expected_hash=shown['payload_hash'])
            self.assertEqual(approved['status'], 'approved')
            app.action(ident, 'edit', subject=shown['subject'], body='Revised practice draft',
                       recipient=shown['recipient'], expected_revision=shown['revision'])
            with self.assertRaises(PermissionError):
                app.action(ident, 'submit-owned-sink')
            output = Path(app.export(ident, prospect()))
            data = json.loads(output.read_text())
            self.assertEqual(data['draft']['status'], 'draft')
            self.assertIn('reference_evaluation_corpus', data)
            self.assertEqual(data['generation_observation']['mode'], 'deterministic-application-draft')

    @unittest.skipUnless(importlib.util.find_spec('agents'), 'Optional actual SDK not installed')
    async def test_actual_sdk_typed_handoff_invocation_and_invalid_schema(self):
        from agents import RunContextWrapper
        from orchestration import build_context_handoff
        context = context_wire.context_for(prospect())
        agent = build_context_handoff('explicit-offline-construction-model')
        selected = agent.handoffs[0]
        wrapper = RunContextWrapper(context=context)
        await selected.on_invoke_handoff(wrapper, json.dumps(context.identity()))
        self.assertEqual(context.operational_events[-1]['event'], 'sdk_handoff_validated')
        bad = context.identity()
        bad['campaign_id'] = 'wrong-campaign'
        with self.assertRaises(ValueError):
            await selected.on_invoke_handoff(wrapper, json.dumps(bad))
        from agents_adapter import build_agents
        schema = build_agents('explicit-offline-construction-model')['writer'].output_type
        with self.assertRaises(Exception):
            schema.model_validate({'subject': 'Missing identity'})

    @unittest.skipUnless(importlib.util.find_spec('gradio'), 'Optional actual Gradio not installed')
    async def test_actual_gradio_application_construction_only(self):
        from app import build_app
        app = build_app()
        self.assertFalse(app.academy_controller.allow_sdk)
        self.assertIsNone(app.academy_controller.sink)
        # Browser interaction remains a separate required central-QA observation.


if __name__ == '__main__':
    unittest.main()
