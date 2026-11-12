"""Authored tests; run only through the coordinator's bounded central QA."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import threading
import unittest

PATH = Path(__file__).resolve().parents[1] / 'examples/stages02-04/stage03_patterns.py'
SPEC = importlib.util.spec_from_file_location('stage03_semantic_material', PATH)
m = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = m
SPEC.loader.exec_module(m)


class Fake:
    def __init__(self, responses):
        self.responses, self.requests = list(responses), []
    def chat(self, messages, tools=None):
        self.requests.append(copy.deepcopy(messages))
        value = self.responses.pop(0)
        if isinstance(value, Exception):
            raise value
        return value


def tool(identity, name, args):
    return {'role': 'assistant', 'tool_calls': [{'id': identity, 'type': 'function',
            'function': {'name': name, 'arguments': json.dumps(args)}}]}


class Stage03SemanticTests(unittest.TestCase):
    def test_extract_validate_format_records_three_steps(self):
        model = Fake([{'content': json.dumps(m.SYNTHETIC_PROFILE)}])
        result = m.extract_validate_format(model, 'Synthetic Alex profile')
        self.assertEqual(result['status'], 'completed')
        self.assertEqual([x['step'] for x in result['trace']], ['extract', 'extract', 'validate', 'format'])
        self.assertIn('[academy-synthetic-profile-v1]', result['text'])
        self.assertEqual(len(model.requests), 1)

    def test_invalid_intermediate_blocks_format(self):
        for value in ('not JSON', '{"name":"Alex"}', json.dumps(dict(m.SYNTHETIC_PROFILE, skills='Python'))):
            result = m.extract_validate_format(Fake([{'content': value}]), 'note')
            self.assertEqual(result['status'], 'blocked')
            self.assertFalse(any(x['step'] == 'format' for x in result['trace']))
            self.assertEqual(result['trace'][-1]['step'], 'validate')

    def test_extraction_transport_failure_retained(self):
        result = m.extract_validate_format(Fake([TimeoutError('private detail')]), 'note')
        self.assertEqual(result['trace'][-1]['error_type'], 'TimeoutError')
        self.assertNotIn('private detail', json.dumps(result))

    def test_common_contact_workflow_and_agent_same_action(self):
        email = 'alex@example.invalid'
        state = m.RequestState(True, email)
        workflow_store, agent_store = [], []
        fixed = m.contact_workflow(email, state, workflow_store)
        model = Fake([tool('contact1', 'capture_contact', {'email': email}), {'content': 'Done'}])
        agent = m.contact_agent(model, email, state, agent_store)
        self.assertEqual(fixed['status'], 'completed')
        self.assertEqual(agent['status'], 'completed')
        self.assertEqual(workflow_store, agent_store)
        self.assertEqual(fixed['model_calls'], 0)
        self.assertEqual(agent['calls'], 2)

    def test_model_cannot_claim_unstored_contact(self):
        state = m.RequestState(True, 'alex@example.invalid')
        result = m.contact_agent(Fake([{'content': 'I saved it'}]), 'alex@example.invalid', state, [])
        self.assertEqual(result['status'], 'human_review')
        self.assertIn('unconfirmed', result['reason'])

    def test_no_consent_blocks_both_paths_without_model(self):
        model, contacts = Fake([]), []
        fixed = m.contact_workflow('alex@example.invalid', m.RequestState(), contacts)
        agent = m.contact_agent(model, 'alex@example.invalid', m.RequestState(), contacts)
        self.assertEqual(fixed['status'], 'human_review')
        self.assertEqual(agent['status'], 'human_review')
        self.assertEqual(model.requests, [])
        self.assertEqual(contacts, [])

    def test_tool_error_returned_as_feedback_and_recovers(self):
        model = Fake([tool('bad', 'delete', {}), tool('good', 'profile_lookup', {'field': 'role'}), {'content': 'Python developer'}])
        result = m.observed_agent_loop(model, 'role?')
        self.assertEqual(result['status'], 'completed')
        feedback = json.loads(model.requests[1][-1]['content'])
        self.assertFalse(feedback['ok'])
        self.assertEqual(model.requests[1][-1]['tool_call_id'], 'bad')
        self.assertTrue(any(x['event'] == 'validated_action' for x in result['trace']))
        self.assertEqual(result['trace'][-1]['event'], 'stop')

    def test_maximum_turn_stop_is_recorded(self):
        result = m.observed_agent_loop(Fake([tool('one', 'profile_lookup', {'field': 'role'})]), 'role?', max_calls=1)
        self.assertEqual(result['status'], 'human_review')
        self.assertEqual(result['reason'], 'maximum_model_calls')
        self.assertEqual(result['trace'][-1]['event'], 'stop')

    def test_reused_identity_terminal_no_second_action(self):
        model = Fake([tool('same', 'profile_lookup', {'field': 'role'}), tool('same', 'profile_lookup', {'field': 'name'})])
        result = m.observed_agent_loop(model, 'profile?')
        self.assertEqual(result['status'], 'blocked')
        self.assertEqual(len(result['tool_results']), 1)

    def test_unknown_transport_stops_without_retry(self):
        model = Fake([TimeoutError('secret'), {'content': 'never'}])
        result = m.observed_agent_loop(model, 'profile?')
        self.assertEqual(len(model.requests), 1)
        self.assertEqual(result['reason'], 'model_outcome_unknown')
        self.assertNotIn('secret', json.dumps(result))

    def test_stateful_router_taxonomy(self):
        no = m.RequestState()
        self.assertEqual(m.route_request({'category': 'professional_information', 'field': 'skills'}, no)['action'], 'profile_lookup')
        for req in ({'category': 'ambiguous'}, {'category': 'professional_information', 'field': 'api_key'},
                    {'category': 'contact_capture', 'email': 'alex@example.invalid', 'approved': True}):
            self.assertEqual(m.route_request(req, no)['action'], 'none')
        hold = m.RequestState(True, 'alex@example.invalid', True)
        self.assertEqual(m.route_request({'category': 'contact_capture', 'email': 'alex@example.invalid'}, hold)['action'], 'none')

    def test_malicious_document_model_output_cannot_authorize_contact(self):
        contacts = []
        model = Fake([tool('injected', 'capture_contact', {'email': 'attacker@example.invalid'}), {'content': 'I could not do that'}])
        result = m.observed_agent_loop(model, m.RISK_REGISTER[0]['attack'], m.RequestState(), contacts)
        self.assertEqual(contacts, [])
        self.assertTrue(any(x['event'] == 'tool_error' for x in result['trace']))

    def test_invented_credentials_tool_request_denied(self):
        with self.assertRaises(ValueError):
            m.application_tool('profile_lookup', {'field': 'api_key'}, m.RequestState(), [])
        with self.assertRaises(PermissionError):
            m.application_tool('profile_lookup', {'field': 'name'}, m.RequestState(human_review_required=True), [])

    def test_model_argument_cannot_be_application_consent(self):
        with self.assertRaises(ValueError):
            m.application_tool('capture_contact', {'email': 'alex@example.invalid', 'consent': True}, m.RequestState(), [])
        with self.assertRaises(PermissionError):
            m.application_tool('capture_contact', {'email': 'different@example.invalid'}, m.RequestState(True, 'alex@example.invalid'), [])

    def test_sequential_concurrent_same_inputs_ids_failures(self):
        tasks = [m.ModelTask('a', 'alpha'), m.ModelTask('b', 'beta'), m.ModelTask('c', 'gamma')]
        def factory(identity):
            return Fake([TimeoutError()]) if identity == 'b' else Fake([{'content': 'response-' + identity}])
        sequential = m.measured_requests(tasks, factory)
        concurrent = m.measured_requests(tasks, factory, concurrent=True, workers=2)
        for result in (sequential, concurrent):
            self.assertEqual([x['request_id'] for x in result['results']], ['a', 'b', 'c'])
            self.assertEqual(result['results'][1]['status'], 'failed')
            self.assertEqual(result['results'][1]['error_type'], 'TimeoutError')
            self.assertGreaterEqual(result['elapsed_seconds'], 0)
            self.assertTrue(result['synthetic_transport'])
        self.assertEqual([x['input_sha256'] for x in sequential['results']], [x['input_sha256'] for x in concurrent['results']])

    def test_concurrent_actual_cap_and_overlap(self):
        gate, lock = threading.Barrier(2), threading.Lock()
        active, maximum = [0], [0]
        class Branch:
            def chat(self, messages):
                with lock:
                    active[0] += 1
                    maximum[0] = max(maximum[0], active[0])
                gate.wait(timeout=5)
                with lock:
                    active[0] -= 1
                return {'content': 'synthetic branch'}
        result = m.measured_requests([m.ModelTask('a', 'a'), m.ModelTask('b', 'b')], lambda identity: Branch(), concurrent=True, workers=2)
        self.assertEqual(maximum[0], 2)
        self.assertTrue(all(x['status'] == 'completed' for x in result['results']))

    def test_typed_profile_workers_and_provenance(self):
        profile = m.validate_profile(m.SYNTHETIC_PROFILE)
        result = m.review_profile(profile, m.SYNTHETIC_PROFILE)
        self.assertEqual(result['status'], 'deterministic_checks_clear')
        self.assertEqual([x['role'] for x in result['plan']], ['grounding', 'tone', 'privacy'])
        self.assertTrue(all(x['worker_id'] and x['source_id'] == profile.source_id for x in result['results']))

    def test_worker_missing_mismatched_provenance_and_failed(self):
        profile = m.validate_profile(m.SYNTHETIC_PROFILE)
        def malformed(task, profile, source):
            if task.role == 'grounding':
                return None
            if task.role == 'tone':
                return m.WorkerResult('wrong-task', 'worker', task.source_id, 'clear', ())
            raise RuntimeError('private detail')
        result = m.review_profile(profile, m.SYNTHETIC_PROFILE, malformed)
        self.assertEqual(result['status'], 'human_review')
        self.assertTrue(all(x['status'] == 'failed' for x in result['results']))
        self.assertNotIn('private detail', json.dumps(result))

    def test_grounding_detects_invented_role(self):
        fake = dict(m.SYNTHETIC_PROFILE, role='Chief executive')
        result = m.review_profile(m.validate_profile(fake), m.SYNTHETIC_PROFILE)
        self.assertEqual(result['status'], 'human_review')
        self.assertIn('Unsupported field: role', result['results'][0]['findings'])

    def test_labeled_dataset_and_escalation_distinguish_subjective_review(self):
        result = m.evaluate_controls()
        self.assertTrue(all(x['passed'] for x in result['cases']))
        self.assertEqual({x['kind'] for x in result['cases']}, {'grounded', 'unsupported', 'malicious', 'contact-consent'})
        self.assertIn('NOT_SCORED', result['subjective_review'])
        self.assertTrue(any('not human approval' in x for x in result['human_escalation_checklist']))

if __name__ == '__main__':
    unittest.main()
