"""Authored Stage4 semantic tests. No actual provider request or installation."""
import copy
from dataclasses import replace
import importlib.util
import io
import json
from pathlib import Path
import sys
import unittest

DIRECTORY = Path(__file__).resolve().parents[1] / 'examples/stages02-04'
sys.path.insert(0, str(DIRECTORY))
import stage03_patterns as patterns
SPEC = importlib.util.spec_from_file_location('stage04_semantic_material', DIRECTORY / 'stage04_selection.py')
m = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = m
SPEC.loader.exec_module(m)

CONFIGS = {
    'academy_hosted': {'provider': 'hosted_compatible', 'model': 'synthetic-hosted-model',
                      'base_url': 'https://example.invalid/v1', 'credential_env': 'ACADEMY_TEST_KEY'},
    'academy_local': {'provider': 'ollama', 'model': 'synthetic-local-model',
                     'base_url': 'http://127.0.0.1:11434'},
}


class FakeModel:
    def __init__(self, responses):
        self.responses, self.requests = list(responses), []
    def chat(self, messages, tools=None):
        self.requests.append(copy.deepcopy(messages))
        return self.responses.pop(0)


def rubric(task='extract', **changes):
    value = m.TaskRubric(task, 'Extract the approved profile fields', '2026-11-12',
                        {'quality': .4, 'speed': .2, 'cost': .2, 'reliability': .2},
                        4, 10, .01, 'illustrative-USD', ('structured_json',))
    return replace(value, **changes)


def measurement(model='synthetic-a', task='extract', **changes):
    value = m.Measurement(model, task, '2026-11-12', 4, 2, .002, 'illustrative-USD', 4, 5,
                          ('structured_json',), True)
    return replace(value, **changes)


