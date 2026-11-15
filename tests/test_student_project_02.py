"""Sales student regressions: no SDK installation, model calls, sockets or email."""
import asyncio
from contextlib import redirect_stdout
import importlib
import io
import json
from pathlib import Path
import re
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch


PROJECT = Path(__file__).resolve().parents[1] / 'projects/02-sales-team'


class Output:
    def __init__(self, values):
        self.values = values

    def model_dump(self):
        return self.values.copy()


class StudentSalesTests(unittest.TestCase):
    def setUp(self):
        self.modules = patch.dict(sys.modules)
        self.modules.start()
        self.addCleanup(self.modules.stop)
        self.paths = patch.object(sys, 'path', [str(PROJECT), *sys.path])
        self.paths.start()
        self.addCleanup(self.paths.stop)
        for name in ('sales', 'agents_adapter', 'application', 'context_wire',
                     'orchestration', 'evaluations', 'exercises', 'app'):
            sys.modules.pop(name, None)
        self.sales = importlib.import_module('sales')
        self.adapter = importlib.import_module('agents_adapter')
        self.application = importlib.import_module('application')
        self.context = importlib.import_module('context_wire')
        self.evaluations = importlib.import_module('evaluations')
        self.prospect = self.sales.Prospect(**json.loads((PROJECT/'fixtures/prospect.json').read_text())['prospect'])
        self.directory = tempfile.TemporaryDirectory(prefix='student-sales-test-')
        self.addCleanup(self.directory.cleanup)
        self.network = patch('socket.create_connection', side_effect=AssertionError('Network forbidden'))
        self.network.start()
        self.addCleanup(self.network.stop)

    def controller(self, **kwargs):
        return self.application.SalesApplication(str(Path(self.directory.name)/'drafts.sqlite'),
            export_directory=Path(self.directory.name)/'reports', **kwargs)

    def runner(self, corrupt_role=None, corrupt_key=None, review_passes=True):
        calls = []
        identity = self.context.context_for(self.prospect).identity()

        async def run(role, payload, **kwargs):
            values = {**identity, 'source_id': self.prospect.source_id}
            if role == 'research':
                values.update(need=self.prospect.verified_need, limitations='synthetic')
            elif role == 'strategy':
                values['value_proposition'] = 'A reporting demonstration'
            elif role == 'writer':
                values.update(subject='Practice draft', body='A reporting demonstration for review.')
            elif role == 'reviewer':
                values.pop('source_id')
                values.update(passed=review_passes, issues=[] if review_passes else ['Unsupported claim'])
            if role == corrupt_role:
                if corrupt_key == 'missing':
                    values.pop('prospect_id')
                else:
                    values[corrupt_key] = ['wrong-evidence'] if corrupt_key == 'evidence_ids' else 'wrong-identity'
            calls.append((role, json.loads(payload), kwargs))
            return SimpleNamespace(final_output=Output(values), last_agent=SimpleNamespace(name=role), new_items=[])

        return run, calls

    def run_fake(self, entry='run_pipeline', **kwargs):
        runner, calls = self.runner(**kwargs)
        fake_sdk = SimpleNamespace(Runner=SimpleNamespace(run=runner), RunConfig=lambda **options: options)
        with patch.dict(sys.modules, {'agents': fake_sdk}), patch.object(self.adapter, 'build_agents',
                return_value={role: role for role in ('research', 'strategy', 'writer', 'reviewer')}):
            result = asyncio.run(getattr(self.adapter, entry)(self.prospect, 'offline-fake-model'))
        return result, calls

    def test_both_sequential_entrypoints_reject_all_identity_mutations(self):
        for entry in ('run_pipeline', 'run_integrated_pipeline'):
            for role in ('research', 'strategy', 'writer', 'reviewer'):
                for key in (*self.context.context_for(self.prospect).identity(), 'missing'):
                    with self.subTest(entry=entry, role=role, field=key), self.assertRaises(ValueError):
                        self.run_fake(entry, corrupt_role=role, corrupt_key=key)

    def test_all_evidence_sources_are_checked(self):
        for role in ('research', 'strategy', 'writer'):
            with self.subTest(role=role), self.assertRaises(ValueError):
                self.run_fake(corrupt_role=role, corrupt_key='source_id')

    def test_valid_cli_pipeline_retains_intermediates_without_approval(self):
        result, calls = self.run_fake()
        self.assertEqual(result['status'], 'human_approval_required')
        self.assertEqual(result['draft']['status'], 'draft')
        self.assertEqual(result['external_messages_sent'], 0)
        self.assertEqual([event['role'] for event in result['operational_events']],
                         ['research', 'strategy', 'writer', 'reviewer'])
        self.assertEqual(calls[2][1]['retained_outputs']['research']['source_id'], self.prospect.source_id)

    def test_cli_failed_review_never_promotes_to_human_approval(self):
        result, calls = self.run_fake(review_passes=False)
        self.assertEqual(result['status'], 'revision_required')
        self.assertEqual(result['issues'], ['Unsupported claim'])
        self.assertEqual(len(calls), 4)

    def test_actual_cli_main_uses_validated_pipeline(self):
        runner, calls = self.runner(corrupt_role='strategy', corrupt_key='source_id')
        fake_sdk = SimpleNamespace(Runner=SimpleNamespace(run=runner), RunConfig=lambda **options: options)
        with patch.dict(sys.modules, {'agents': fake_sdk}), patch.object(self.adapter, 'build_agents',
                return_value={role: role for role in ('research', 'strategy', 'writer', 'reviewer')}), \
                patch.object(sys, 'argv', ['agents_adapter.py', '--live']), \
                patch.dict(self.adapter.os.environ, {'OPENAI_API_KEY': 'offline-fixture-not-a-secret', 'ACADEMY_MODEL': 'offline-fake-model'}), \
                self.assertRaises(ValueError):
            self.adapter.main()
        self.assertEqual(len(calls), 2)

    def test_failed_sdk_review_can_be_rejected_but_not_approved(self):
        controller = self.controller(allow_sdk=True, model='offline-fake-model')
        result, calls = self.run_fake('run_integrated_pipeline', review_passes=False)

        async def failed_review(*args, **kwargs):
            return result

        with patch.object(self.adapter, 'run_integrated_pipeline', side_effect=failed_review):
            created = asyncio.run(controller.create(self.prospect, 'sdk-sequential'))
        ident = created['draft_id']
        self.assertEqual(created['preview']['status'], 'revision_required')
        with self.assertRaises(ValueError):
            controller.action(ident, 'approve', expected_hash=created['preview']['payload_hash'])
        self.assertEqual(controller.action(ident, 'reject')['status'], 'rejected')

    def test_reject_preserves_unknown_sending_and_submitted_holds(self):
        team = self.sales.SalesTeam()
        self.addCleanup(team.db.close)
        for status in ('sending', 'unknown_outcome', 'accepted_by_owned_sink', 'simulated_delivery'):
            ident = team.create_draft(self.prospect)
            with team.db:
                team.db.execute('UPDATE drafts SET status=? WHERE id=?', (status, ident))
            with self.subTest(status=status), self.assertRaises(PermissionError):
                team.reject(ident)

    def test_offline_controller_capstone_stale_hash_and_duplicate_refusal(self):
        controller = self.controller()
        created = asyncio.run(controller.create(self.prospect))
        ident, preview = created['draft_id'], created['preview']
        with self.assertRaises(PermissionError):
            controller.action(ident, 'simulate', expected_hash=preview['payload_hash'])
        with self.assertRaises(PermissionError):
            controller.action(ident, 'simulate', expected_hash='stale')
        controller.action(ident, 'approve', expected_hash=preview['payload_hash'])
        receipt = controller.action(ident, 'simulate', expected_hash=preview['payload_hash'])
        self.assertEqual(receipt['delivery'], 'simulated_only')
        self.assertEqual(receipt['external_messages_sent'], 0)
        with self.assertRaises(PermissionError):
            controller.action(ident, 'simulate', expected_hash=preview['payload_hash'])
        exported = json.loads(Path(controller.export(ident, self.prospect)).read_text())
        self.assertEqual(exported['draft']['status'], 'simulated_delivery')
        self.assertEqual(exported['transport_history'], [])
        self.assertEqual(len(exported['simulated_outbox']), 1)

    def test_edit_revokes_approval_before_simulation(self):
        controller = self.controller()
        created = asyncio.run(controller.create(self.prospect))
        ident, preview = created['draft_id'], created['preview']
        controller.action(ident, 'approve', expected_hash=preview['payload_hash'])
        edited = controller.action(ident, 'edit', subject='Edited', body=preview['body'])
        with self.assertRaises(PermissionError):
            controller.action(ident, 'simulate', expected_hash=edited['payload_hash'])
        with self.assertRaises(PermissionError):
            controller.action(ident, 'submit-owned-sink', expected_hash=edited['payload_hash'])

    def test_manager_and_handoff_observations_export_without_drafts(self):
        controller = self.controller(allow_sdk=True, model='offline-fake-model')

        async def observation(*args, **kwargs):
            return {'mode': 'offline-fixture', 'final_output': 'No revision observed', 'external_messages_sent': 0}

        for mode, target in (('sdk-manager', 'run_integrated_pipeline'), ('sdk-handoff', 'run_context_handoff')):
            with patch.object(self.adapter, target, side_effect=observation):
                result = asyncio.run(controller.create(self.prospect, mode))
            self.assertIsNone(result['draft_id'])
            report = json.loads(Path(controller.export_observation(result['observation_id'])).read_text())
            self.assertEqual(report['observation']['mode'], 'offline-fixture')
            with self.assertRaises(ValueError):
                controller.action(None, 'simulate')
            with self.assertRaises(ValueError):
                controller.export(None, self.prospect)
        with self.assertRaises(ValueError):
            controller.export_observation('../unknown')

    def test_observation_events_keep_actual_calls_outputs_and_transfer_only(self):
        result = SimpleNamespace(new_items=[
            SimpleNamespace(type='tool_call_item', raw_item=SimpleNamespace(name='writer', arguments='{"revision_reason":"remove claim"}', call_id='fixture-call')),
            SimpleNamespace(type='tool_call_output_item', output='Actual fixture result'),
            SimpleNamespace(type='handoff_output_item', source_agent=SimpleNamespace(name='triage'), target_agent=SimpleNamespace(name='research')),
            SimpleNamespace(type='reasoning_item', raw_item='must not export private reasoning')])
        events = self.adapter.coordination_events(result)
        self.assertEqual(events[0]['name'], 'writer')
        self.assertEqual(events[1]['output'], 'Actual fixture result')
        self.assertEqual(events[2]['to_agent'], 'research')
        self.assertNotIn('private reasoning', json.dumps(events))

    def test_six_worked_solutions(self):
        exercise = importlib.import_module('exercises')
        result = exercise.worked_solutions()
        self.assertEqual(result['exercises_checked'], 6)
        self.assertEqual(result['receipt']['external_messages_sent'], 0)

    def test_documented_scoring_sample_counts_sparse_failure(self):
        text = (PROJECT/'WORKED-SOLUTIONS.md').read_text()
        snippet = re.search(r'```python\n(.*?)```', text, re.S).group(1)
        real_path = Path

        def project_path(value):
            return PROJECT/value if value == 'fixtures' else real_path(value)

        output = io.StringIO()
        with patch('pathlib.Path', side_effect=project_path), redirect_stdout(output):
            exec(compile(snippet, 'WORKED-SOLUTIONS.md', 'exec'), {})
        report = json.loads(output.getvalue())
        self.assertEqual((report['fixture_count'], report['agent_output_count'], report['failure_count']), (2, 0, 1))
        self.assertFalse(report['model_scoring_performed'])
        bad = report['cases'][0]
        for field, value in (('source_id', 'unknown'), ('reviewer', ''), ('output_origin', 'model-verified')):
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.evaluations.score_observations([{**bad, field: value}])
        with self.assertRaises(ValueError):
            self.evaluations.score_observations([{**bad, 'scores': dict.fromkeys(self.evaluations.DIMENSIONS, True)}])

    def test_project_document_links_exist_and_no_internal_release_gates(self):
        for filename in ('README.md', 'WORKED-SOLUTIONS.md'):
            text = (PROJECT/filename).read_text()
            for destination in re.findall(r'\]\(([^)]+)\)', text):
                path = destination.split('#')[0]
                if path:
                    self.assertTrue((PROJECT/path).exists(), destination)
            self.assertNotIn('central runtime validation', text)
            self.assertNotIn('central guarded validator', text)

    def test_ui_callbacks_simulate_and_export_observations_without_gradio_or_servers(self):
        callbacks = {}

        class Component:
            def __init__(self, *values, label=None, **kwargs):
                self.label = label or (values[0] if values else None)

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def click(self, function, inputs=None, outputs=None):
                callbacks[self.label] = SimpleNamespace(function=function, outputs=outputs)

        fake_gradio = SimpleNamespace(**{name: Component for name in
            ('Blocks', 'Markdown', 'State', 'Dropdown', 'Textbox', 'Number', 'JSON', 'Button', 'File')})
        ui = importlib.import_module('app')
        with patch.dict(sys.modules, {'gradio': fake_gradio}), \
                patch.object(ui.tempfile, 'mkdtemp', return_value=self.directory.name):
            built = ui.build_app(allow_sdk=True, model='offline-fake-model')
        generated = asyncio.run(callbacks['Generate or observe selected workflow'].function('deterministic'))
        self.assertEqual(len(generated), len(callbacks['Generate or observe selected workflow'].outputs))
        ident, observation_id, recipient, subject, body, revision, shown_hash, report = generated
        self.assertIsNone(observation_id)
        arguments = (ident, recipient, subject, body, revision, shown_hash)
        with self.assertRaises(PermissionError):
            callbacks['Approve exact preview'].function(ident, recipient, 'Unsaved text', body, revision, shown_hash)
        callbacks['Approve exact preview'].function(*arguments)
        with self.assertRaises(PermissionError):
            callbacks['Simulate approved delivery; no email'].function(ident, recipient, 'Unsaved text', body, revision, shown_hash)
        result = callbacks['Simulate approved delivery; no email'].function(*arguments)
        self.assertEqual(result[-1]['delivery'], 'simulated_only')

        async def observation(*args, **kwargs):
            return {'mode': 'offline-fixture-observation', 'external_messages_sent': 0}

        with patch.object(self.adapter, 'run_context_handoff', side_effect=observation):
            generated = asyncio.run(callbacks['Generate or observe selected workflow'].function('sdk-handoff'))
        self.assertIsNone(generated[0])
        path = callbacks['Export selected manager/handoff observation'].function(generated[1])
        self.assertEqual(json.loads(Path(path).read_text())['observation']['mode'], 'offline-fixture-observation')
        with self.assertRaises(ValueError):
            callbacks['Approve exact preview'].function(None, '', '', '', None, '')


if __name__ == '__main__':
    unittest.main()
