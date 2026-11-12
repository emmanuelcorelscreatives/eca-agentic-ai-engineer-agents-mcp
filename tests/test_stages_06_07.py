"""Offline acceptance checks; no network or credentials required."""
import asyncio
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import AsyncMock

EXAMPLE = Path(__file__).resolve().parents[1] / 'examples/stages06-07'
sys.path.insert(0, str(EXAMPLE))
import workflows as w


class Stage06Tests(unittest.IsolatedAsyncioTestCase):
    def test_schema_rejects_invalid_extra_and_level(self):
        row = json.loads(w.CATALOG.read_text())[0]
        for mutated in [dict(row, extra=1), dict(row, level='invented'), dict(row, course_id=1),
                        dict(row, prerequisites='ECA-101'), dict(row, title='')]:
            with self.assertRaises(ValueError):
                w.Course.parse(mutated)

    def test_catalogue_known_unknown_invalid(self):
        self.assertEqual(w.lookup_course('ECA-101')['course']['title'], 'Python Foundations')
        self.assertEqual(w.lookup_course('ECA-999'), {'found': False, 'course': None})
        with self.assertRaises(ValueError):
            w.lookup_course("'; DROP TABLE courses")

    async def test_run_envelope_and_failure_trace(self):
        result = await w.catalogue_run('ECA-201')
        self.assertEqual(result['mode'], 'deterministic-offline')
        self.assertIsNone(result['usage'])
        self.assertEqual(result['events'][-1]['status'], 'complete')
        trace = w.LocalTrace()
        with self.assertRaises(ValueError):
            await w.catalogue_run('wrong', trace)
        self.assertEqual(trace.events[-1]['status'], 'failed')

    async def test_synthetic_stream_typed_and_ordered(self):
        events = [e async for e in w.offline_stream('ECA-101')]
        self.assertEqual(events[0]['type'], 'agent_updated_stream_event')
        self.assertEqual(events[-1]['type'], 'run_item_stream_event')
        self.assertTrue(all(e['synthetic'] for e in events))
        text = ''.join(e.get('delta', '') for e in events)
        self.assertEqual(json.loads(text), w.lookup_course('ECA-101'))

    def test_memory_persists_across_instances_and_isolates_sessions(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'sessions.sqlite'
            a = w.SQLiteHistory(path)
            a.add('alice', 'user', 'ECA-101')
            a.add('alice', 'assistant', 'Python Foundations')
            a.add('bob', 'user', 'ECA-301')
            b = w.SQLiteHistory(path)
            self.assertEqual([x['role'] for x in b.items('alice')], ['user', 'assistant'])
            self.assertEqual(len(b.items('bob')), 1)
            b.clear('alice')
            self.assertEqual(b.items('alice'), [])
            self.assertEqual(len(b.items('bob')), 1)


class Stage07Tests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.ctx = w.RequestContext('REQ-001', 'KB-01', '2026-11-demo')

    async def test_parallel_overlap_with_barrier_and_result_ownership(self):
        entered = set()
        barrier = asyncio.Event()
        async def op(role, operation):
            entered.add(role)
            if len(entered) == 2:
                barrier.set()
            await barrier.wait()
            return w.capability(role, operation, self.ctx)
        result = await asyncio.wait_for(w.specialists(self.ctx, operations={
            'research': lambda: op('research', 'inventory'),
            'policy': lambda: op('policy', 'policy')}), 2)
        self.assertEqual([r['role'] for r in result['results']], ['research', 'policy'])
        self.assertEqual(result['unresolved'], [])

    async def test_as_tool_manager_ownership_vs_handoff_ownership(self):
        self.assertEqual((await w.specialists(self.ctx))['owner'], 'manager')
        handed = await w.handoff_shipping(self.ctx, w.LocalTrace())
        self.assertEqual(handed['owner'], 'shipping')
        self.assertEqual(handed['trace'][1]['kind'], 'handoff')

    def test_capabilities_not_overridden_by_untrusted_text(self):
        case = json.loads(w.CASES.read_text())[2]
        self.assertIn('Ignore', case['question'])
        for action in ['send_message', 'policy', case['question']]:
            with self.assertRaises(PermissionError):
                w.capability('research', action, self.ctx)
        with self.assertRaises(ValueError):
            w.RequestContext('REQ-001', 'KB-01', 'invented')

    async def test_transient_only_bounded_retries(self):
        mock = AsyncMock(side_effect=[w.TransientLookupError(), {'ok': True}])
        self.assertEqual(await w.bounded_read(mock), {'ok': True})
        self.assertEqual(mock.await_count, 2)
        permanent = AsyncMock(side_effect=ValueError('bad schema'))
        with self.assertRaises(ValueError):
            await w.bounded_read(permanent)
        self.assertEqual(permanent.await_count, 1)
        exhausted = AsyncMock(side_effect=w.TransientLookupError())
        with self.assertRaises(w.TransientLookupError):
            await w.bounded_read(exhausted, attempts=3)
        self.assertEqual(exhausted.await_count, 3)

    async def test_timeout_cancels_and_awaits_cleanup(self):
        cleaned = asyncio.Event()
        async def stuck():
            try:
                await asyncio.Event().wait()
            finally:
                cleaned.set()
        with self.assertRaises(TimeoutError):
            await w.bounded_read(stuck, timeout=.01)
        self.assertTrue(cleaned.is_set())
        active = [t for t in asyncio.all_tasks() if t is not asyncio.current_task() and not t.done()]
        self.assertEqual(active, [])

    async def test_cross_request_and_invalid_schema_become_honest_partial(self):
        wrong = AsyncMock(return_value={'request_id': 'REQ-999', 'stock': 1})
        result = await w.specialists(self.ctx, operations={'research': wrong})
        self.assertEqual(result['unresolved'], ['research'])
        self.assertIsNone(result['results'][0]['result'])
        self.assertIsNotNone(result['results'][1]['result'])
        invalid = AsyncMock(return_value={'request_id': self.ctx.request_id, 'stock': 'lots'})
        self.assertEqual((await w.specialists(self.ctx, operations={'research': invalid}))['unresolved'], ['research'])

    async def test_trace_correlation_privacy_and_complete_run(self):
        result = await w.specialists(self.ctx)
        events = result['trace']
        self.assertEqual(len({x['run_id'] for x in events}), 1)
        spans = {x['span_id'] for x in events}
        self.assertTrue(all(x['parent_span_id'] is None or x['parent_span_id'] in spans for x in events))
        self.assertTrue({'start', 'delegation', 'tool', 'synthesis', 'terminal'} <= {x['kind'] for x in events})
        trace = w.LocalTrace()
        with self.assertRaises(ValueError):
            trace.emit('input', user_text='SENTINEL_PRIVATE')
        self.assertNotIn('SENTINEL_PRIVATE', json.dumps(trace.events))

    async def test_comparison_never_claims_provider_benchmark(self):
        result = await w.orchestration_comparison(self.ctx)
        self.assertEqual(result['measurement']['kind'], 'local-event-count')
        self.assertIsNone(result['measurement']['provider_latency'])


@unittest.skipUnless(importlib.util.find_spec('agents'), 'Optional openai-agents package not installed')
class ActualSDKOfflineTests(unittest.IsolatedAsyncioTestCase):
    async def test_build_actual_sdk_tools_and_strict_schemas_without_network(self):
        import sdk_adapter as s
        a = s.make_agents('explicit-model-for-offline-construction')
        self.assertEqual(a['catalogue'].tools[0].name, 'catalogue_lookup')
        self.assertTrue(a['catalogue'].tools[0].params_json_schema['additionalProperties'] is False)
        self.assertEqual(len(a['manager'].tools), 2)
        self.assertEqual(a['manager'].tools[0].params_json_schema['required'], ['question'])
        self.assertEqual(len(a['triage'].handoffs), 1)
        from agents.tool_context import ToolContext
        text = await a['catalogue'].tools[0].on_invoke_tool(ToolContext(context=None, tool_name='catalogue_lookup', tool_call_id='offline-1', tool_arguments='{"course_id":"ECA-101"}'), '{"course_id":"ECA-101"}')
        self.assertIn('Python Foundations', str(text))
        # Actual function tool invocation; not a fake provider or paid request.
        inventory = await a['research'].tools[0].on_invoke_tool(
            ToolContext(context=w.RequestContext('REQ-001', 'KB-01', '2026-11-demo'), tool_name='inventory', tool_call_id='offline-2', tool_arguments='{}'), '{}')
        self.assertIn('synthetic-inventory', str(inventory))

    async def test_actual_sdk_sqlite_session_restart_and_isolation(self):
        from agents import SQLiteSession
        with tempfile.TemporaryDirectory() as d:
            path = str(Path(d) / 'sdk.sqlite')
            a = SQLiteSession('a', db_path=path)
            await a.add_items([{'role': 'user', 'content': 'ECA-101'}])
            b = SQLiteSession('b', db_path=path)
            self.assertEqual(await b.get_items(), [])
            reopened = SQLiteSession('a', db_path=path)
            self.assertEqual((await reopened.get_items())[0]['content'], 'ECA-101')
            await reopened.clear_session()
            self.assertEqual(await a.get_items(), [])

    async def test_live_runner_entrypoint_with_fake_preserves_config(self):
        import sdk_adapter as s
        from types import SimpleNamespace
        from unittest.mock import patch
        calls = []
        async def fake_run(agent, prompt, **kwargs):
            calls.append((agent.name, kwargs))
            return SimpleNamespace(final_output='FAKE OUTPUT', last_agent=agent)
        with tempfile.TemporaryDirectory() as d, patch.dict('os.environ', {'OPENAI_API_KEY': 'fake-not-a-key'}), patch.object(s.Runner, 'run', side_effect=fake_run):
            await s.run_live(model='explicit-offline-model', mode='manager',
                             db=str(Path(d)/'session.sqlite'), hosted_tracing=False, stream=False)
        self.assertEqual(calls[0][0], 'Support manager')
        self.assertTrue(calls[0][1]['run_config'].tracing_disabled)
        self.assertFalse(calls[0][1]['run_config'].trace_include_sensitive_data)
        self.assertEqual(calls[0][1]['max_turns'], 8)


if __name__ == '__main__':
    unittest.main()