class Stage04SemanticTests(unittest.TestCase):
    def test_config_factory_selects_without_request_during_construction(self):
        calls = []
        def forbidden(request, timeout):
            calls.append(request)
            raise AssertionError('Construction must not request')
        first = m.provider_factory(CONFIGS, 'academy_hosted', environment={'ACADEMY_TEST_KEY': 'sentinel-dummy'}, transport=forbidden)
        second = m.provider_factory(CONFIGS, 'academy_local', environment={'ACADEMY_TEST_KEY': 'sentinel-dummy'}, transport=forbidden)
        self.assertEqual(first.settings.provider, 'hosted_compatible')
        self.assertEqual(second.settings.provider, 'ollama')
        self.assertEqual(calls, [])
        local_without_hosted_key = m.provider_factory(CONFIGS, 'academy_local', environment={}, transport=forbidden)
        self.assertEqual(local_without_hosted_key.settings.provider, 'ollama')
        self.assertNotIn('sentinel-dummy', repr(first.settings))
        with self.assertRaises(RuntimeError):
            first.chat([{'role': 'user', 'content': 'synthetic'}])
        self.assertEqual(calls, [])

    def test_unsupported_provider_options_and_missing_credential(self):
        bad_rows = [dict(CONFIGS['academy_local'], provider='unknown'),
                    dict(CONFIGS['academy_local'], temperature=.2),
                    dict(CONFIGS['academy_local'], credential_env='KEY'),
                    dict(CONFIGS['academy_hosted'], base_url='http://public.example/v1'),
                    dict(CONFIGS['academy_local'], base_url='http://localhost:11434/v1')]
        for row in bad_rows:
            with self.assertRaises(ValueError):
                m.load_provider_settings(row, {'ACADEMY_TEST_KEY': 'dummy'})
        with self.assertRaises(ValueError):
            m.load_provider_settings(CONFIGS['academy_hosted'], {})
        with self.assertRaises(ValueError):
            m.provider_factory(CONFIGS, 'missing', environment={'ACADEMY_TEST_KEY': 'dummy'})

    def test_factory_real_adapter_payloads_with_fake_transport(self):
        requests = []
        def transport(request, timeout):
            requests.append(request)
            if request.full_url.endswith('/chat/completions'):
                return io.BytesIO(b'{"model":"synthetic-hosted-model","choices":[{"finish_reason":"stop","message":{"role":"assistant","content":"synthetic hosted"}}]}')
            return io.BytesIO(b'{"done":true,"message":{"role":"assistant","content":"synthetic local"},"eval_count":3}')
        messages = [{'role': 'user', 'content': 'same synthetic input'}]
        for name in CONFIGS:
            client = m.provider_factory(CONFIGS, name, environment={'ACADEMY_TEST_KEY': 'dummy'}, allow_live=True, transport=transport)
            self.assertIn('synthetic', client.chat(messages)['content'])
        self.assertEqual([r.full_url for r in requests], ['https://example.invalid/v1/chat/completions','http://127.0.0.1:11434/api/chat'])
        self.assertEqual(json.loads(requests[0].data)['messages'], json.loads(requests[1].data)['messages'])
        self.assertFalse(json.loads(requests[1].data)['stream'])

    def test_native_ollama_rejects_unimplemented_tool_payload_without_transport(self):
        calls = []
        def transport(request, timeout):
            calls.append(request)
        client = m.provider_factory({'local': CONFIGS['academy_local']}, 'local', allow_live=True, transport=transport)
        with self.assertRaises(ValueError):
            client.chat([], tools=[m.CONTACT_TOOL])
        self.assertEqual(calls, [])

    def test_weighted_task_specific_worksheet_reliability_and_known_units(self):
        result = m.weighted_model_worksheet([rubric()], ['synthetic-a','synthetic-b'],
                  [measurement(),measurement('synthetic-b', successes=5, attempts=5, quality_score=5, latency_seconds=1, cost_amount=.001)])
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(result['recommendation'], 'synthetic-b')
        self.assertEqual(result['models'][0]['tasks'][0]['utilities']['reliability'], .8)
        self.assertEqual(result['measurement_scope'], 'SYNTHETIC_EXERCISE')

    def test_three_predeclared_tasks_and_aggregate_weights(self):
        tasks = [rubric('extract', task_weight=2), rubric('summarize', objective='Summarize approved text'),
                 rubric('tool', objective='Request the allowed tool', required_capabilities=('tool_calling',))]
        rows = [measurement(task='extract'), measurement(task='summarize'),
                measurement(task='tool', capabilities=('tool_calling',))]
        result = m.weighted_model_worksheet(tasks, ['synthetic-a'], rows)
        self.assertEqual(len(result['models'][0]['tasks']), 3)
        self.assertEqual(result['recommendation'], 'synthetic-a')

    def test_missing_metrics_no_imputed_zero_or_winner(self):
        result = m.weighted_model_worksheet([rubric()], ['synthetic-a','synthetic-b'], [measurement()])
        self.assertEqual(result['status'], 'incomplete')
        self.assertIsNone(result['recommendation'])
        self.assertIsNone(result['models'][1]['score'])
        self.assertIn('attempts', result['models'][1]['tasks'][0]['missing'])
        result = m.weighted_model_worksheet([rubric()], ['synthetic-a'], [measurement(latency_seconds=None)])
        self.assertIsNone(result['recommendation'])

    def test_invalid_units_dates_weights_and_reliability(self):
        with self.assertRaises(ValueError):
            m.weighted_model_worksheet([rubric(weights={'quality': 1})], ['synthetic-a'], [measurement()])
        for row in (measurement(currency_unit='different-unit'), measurement(observed_on='2026-11-11'),
                    measurement(successes=6, attempts=5), measurement(latency_seconds=float('nan')),
                    measurement(quality_score=True)):
            with self.assertRaises(ValueError):
                m.weighted_model_worksheet([rubric()], ['synthetic-a'], [row])
        with self.assertRaises(ValueError):
            m.weighted_model_worksheet([rubric()], ['synthetic-a'], [measurement(), measurement()])

    def test_task_capabilities_and_quality_can_exclude_every_model(self):
        result = m.weighted_model_worksheet([rubric()], ['synthetic-a'], [measurement(capabilities=())])
        self.assertFalse(result['models'][0]['eligible'])
        self.assertIsNone(result['recommendation'])

    def test_contact_input_consent_before_backend_effect(self):
        calls, contacts = [], []
        def backend(email, store):
            calls.append(email)
            return m.memory_contact_backend(email, store)
        for args in ({'email':'alex@example.invalid'}, {'email':'alex@example.invalid','consent':True}, {'email':99}):
            result = m.dispatch_contact(args, patterns.RequestState(), contacts, backend)
            self.assertFalse(result['ok'])
            self.assertEqual(result['error']['effect_status'], 'NOT_INVOKED')
        self.assertEqual(calls, [])
        self.assertEqual(contacts, [])

    def test_typed_contact_result_positive_and_idempotent(self):
        state, contacts = patterns.RequestState(True, 'alex@example.invalid'), []
        first = m.dispatch_contact({'email':'alex@example.invalid'}, state, contacts)
        second = m.dispatch_contact({'email':'alex@example.invalid'}, state, contacts)
        self.assertTrue(first['ok'])
        self.assertIsInstance(m.validate_contact_result(first['result'], 'alex@example.invalid'), m.ContactResult)
        self.assertEqual(first, second)
        self.assertEqual(contacts, ['alex@example.invalid'])

    def test_malformed_return_and_backend_exception_are_sanitized_unknown(self):
        state = patterns.RequestState(True, 'alex@example.invalid')
        def bad(email, contacts):
            contacts.append(email)
            return {'status': 'captured', 'synthetic': 'true', 'private': 'secret-sentinel'}
        contacts = []
        result = m.dispatch_contact({'email':'alex@example.invalid'}, state, contacts, bad)
        self.assertFalse(result['ok'])
        self.assertEqual(result['error']['effect_status'], 'UNKNOWN_DO_NOT_RETRY')
        self.assertEqual(contacts, ['alex@example.invalid'])
        self.assertNotIn('secret-sentinel', json.dumps(result))
        def broken(email, contacts):
            raise RuntimeError('secret-sentinel')
        self.assertEqual(m.dispatch_contact({'email':'alex@example.invalid'}, state, [], broken), result)

    def test_contact_result_rejects_invalid_types_values_and_extra_fields(self):
        raw = m.memory_contact_backend('alex@example.invalid', [])
        for wrong in (dict(raw, synthetic='true'),dict(raw, storage='external'),dict(raw, email='other@example.invalid'),
                      dict(raw, contact_id=123),dict(raw, extra=True)):
            with self.assertRaises(ValueError):
                m.validate_contact_result(wrong, 'alex@example.invalid')

    def test_same_turn_two_calls_successful_correlated_round_trip_model_double(self):
        def call(identity):
            return {'id':identity,'type':'function','function':{'name':'capture_contact','arguments':'{"email":"alex@example.invalid"}'}}
        model = FakeModel([{'role':'assistant','tool_calls':[call('batch-1'),call('batch-2')]},
                           {'role':'assistant','content':'Synthetic contact captured'}])
        contacts = []
        result = m.contact_tool_loop(model,'Capture the fictional contact',patterns.RequestState(True,'alex@example.invalid'),contacts)
        self.assertEqual(result['status'], 'completed')
        self.assertEqual(result['model_calls'], 2)
        tool_messages = [x for x in model.requests[1] if x['role']=='tool']
        self.assertEqual([x['tool_call_id'] for x in tool_messages], ['batch-1','batch-2'])
        self.assertTrue(all(json.loads(x['content'])['ok'] for x in tool_messages))
        self.assertEqual(contacts, ['alex@example.invalid'])
        self.assertIn('unverified', result['reason'])

    def test_unknown_backend_effect_stops_before_next_model_or_replay(self):
        call = {'id':'first','function':{'name':'capture_contact','arguments':'{"email":"alex@example.invalid"}'}}
        model = FakeModel([{'tool_calls':[call]},{'content':'never'}])
        invoked=[]
        def malformed(email, contacts):
            invoked.append(email)
            return {}
        result = m.contact_tool_loop(model,'Synthetic',patterns.RequestState(True,'alex@example.invalid'),[],backend=malformed)
        self.assertEqual(result['reason'], 'backend_effect_unknown')
        self.assertEqual(len(model.requests),1)
        self.assertEqual(len(invoked),1)

    def test_loop_derived_bound_and_duplicate_id(self):
        call = {'id':'same','function':{'name':'capture_contact','arguments':'{"email":"alex@example.invalid"}'}}
        model = FakeModel([{'tool_calls':[call,copy.deepcopy(call)]}])
        result = m.contact_tool_loop(model,'Synthetic',patterns.RequestState(True,'alex@example.invalid'),[])
        self.assertEqual(result['reason'],'invalid_or_duplicate_call_identity')
        self.assertEqual(len([x for x in result['events'] if x['event']=='tool_result']),1)
        with self.assertRaises(ValueError):
            m.contact_tool_loop(FakeModel([]),'Synthetic',patterns.RequestState(),[],max_calls=6)

if __name__ == '__main__':
    unittest.main()
