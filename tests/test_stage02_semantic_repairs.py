"""Author-only tests awaiting bounded coordinator QA; no live model call."""
import contextlib
from decimal import Decimal
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from urllib.error import HTTPError, URLError

PATH = Path(__file__).resolve().parents[1] / 'examples/stages02-04/stage02_configuration.py'
SPEC = importlib.util.spec_from_file_location('stage02_semantic_material', PATH)
m = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = m
SPEC.loader.exec_module(m)


def envelope(usage=True):
    value = {'model': 'synthetic-model', 'choices': [{'finish_reason': 'stop',
             'message': {'role': 'assistant', 'content': 'Synthetic hello'}}]}
    if usage:
        value['usage'] = {'prompt_tokens': 1000, 'completion_tokens': 2000}
    return value


class Fake:
    def __init__(self, outputs):
        self.outputs, self.requests = list(outputs), []
    def chat(self, messages):
        self.requests.append(messages)
        return self.outputs.pop(0)


class Stage02SemanticTests(unittest.TestCase):
    def test_explicit_dotenv_loading_alias_and_no_secret_output(self):
        stdout, stderr = io.StringIO(), io.StringIO()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / '.env'
            path.write_text('MODEL_API_KEY=synthetic-private-sentinel\nMODEL_NAME=synthetic-model\n', encoding='utf-8')
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                config = m.load_configuration(path, env={})
            self.assertEqual(config.api_key, 'synthetic-private-sentinel')
            self.assertNotIn('synthetic-private-sentinel', repr(config))
            self.assertEqual(stdout.getvalue() + stderr.getvalue(), '')
            alias = m.load_configuration(env={'OPENAI_API_KEY': 'dummy', 'OPENAI_MODEL': 'model'})
            self.assertEqual(alias.model, 'model')

    def test_dotenv_malformed_errors_never_echo_values(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / '.env'
            for content in ('MODEL_API_KEY=synthetic-private-sentinel\nUNKNOWN=synthetic-private-sentinel',
                            'MODEL_API_KEY="synthetic-private-sentinel',
                            'MODEL_API_KEY=synthetic-private-sentinel\nMODEL_API_KEY=duplicate',
                            'MODEL_API_KEY=$synthetic-private-sentinel'):
                path.write_text(content, encoding='utf-8')
                with self.assertRaises(ValueError) as caught:
                    m.load_configuration(path, env={})
                self.assertNotIn('synthetic-private-sentinel', str(caught.exception))
                self.assertIsNone(caught.exception.__cause__)

    def test_environment_override_conflict_and_endpoint_validation(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / '.env'
            path.write_text('MODEL_API_KEY=dummy\nMODEL_NAME=old\n', encoding='utf-8')
            self.assertEqual(m.load_configuration(path, env={'MODEL_NAME': 'new'}).model, 'new')
        for env in ({'MODEL_API_KEY': 'one', 'OPENAI_API_KEY': 'two', 'MODEL_NAME': 'model'},
                    {'MODEL_API_KEY': 'key', 'MODEL_NAME': 'model', 'MODEL_BASE_URL': 'http://public.example/v1'}):
            with self.assertRaises(ValueError):
                m.load_configuration(env=env)

    def test_ignore_declarations_not_mislabeled_git_proof(self):
        result = m.placeholder_tracking_check(PATH.parents[2])
        self.assertTrue(result['dotenv_ignore_declared'])
        self.assertTrue(result['template_allow_declared'])
        self.assertFalse(result['git_index_checked'])

    def test_response_usage_envelope_and_missing_status(self):
        full = m.observation_from_response(envelope(), 'req-synthetic-123')
        self.assertEqual(full.provider_request_id, 'req-synthetic-123')
        self.assertEqual(full.input_tokens, 1000)
        self.assertEqual(full.output_tokens, 2000)
        missing = m.observation_from_response(envelope(False))
        self.assertIsNone(missing.input_tokens)
        self.assertEqual(missing.usage_status, 'missing')
        broken = envelope()
        broken['usage']['prompt_tokens'] = True
        with self.assertRaises(ValueError):
            m.observation_from_response(broken)

    def test_observation_incomplete_or_invalid(self):
        for value in ({}, {'choices': []}, {'choices': [{'finish_reason': 'length', 'message': {}}]}):
            with self.assertRaises(ValueError):
                m.observation_from_response(value)

    def test_usage_worksheet_cost_and_count_stops(self):
        ledger = m.UsageLedger(maximum_calls=1, maximum_tokens=4000)
        ledger.reserve('r1', 1000, 2000)
        record = ledger.record('r1', m.observation_from_response(envelope()))
        self.assertEqual(record['example_cost'], Decimal('0.005'))
        self.assertEqual(record['total_tokens'], 3000)
        with self.assertRaises(RuntimeError):
            ledger.reserve('r2', 1, 1)

    def test_unknown_usage_never_recorded_as_zero_and_stops(self):
        ledger = m.UsageLedger()
        ledger.reserve('r1', 1000, 2000)
        result = ledger.record('r1', m.observation_from_response(envelope(False)))
        self.assertIsNone(result['actual_tokens'])
        self.assertEqual(ledger.records, {})
        with self.assertRaises(RuntimeError):
            ledger.reserve('r2', 1, 1)

    def test_reservation_and_observed_overrun(self):
        ledger = m.UsageLedger(maximum_tokens=100)
        with self.assertRaises(RuntimeError):
            ledger.reserve('too-large', 100, 1)
        ledger = m.UsageLedger()
        ledger.reserve('r1', 10, 10)
        ledger.record('r1', m.observation_from_response(envelope()))
        self.assertEqual(ledger.stop_reason, 'observed_usage_exceeds_planned_limit')
        with self.assertRaises(RuntimeError):
            ledger.reserve('r2', 1, 1)

    def test_remote_unknown_consumes_pending_admission(self):
        ledger = m.UsageLedger()
        ledger.reserve('r1', 100, 100)
        ledger.record_unknown('r1')
        self.assertEqual(ledger.pending['r1']['outcome'], 'remote_outcome_unknown')
        with self.assertRaises(RuntimeError):
            ledger.reserve('r2', 1, 1)

    def test_real_http_adapter_maps_injected_http_errors(self):
        config = m.Configuration('synthetic-model', 'https://example.invalid/v1', 'synthetic-private-sentinel')
        for status, category in ((429, 'rate_limited'), (401, 'authentication'), (403, 'authentication'),
                                 (400, 'invalid_input'), (422, 'invalid_input'), (503, 'http_failure_no_auto_retry')):
            def transport(request, timeout, status=status):
                raise HTTPError(request.full_url, status, 'synthetic-private-sentinel',
                                {'Retry-After': '2', 'x-request-id': 'req-synthetic'}, None)
            client = m.ObservedCompatibleModel(config, allow_live=True, transport=transport)
            with self.assertRaises(m.ModelBoundaryError) as caught:
                client.chat([{'role': 'user', 'content': 'synthetic'}])
            self.assertEqual(caught.exception.category, category)
            self.assertEqual(caught.exception.request_id, 'req-synthetic')
            self.assertNotIn('synthetic-private-sentinel', str(caught.exception))
            self.assertIsNone(caught.exception.__cause__)

    def test_actual_adapter_success_metadata_with_fake_transport(self):
        requests = []
        class Response(io.BytesIO):
            headers = {'x-request-id': 'req-observed'}
        def transport(request, timeout):
            requests.append(request)
            return Response(json.dumps(envelope()).encode())
        client = m.ObservedCompatibleModel(m.Configuration('model', 'https://example.invalid/v1', 'secret'), allow_live=True, transport=transport)
        observation = client.observe([{'role': 'user', 'content': 'hello'}])
        self.assertEqual(observation.provider_request_id, 'req-observed')
        self.assertEqual(observation.usage_status, 'reported')
        self.assertEqual(len(requests), 1)

    def test_malformed_response_and_timeout_distinct(self):
        config = m.Configuration('model', 'https://example.invalid/v1', 'secret')
        def malformed(request, timeout):
            return io.BytesIO(b'not JSON')
        client = m.ObservedCompatibleModel(config, allow_live=True, transport=malformed)
        with self.assertRaises(m.ModelBoundaryError) as caught:
            client.chat([])
        self.assertEqual(caught.exception.category, 'invalid_response')
        calls = []
        def timeout(request, timeout):
            calls.append(1)
            raise TimeoutError('private detail')
        client = m.ObservedCompatibleModel(config, allow_live=True, transport=timeout)
        with self.assertRaises(m.ModelBoundaryError) as caught:
            m.qualified_retry(lambda: client.chat([]))
        self.assertEqual(caught.exception.category, 'remote_outcome_unknown')
        self.assertEqual(len(calls), 1)

    def test_retry_after_and_elapsed_admission_with_fake_clock(self):
        now, calls = [0.0], []
        def sleep(seconds):
            now[0] += seconds
        def operation():
            calls.append(1)
            if len(calls) == 1:
                raise m.ModelBoundaryError('rate_limited', retry_after=2)
            return 'synthetic success'
        self.assertEqual(m.qualified_retry(operation, sleep=sleep, clock=lambda: now[0]), 'synthetic success')
        self.assertEqual(now[0], 2)
        def too_long():
            raise m.ModelBoundaryError('rate_limited', retry_after=90)
        with self.assertRaises(m.ModelBoundaryError) as caught:
            m.qualified_retry(too_long, sleep=sleep, clock=lambda: now[0])
        self.assertEqual(caught.exception.category, 'retry_hint_exceeds_budget')
        self.assertEqual(m.retry_after_seconds('NaN'), None)

    def test_terminal_authentication_never_retries(self):
        calls = []
        def operation():
            calls.append(1)
            raise m.ModelBoundaryError('authentication')
        with self.assertRaises(m.ModelBoundaryError):
            m.qualified_retry(operation)
        self.assertEqual(len(calls), 1)

    def test_typed_requirements_chain_uses_validated_first_result(self):
        model = Fake([{'content': '{"requirements":[{"id":"r1","text":"Export CSV"}]}'}, {'content': '- Export CSV'}])
        result = m.requirements_chain(model, 'synthetic note')
        self.assertEqual(result['status'], 'completed')
        self.assertEqual([x['step'] for x in result['trace']], ['extract', 'validate', 'format'])
        self.assertIn('Export CSV', model.requests[1][1]['content'])

    def test_schema_invalid_nonempty_first_blocks_second(self):
        for value in ('nonempty not JSON', '{"requirements":"wrong"}', '{"requirements":[{"id":"a","text":"X","extra":true}]}'):
            model = Fake([{'content': value}, {'content': 'must not run'}])
            result = m.requirements_chain(model, 'synthetic note')
            self.assertEqual(result['status'], 'blocked')
            self.assertEqual(len(model.requests), 1)

if __name__ == '__main__':
    unittest.main()
