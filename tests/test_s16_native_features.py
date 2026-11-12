"""Opt-in genuine SDK tests with a local deterministic model; zero provider calls."""
import os
import unittest

SDK_ENABLED = os.environ.get('COURSE_SDK_OFFLINE') == '1'

if SDK_ENABLED:
    from typing import Any
    from pydantic import Field, ValidationError
    from langchain_core.language_models.chat_models import BaseChatModel
    from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage, ToolMessage
    from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult
    from langchain_core.utils.function_calling import convert_to_openai_tool
    from examples.s16.native_features import (PageAnswer, academy_page, bind_and_inspect,
        invoke_and_stream, make_agent, prune_thread, recent_turns, structured_answer, thread_config)

    class DeterministicAcademyModel(BaseChatModel):
        """Explicit SDK fixture, never a simulated provider observation."""
        schemas: list[dict] = Field(default_factory=list)
        seen: list[Any] = Field(default_factory=list)
        behavior: str = 'normal'

        @property
        def _llm_type(self):
            return 'deterministic-academy-native-sdk-fixture'

        def bind_tools(self, tools, *, tool_choice=None, **kwargs):
            return self.model_copy(update={'schemas': [convert_to_openai_tool(t) for t in tools]})

        def _generate(self, messages, stop=None, run_manager=None, **kwargs):
            self.seen.append(list(messages))
            names = [schema['function']['name'] for schema in self.schemas]
            if 'PageAnswer' in names:
                args = {'answer': 'Use an isolated profile. Never use personal account data.', 'citations': ['privacy']}
                if self.behavior == 'missing':
                    args.pop('answer')
                elif self.behavior == 'wrong-type':
                    args['answer'] = 123
                elif self.behavior == 'unknown-citation':
                    args['citations'] = ['invented']
                answer = AIMessage(content='', tool_calls=[{'id': 'structured-fixture', 'name': 'PageAnswer', 'args': args}])
            elif names and not isinstance(messages[-1], ToolMessage):
                args = {'page_id': 'privacy' if self.behavior != 'bad-tool' else 'personal-secret'}
                answer = AIMessage(content='', tool_calls=[{'id': 'lookup-fixture', 'name': 'academy_page', 'args': args}])
            else:
                answer = AIMessage(content='Academy fixture answer; no provider was called.')
            return ChatResult(generations=[ChatGeneration(message=answer)])

        def _stream(self, messages, stop=None, run_manager=None, **kwargs):
            yield ChatGenerationChunk(message=AIMessageChunk(content='Academy '))
            if self.behavior == 'interrupted':
                raise InterruptedError('explicit deterministic stream failure')
            yield ChatGenerationChunk(message=AIMessageChunk(content='privacy.', response_metadata={'finish_reason': 'stop'}))


