"""Behavioral tests for Stage 5 local lead/question tooling.

Authored for central QA execution; these tests contain no network operation.
"""
import importlib
from pathlib import Path
import sys
import tempfile
import unittest

PROJECT = Path(__file__).resolve().parents[1] / 'projects' / '01-digital-twin'
sys.path.insert(0, str(PROJECT))
from tools import Lead, Question, ToolCall, ToolsService
from notifications import NotificationAdapter


class Stage05ToolsTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.database = str(Path(self.directory.name) / 'contacts.sqlite3')
        self.service = ToolsService(self.database)

    def tearDown(self):
        self.service.close()
        self.directory.cleanup()

    def lead(self, call_id='lead-1', **changes):
        arguments = dict(name='Visitor', email='visitor@example.test', message='Discuss a role',
                         consent=True, opportunity='Python instructor')
        arguments.update(changes)
        return self.service.record_lead(call_id, **arguments)

    def test_lead_opportunity_and_durable_restart_dedupe(self):
        first = self.lead()
        self.assertEqual('Python instructor', self.service.store.db.execute('SELECT opportunity FROM twin_leads').fetchone()[0])
        self.service.close()
        self.service = ToolsService(self.database)
        self.assertEqual(first, self.lead())
        self.assertEqual(1, self.service.store.db.execute('SELECT count(*) FROM twin_leads').fetchone()[0])
        self.assertEqual(1, len(self.service.pending_outbox()))

    def test_same_call_id_changed_arguments_or_tool_rejected(self):
        self.lead()
        with self.assertRaises(ValueError):
            self.lead(message='A changed request')
        with self.assertRaises(ValueError):
            self.service.capture_question('lead-1', 'What happens next?', True)
        self.assertEqual(0, self.service.store.db.execute('SELECT count(*) FROM twin_questions').fetchone()[0])

    def test_typed_consent_and_fields(self):
        for value in [False, None, 'true', 1]:
            with self.assertRaises(PermissionError):
                self.lead(consent=value)
        with self.assertRaises(ValueError):
            self.lead(email='not-an-email')
        with self.assertRaises(ValueError):
            self.lead(message='x' * 2001)
        with self.assertRaises(ValueError):
            self.lead(opportunity={'untyped': True})
        with self.assertRaises(PermissionError):
            Question('Why?', False)
        self.assertEqual(0, self.service.store.db.execute('SELECT count(*) FROM twin_calls').fetchone()[0])

    def test_question_persistence_replay(self):
        first = self.service.capture_question('question-1', 'What projects can you discuss?', True)
        self.assertEqual(first, self.service.capture_question('question-1', 'What projects can you discuss?', True))
        self.assertEqual(1, self.service.store.db.execute('SELECT count(*) FROM twin_questions').fetchone()[0])
        self.assertEqual({'kind': 'question_received', 'question_id': first['question_id']}, self.service.pending_outbox()[0]['payload'])

    def test_mixed_tools_continue_in_order_and_resume(self):
        calls = [ToolCall('capture_question', {'question': 'Which Python work?', 'consent': True}, 'question-1'),
                 {'name': 'delete_everything', 'args': {}, 'call_id': 'bad-1'},
                 {'name': 'record_lead', 'arguments': {'name': 'Visitor', 'email': 'visitor@example.test',
                  'message': 'A role', 'consent': True}, 'call_id': 'lead-1'}]
        first = self.service.run(calls)
        self.assertEqual(['ok', 'rejected', 'ok'], [r['status'] for r in first])
        self.assertEqual(first, self.service.run(calls))
        self.assertEqual(2, len(self.service.pending_outbox()))

    def test_turn_limit_rejects_before_any_effect(self):
        calls = [{'name': 'capture_question', 'args': {'question': 'Why?', 'consent': True}, 'call_id': f'q-{i}'} for i in range(9)]
        with self.assertRaises(ValueError):
            self.service.run(calls)
        self.assertEqual([], self.service.pending_outbox())

    def test_invalid_call_shape_cannot_override_call_id(self):
        result = self.service.run([{'name': 'capture_question', 'call_id': 'q-1',
                                   'args': {'call_id': 'q-2', 'question': 'Why?', 'consent': True}}])
        self.assertEqual('rejected', result[0]['status'])
        self.assertEqual([], self.service.pending_outbox())

    def test_nested_transaction_rollback_is_atomic(self):
        with self.assertRaises(RuntimeError):
            with self.service.store.transaction():
                self.lead()
                raise RuntimeError('outer caller failed')
        for table in ['twin_leads', 'twin_calls', 'twin_outbox']:
            self.assertEqual(0, self.service.store.db.execute(f'SELECT count(*) FROM {table}').fetchone()[0])
        self.lead()
        self.assertEqual(1, len(self.service.pending_outbox()))

    def test_inner_rollback_does_not_erase_outer_work(self):
        with self.service.store.transaction():
            self.lead('first')
            try:
                with self.service.store.transaction():
                    self.lead('rolled-back')
                    raise ValueError('nested failure')
            except ValueError:
                pass
            self.service.capture_question('q-1', 'Why?', True)
        self.assertEqual(2, self.service.store.db.execute('SELECT count(*) FROM twin_calls').fetchone()[0])

    def test_default_delivery_is_durable_local_dry_run(self):
        first = self.lead()
        receipt = self.service.dispatch_once(first['outbox_id'])
        self.assertEqual('dry_run', receipt['status'])
        self.assertEqual('not_sent', receipt['receipt']['delivery'])
        self.assertNotIn('email', receipt['receipt']['payload'])
        self.assertFalse(self.service.dispatch_once(first['outbox_id'])['dispatched'])
        self.assertEqual([], self.service.pending_outbox())

    def test_local_failure_needs_explicit_retry_without_contact_recreation(self):
        first = self.lead()
        calls = []
        def fail(payload):
            calls.append(payload)
            raise OSError('not delivered')
        adapter = NotificationAdapter('local-failure', fail, external=False)
        self.assertEqual('local_failed', self.service.dispatch_once(first['outbox_id'], adapter=adapter)['status'])
        self.assertFalse(self.service.dispatch_once(first['outbox_id'], adapter=adapter)['dispatched'])
        self.assertEqual(1, len(calls))
        self.assertEqual('dry_run', self.service.dispatch_once(first['outbox_id'], retry_local=True)['status'])
        self.assertEqual(first, self.lead())
        self.assertEqual(1, self.service.store.db.execute('SELECT count(*) FROM twin_leads').fetchone()[0])

    def test_external_requires_permission_and_unknown_is_never_replayed(self):
        first = self.lead()
        calls = []
        def uncertain(payload):
            calls.append(payload)
            raise TimeoutError('provider may already have received request')
        adapter = NotificationAdapter('explicit-test-adapter', uncertain)
        with self.assertRaises(PermissionError):
            self.service.dispatch_once(first['outbox_id'], adapter=adapter)
        self.assertEqual([], calls)
        self.assertEqual('unknown', self.service.dispatch_once(first['outbox_id'], adapter=adapter, allow_external=True)['status'])
        self.assertFalse(self.service.dispatch_once(first['outbox_id'], adapter=adapter, allow_external=True, retry_local=True)['dispatched'])
        self.assertEqual(1, len(calls))

    def test_external_delivered_receipt_is_separate_from_stored_lead(self):
        first = self.lead()
        adapter = NotificationAdapter('test-receipt', lambda _: {'status': 'delivered', 'receipt_id': 'fixture-ack-1'})
        delivered = self.service.dispatch_once(first['outbox_id'], adapter=adapter, allow_external=True)
        self.assertEqual('delivered', delivered['status'])
        self.assertEqual(first, self.lead())
        self.assertEqual(1, self.service.store.db.execute('SELECT attempts FROM twin_outbox').fetchone()[0])

    def test_crash_dispatching_state_is_held_after_restart(self):
        first = self.lead()
        with self.service.store.transaction() as db:
            db.execute("UPDATE twin_outbox SET status='dispatching',external=1 WHERE id=?", (first['outbox_id'],))
        self.service.close()
        self.service = ToolsService(self.database)
        self.assertEqual('dispatching', self.service.dispatch_once(first['outbox_id'])['status'])
        self.assertEqual('nothing_pending', self.service.dispatch_once()['status'])

    def test_dispatch_inside_outer_transaction_refused(self):
        first = self.lead()
        with self.service.store.transaction():
            with self.assertRaises(RuntimeError):
                self.service.dispatch_once(first['outbox_id'])
        self.assertEqual('pending', self.service.pending_outbox()[0]['status'])

    def test_retention_erases_personal_data_keeps_replay_tombstone(self):
        self.service.store.clock = lambda: 100.0
        first = self.lead()
        self.service.capture_question('q-1', 'Private question', True)
        counts = self.service.purge_retention(101.0)
        self.assertEqual(1, counts['twin_leads'])
        self.assertEqual(1, counts['twin_questions'])
        self.assertEqual('expired', self.lead()['status'])
        self.assertEqual([], self.service.pending_outbox())
        self.assertEqual(0, self.service.store.db.execute('SELECT count(*) FROM twin_leads').fetchone()[0])


if __name__ == '__main__':
    unittest.main()
