"""New semantic boundaries; authored for the sole central QA owner to execute.

Synthetic event sources/model counters are explicitly fixtures. Real SDK objects
are tested only when installed; skips never count as actual SDK evidence.
"""
import asyncio
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock

EXAMPLE = Path(__file__).resolve().parents[1] / 'examples/stages06-07'
sys.path.insert(0, str(EXAMPLE))
import workflows as workflow
from stream_receipt import StreamReceipt, consume_sdk_stream


def synthetic_delta(text):
    return SimpleNamespace(type='raw_response_event', data=SimpleNamespace(
        type='response.output_text.delta', delta=text))


class SyntheticEventSource:
    """Application-consumer fixture, never a simulated provider observation."""
    def __init__(self, events, failure=None):
        self.events, self.failure = events, failure
        self.cancelled = False
        self.closed = False

    def cancel(self, *, mode):
        if mode != 'immediate':
            raise ValueError('fixture only supports immediate cleanup')
        self.cancelled = True

    async def stream_events(self):
        try:
            for event in self.events:
                if self.cancelled:
                    break
                yield event
            if self.failure and not self.cancelled:
                raise self.failure
        finally:
            self.closed = True


class StreamAndFallbackTests(unittest.IsolatedAsyncioTestCase):
    async def test_empty_and_unknown_events_do_not_invent_text(self):
        source = SyntheticEventSource([SimpleNamespace(type='new_sdk_event'),
                                       SimpleNamespace(), synthetic_delta(''), synthetic_delta('actual fixture')])
        receipt = await consume_sdk_stream(source)
        self.assertEqual(receipt.status, 'complete')
        self.assertEqual(receipt.partial_text, 'actual fixture')
        self.assertEqual(receipt.ignored_events, 2)
        self.assertTrue(source.closed)

    async def test_failure_after_partial_output_never_becomes_final(self):
        source = SyntheticEventSource([synthetic_delta('partial')], RuntimeError('synthetic failure'))
        receipt = await consume_sdk_stream(source)
        self.assertEqual(receipt.partial_text, 'partial')
        self.assertEqual(receipt.status, 'failed')
        self.assertEqual(receipt.error_type, 'RuntimeError')
        self.assertTrue(source.cancelled)
        self.assertTrue(receipt.cleanup_complete)

    async def test_user_cancel_stops_deltas_and_drains_same_source(self):
        source = SyntheticEventSource([synthetic_delta('first'), synthetic_delta('second')])
        receipt = await consume_sdk_stream(source, cancel_after_deltas=1)
        self.assertEqual(receipt.status, 'cancelled')
        self.assertEqual(receipt.partial_text, 'first')
        self.assertTrue(source.closed)
        self.assertTrue(receipt.cleanup_complete)

    async def test_task_cancellation_propagates_after_owned_cleanup(self):
        entered = asyncio.Event()
        class WaitingSource(SyntheticEventSource):
            async def stream_events(self):
                try:
                    entered.set()
                    await asyncio.Event().wait()
                    yield synthetic_delta('unreachable')
                finally:
                    self.closed = True
        source = WaitingSource([])
        receipt = StreamReceipt()
        task = asyncio.create_task(consume_sdk_stream(source, receipt=receipt))
        await entered.wait()
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        self.assertEqual(receipt.status, 'cancelled')
        self.assertTrue(source.cancelled)
        self.assertTrue(source.closed)

    async def test_explicit_fallback_preserves_healthy_fact_and_failed_provenance(self):
        ctx = workflow.RequestContext('REQ-001', 'KB-01', '2026-11-demo')
        broken = AsyncMock(side_effect=workflow.TransientLookupError())
        result = await workflow.specialists_with_fallback(ctx, operations={'research': broken})
        self.assertEqual(broken.await_count, 2)
        self.assertIsNone(result['results'][0]['result'])
        self.assertEqual(result['results'][1]['result']['source'], 'synthetic-policy')
        self.assertEqual(result['unresolved'], ['research'])
        fallback = result['fallbacks'][0]
        self.assertEqual(fallback['failed_role'], 'research')
        self.assertEqual(fallback['trigger'], 'TransientLookupError')
        self.assertEqual(fallback['source'], 'application-failure-policy-v1')
        self.assertFalse(fallback['facts_recovered'])
        self.assertFalse(fallback['sent'])

    async def test_permanent_schema_error_uses_no_retry_and_distinct_draft(self):
        ctx = workflow.RequestContext('REQ-001', 'KB-01', '2026-11-demo')
        invalid = AsyncMock(return_value={'request_id': 'REQ-999'})
        result = await workflow.specialists_with_fallback(ctx, operations={'policy': invalid})
        self.assertEqual(invalid.await_count, 1)
        self.assertEqual(result['fallbacks'][0]['action'], 'draft_manual_review')
        self.assertEqual(result['fallbacks'][0]['trigger'], 'ValueError')

    async def test_connected_application_lineage_is_one_correlated_non_sdk_run(self):
        result = await workflow.connected_application_run(workflow.RequestContext('REQ-001', 'KB-01', '2026-11-demo'))
        self.assertEqual(result['mode'], 'deterministic-application-lineage-not-sdk')
        self.assertEqual(result['owner'], 'shipping')
        self.assertEqual(len(set(e['run_id'] for e in result['trace'])), 1)
        self.assertTrue({'delegation', 'tool', 'handoff', 'synthesis', 'terminal'} <= {e['kind'] for e in result['trace']})
        self.assertEqual(result['source_ids'], ['synthetic-inventory', 'synthetic-policy', 'synthetic-shipping'])
        spans = {e['span_id'] for e in result['trace']}
        self.assertTrue(all(e['parent_span_id'] is None or e['parent_span_id'] in spans for e in result['trace']))