@unittest.skipUnless(SDK_ENABLED, 'Set COURSE_SDK_OFFLINE=1 in the pinned SDK environment')
class NativeStage16Tests(unittest.TestCase):
    def test_native_invoke_and_stream_objects(self):
        result = invoke_and_stream(DeterministicAcademyModel(), 'Read privacy.')
        self.assertIsInstance(result['invoked'], AIMessage)
        self.assertIsInstance(result['streamed'], AIMessageChunk)
        self.assertEqual(result['streamed'].content, 'Academy privacy.')

    def test_stream_interruption_propagates(self):
        with self.assertRaises(InterruptedError):
            invoke_and_stream(DeterministicAcademyModel(behavior='interrupted'), 'Read privacy.')

    def test_decorated_tool_and_binding_schema(self):
        self.assertIn('allowlisted', academy_page.description)
        result = bind_and_inspect(DeterministicAcademyModel(), 'Read privacy.')
        self.assertEqual(result['tool_calls'][0]['args'], {'page_id': 'privacy'})
        self.assertEqual(result['schema']['properties']['page_id']['enum'], ['course', 'privacy', 'checkpoint'])
        self.assertEqual(academy_page.invoke({'page_id': 'privacy'})['page_id'], 'privacy')
        with self.assertRaises(ValidationError):
            academy_page.invoke({'page_id': 'personal-secret'})

    def test_native_structured_output(self):
        result = structured_answer(DeterministicAcademyModel(), 'Read privacy.')
        self.assertIsInstance(result, PageAnswer)
        self.assertEqual(result.citations, ['privacy'])

    def test_native_agent_structured_output(self):
        agent = make_agent(DeterministicAcademyModel(), trace=[], structured=True)
        result = agent.invoke({'messages': [HumanMessage(content='Read privacy.')]}, thread_config('structured'))
        self.assertIsInstance(result['structured_response'], PageAnswer)

    def test_native_structured_validation_errors(self):
        for behavior in ('missing', 'wrong-type', 'unknown-citation'):
            with self.subTest(behavior=behavior), self.assertRaises(ValidationError):
                structured_answer(DeterministicAcademyModel(behavior=behavior), 'Read privacy.')

    def test_real_agent_tool_loop_and_redacted_timing(self):
        trace = []
        agent = make_agent(DeterministicAcademyModel(), trace=trace)
        result = agent.invoke({'messages': [HumanMessage(content='private-canary Read privacy.')]}, thread_config('a'))
        tool_messages = [message for message in result['messages'] if isinstance(message, ToolMessage)]
        self.assertEqual(len(tool_messages), 1)
        self.assertEqual(tool_messages[0].tool_call_id, 'lookup-fixture')
        self.assertIn('isolated profile', tool_messages[0].content)
        self.assertEqual([event['kind'] for event in trace], ['model', 'tool', 'model'])
        self.assertNotIn('private-canary', repr(trace))
        self.assertTrue(all(set(event) == {'trace_id', 'span_id', 'parent_span_id', 'kind', 'status', 'elapsed_seconds'} and event['elapsed_seconds'] >= 0 for event in trace))

    def test_model_input_failure_is_traced_without_content(self):
        trace = []
        agent = make_agent(DeterministicAcademyModel(), trace=trace, max_input_chars=4)
        with self.assertRaises(ValueError):
            agent.invoke({'messages': [HumanMessage(content='private-canary')]}, thread_config('too-long'))
        self.assertEqual(trace[-1]['status'], 'error')
        self.assertNotIn('private-canary', repr(trace))

    def test_tool_policy_failure_is_traced(self):
        trace = []
        agent = make_agent(DeterministicAcademyModel(behavior='bad-tool'), trace=trace)
        with self.assertRaises(ValueError):
            agent.invoke({'messages': [HumanMessage(content='Read private page.')]}, thread_config('bad-tool'))
        self.assertEqual(trace[-1]['kind'], 'tool')
        self.assertEqual(trace[-1]['status'], 'error')

    def test_checkpoint_thread_isolation_context_and_pruning(self):
        model = DeterministicAcademyModel()
        agent = make_agent(model, trace=[], context_turns=1)
        config = thread_config('one')
        agent.invoke({'messages': [HumanMessage(content='First privacy turn.')]}, config)
        agent.invoke({'messages': [HumanMessage(content='Second privacy turn.')]}, config)
        stored = agent.get_state(config).values['messages']
        self.assertEqual(sum(isinstance(m, HumanMessage) for m in stored), 2)
        self.assertEqual(sum(isinstance(m, HumanMessage) for m in model.seen[-1]), 1)
        self.assertEqual(model.seen[-1][0].type, 'system')
        retained = prune_thread(agent, 'one', max_turns=1)
        self.assertEqual(sum(isinstance(m, HumanMessage) for m in retained), 1)
        self.assertEqual(sum(isinstance(m, ToolMessage) for m in retained), 1)
        self.assertEqual(agent.get_state(thread_config('two')).values, {})
        agent.invoke({'messages': [HumanMessage(content='Separate privacy turn.')]}, thread_config('two'))
        self.assertEqual(agent.get_state(config).values['messages'][0].content, 'Second privacy turn.')

    def test_invalid_memory_limits_and_thread_ids(self):
        with self.assertRaises(ValueError):
            recent_turns([], 0)
        with self.assertRaises(ValueError):
            thread_config(' ')
        with self.assertRaises(ValueError):
            make_agent(DeterministicAcademyModel(), trace=[], max_input_chars=0)


if __name__ == '__main__':
    unittest.main()
