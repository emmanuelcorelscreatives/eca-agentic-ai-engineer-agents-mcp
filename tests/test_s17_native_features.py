"""Actual LangGraph SDK tests, authored for central execution, no provider calls.

The standard-library course suite can discover this optional integration module
without installing LangGraph. A skipped SDK test is NOT semantic execution proof;
the separately retained installed-SDK results establish the native behavior.
"""
from importlib.util import find_spec
import unittest

OPTIONAL_SDK_MODULES = ('langchain_core', 'langgraph', 'langsmith')
MISSING_SDK_MODULES = tuple(name for name in OPTIONAL_SDK_MODULES if find_spec(name) is None)
SDK_AVAILABLE = not MISSING_SDK_MODULES

if SDK_AVAILABLE:
    # Do not hide incompatible SDK APIs or product import failures as skips.
    # Once the named optional packages exist, their imports must actually work.
    from langchain_core.messages import AIMessage, ToolMessage
    from langgraph.checkpoint.memory import InMemorySaver
    from langsmith import tracing_context

    from examples.s17.native_graph_features import (
        build_parallel_graph, build_recovery_graph, build_tool_loop,
    )


@unittest.skipUnless(SDK_AVAILABLE, 'Optional SDK unavailable: ' + ', '.join(MISSING_SDK_MODULES)
                     + '; skipped integration is not semantic PASS')
class NoTelemetry(unittest.TestCase):
    def setUp(self):
        self.trace_context = tracing_context(enabled=False)
        self.trace_context.__enter__()
        self.addCleanup(self.trace_context.__exit__, None, None, None)


class NativeParallelEvidence(NoTelemetry):
    def test_sibling_updates_and_and_join(self):
        graph = build_parallel_graph()
        updates = list(graph.stream({'evidence': [], 'audit': []}, stream_mode='updates'))
        self.assertEqual(set(updates[0]) | set(updates[1]), {'privacy', 'course'})
        self.assertEqual(set(updates[2]), {'compose'})
        self.assertEqual(updates[2]['compose']['audit'], ['joined:2'])
        # Both nodes have crossed the real two-party barrier for this to finish.
        self.assertEqual(len(updates), 3)
        edges = {(edge.source, edge.target) for edge in graph.get_graph().edges}
        self.assertTrue({('__start__', 'privacy'), ('__start__', 'course'),
                         ('privacy', 'compose'), ('course', 'compose')} <= edges)

    def test_reducer_checkpoint_has_both_evidence_records(self):
        graph = build_parallel_graph(checkpointer=InMemorySaver())
        config = {'configurable': {'thread_id': 's17-two-siblings'}}
        result = graph.invoke({'evidence': [], 'audit': []}, config)
        self.assertEqual([row['id'] for row in result['evidence']], ['course', 'privacy'])
        history = list(graph.get_state_history(config))
        self.assertTrue(any(set(snapshot.next) == {'privacy', 'course'} for snapshot in history))
        self.assertTrue(any(snapshot.next == ('compose',) and len(snapshot.values['evidence']) == 2
                            for snapshot in history))

    def test_duplicate_identity_is_idempotent(self):
        result = build_parallel_graph(duplicate=True).invoke({'evidence': [], 'audit': []})
        self.assertEqual(len(result['evidence']), 1)
        self.assertEqual(result['audit'][-1], 'joined:1')

    def test_conflicting_identity_fails_before_compose(self):
        with self.assertRaisesRegex(ValueError, 'conflicting evidence identity'):
            build_parallel_graph(conflict=True).invoke({'evidence': [], 'audit': []})


class NativeToolAndLoop(NoTelemetry):
    def test_real_tool_node_preserves_call_identity(self):
        graph = build_tool_loop()
        result = graph.invoke({'messages': [], 'rounds': 0, 'audit': []})
        self.assertIsInstance(result['messages'][0], AIMessage)
        self.assertIsInstance(result['messages'][1], ToolMessage)
        self.assertEqual(result['messages'][0].tool_calls[0]['id'],
                         result['messages'][1].tool_call_id)
        self.assertEqual(result['messages'][1].name, 'academy_product')
        self.assertIn('sidekick', result['messages'][1].content)
        self.assertEqual(result['rounds'], 1)
        self.assertEqual(result['status'], 'complete')
        edges = {(edge.source, edge.target) for edge in graph.get_graph().edges}
        self.assertIn(('tools', 'reason'), edges)
        self.assertIn(('reason', 'tools'), edges)

    def test_never_finishing_message_producer_stops_at_explicit_budget(self):
        result = build_tool_loop(max_rounds=3, never_finish=True).invoke(
            {'messages': [], 'rounds': 0, 'audit': []}, {'recursion_limit': 20})
        calls = [message for message in result['messages'] if isinstance(message, ToolMessage)]
        self.assertEqual([message.tool_call_id for message in calls],
                         ['academy-call-1', 'academy-call-2', 'academy-call-3'])
        self.assertEqual(result['rounds'], 3)
        self.assertEqual(result['status'], 'budget-exhausted')
        self.assertFalse(result['messages'][-1].tool_calls)

    def test_invalid_loop_budget(self):
        for budget in (0, 9, True):
            with self.assertRaises(ValueError):
                build_tool_loop(max_rounds=budget)


class NativeRecoveryEdges(NoTelemetry):
    def test_controlled_transient_failure_routes_retry_then_success(self):
        graph = build_recovery_graph(failure='transient')
        events = list(graph.stream({'attempts': 0, 'audit': []}, stream_mode='updates'))
        self.assertEqual([next(iter(event)) for event in events],
                         ['attempt', 'retry', 'attempt', 'finish'])
        self.assertEqual(events[0]['attempt']['outcome'], 'retryable')
        self.assertEqual(events[2]['attempt']['attempts'], 2)
        self.assertEqual(events[2]['attempt']['outcome'], 'success')

    def test_exhausted_transient_path_is_labelled_fallback(self):
        result = build_recovery_graph(failure='permanent', max_attempts=2).invoke(
            {'attempts': 0, 'audit': []})
        self.assertEqual(result['attempts'], 2)
        self.assertEqual(result['outcome'], 'fallback')
        self.assertIn('Cached synthetic', result['answer'])
        self.assertNotIn('finish:success', result['audit'])

    def test_invalid_data_routes_intervention_without_retry(self):
        result = build_recovery_graph(failure='invalid').invoke({'attempts': 0, 'audit': []})
        self.assertEqual(result['attempts'], 1)
        self.assertEqual(result['outcome'], 'intervention')
        self.assertNotIn('retry:scheduled', result['audit'])

    def test_exhausted_path_can_require_user_intervention(self):
        result = build_recovery_graph(failure='permanent', exhausted_action='intervention').invoke(
            {'attempts': 0, 'audit': []})
        self.assertEqual(result['attempts'], 2)
        self.assertEqual(result['outcome'], 'intervention')


if __name__ == '__main__':
    unittest.main()