@unittest.skipUnless(importlib.util.find_spec('agents'), 'Central QA must select installed SDK environment')
class ActualSDKSemanticTests(unittest.IsolatedAsyncioTestCase):
    def test_structured_tool_return_validates_shape_variants_and_current_facts(self):
        import sdk_adapter as sdk
        valid = workflow.lookup_course('ECA-101')
        self.assertEqual(sdk.validated_catalogue_result(valid, 'ECA-101'), valid)
        self.assertEqual(sdk.validated_catalogue_result({'found': False, 'course': None}, 'ECA-999'),
                         {'found': False, 'course': None})
        cases = [dict(valid, found='yes'), dict(valid, extra=True), {'found': True, 'course': None},
                 {'found': False, 'course': valid['course']},
                 {'found': True, 'course': dict(valid['course'], title='Invented but well typed')},
                 {'found': True, 'course': dict(valid['course'], prerequisites='wrong')},
                 {'found': True, 'course': dict(valid['course'], level='invented')},
                 workflow.lookup_course('ECA-201')]
        for malformed in cases:
            with self.subTest(value=malformed), self.assertRaises(ValueError):
                sdk.validated_catalogue_result(malformed, 'ECA-101')

    def test_actual_complete_sdk_graph_has_tools_and_continuation_owner(self):
        import sdk_adapter as sdk
        agents = sdk.make_agents('explicit-offline-construction')
        self.assertEqual([tool.name for tool in agents['complete'].tools], ['ask_inventory', 'ask_policy'])
        self.assertEqual(agents['complete'].handoffs[0].agent_name, 'Delivery synthesizer')
        self.assertEqual(agents['synthesizer'].tools[0].name, 'shipping')

    async def test_real_hooks_keep_missing_usage_distinct_from_zero(self):
        from sdk_observation import ObservationHooks, usage_fields
        hooks = ObservationHooks()
        context = SimpleNamespace()
        agent = SimpleNamespace(name='synthetic-callback-fixture')
        self.assertIsNone(usage_fields(None)['input_tokens'])
        await hooks.on_llm_start(context, agent, 'not retained', [])
        # Explicit synthetic SDK-callback fixture; not a provider response.
        response = SimpleNamespace(usage=SimpleNamespace(requests=1, input_tokens=12,
                                                        output_tokens=4, total_tokens=16), response_id=None)
        await hooks.on_llm_end(context, agent, response)
        call = hooks.export()['calls'][0]
        self.assertEqual(call['usage']['total_tokens'], 16)
        self.assertGreaterEqual(call['duration_seconds'], 0)
        self.assertIsNone(call['response_id'])

    def test_actual_sdk_local_span_export_has_lineage_without_private_text(self):
        from agents import set_trace_processors, trace, function_span
        from sdk_observation import LocalSDKTraceProcessor
        collector = LocalSDKTraceProcessor()
        set_trace_processors([collector])
        try:
            with trace('Academy local SDK span contract'):
                with function_span('outer', input='PRIVATE_SENTINEL'):
                    with function_span('inner', output='PRIVATE_SENTINEL'):
                        pass
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / 'actual-sdk-spans.json'
                collector.write(path)
                text = path.read_text()
                proof = json.loads(text)
                self.assertNotIn('PRIVATE_SENTINEL', text)
                self.assertFalse(proof['hosted_upload_proven'])
                self.assertEqual(len(proof['spans']), 2)
                ids = {span['id'] for span in proof['spans']}
                self.assertTrue(any(span['parent_id'] in ids for span in proof['spans']))
                with self.assertRaises(FileExistsError):
                    collector.write(path)
        finally:
            set_trace_processors([])

    def test_separate_process_actual_runner_sqlite_history_and_unrelated_control(self):
        with tempfile.TemporaryDirectory() as directory:
            database = str(Path(directory) / 'course-owned-sdk.sqlite')
            observations = []
            for step in ('seed', 'followup', 'control'):
                result = subprocess.run([sys.executable, str(EXAMPLE / 'session_contract_probe.py'),
                                         '--db', database, '--step', step],
                                        capture_output=True, text=True, check=True, timeout=30)
                observations.append(json.loads(result.stdout))
            self.assertTrue(observations[1]['result']['prior_marker_present'])
            self.assertFalse(observations[2]['result']['prior_marker_present'])
            self.assertEqual([row['provider_calls'] for row in observations], [0, 0, 0])
            self.assertEqual(observations[1]['stored_items'], 4)

    def test_lineage_instructions_are_not_a_substitute_for_observed_callbacks(self):
        from sdk_observation import complete_lineage_observed
        self.assertFalse(complete_lineage_observed([]))
        events = [{'kind': 'tool_end', 'tool': 'ask_inventory'},
                  {'kind': 'tool_end', 'tool': 'ask_policy'},
                  {'kind': 'handoff', 'to_agent': 'Delivery synthesizer'},
                  {'kind': 'tool_end', 'tool': 'shipping'},
                  {'kind': 'agent_final', 'agent': 'Delivery synthesizer'}]
        self.assertTrue(complete_lineage_observed(events))
        self.assertFalse(complete_lineage_observed(events[2:] + events[:2]))


if __name__ == '__main__':
    unittest.main()
