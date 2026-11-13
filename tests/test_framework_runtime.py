"""Actual SDK construction probes. Run one family in its real isolated environment.

ECA_FRAMEWORK_FAMILY selects the installed family. Nothing contacts a provider;
all socket connects are denied during each test. Skips are not runtime passes.
"""
import asyncio
import importlib.metadata
import os
from pathlib import Path
import socket
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
FAMILY = os.environ.get('ECA_FRAMEWORK_FAMILY', '')

class ActualFrameworkRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.guards = [patch.object(socket.socket, 'connect', side_effect=AssertionError('Provider/network sockets forbidden in SDK construction tests')),
                       patch.object(socket.socket, 'connect_ex', side_effect=AssertionError('Provider/network sockets forbidden in SDK construction tests')),
                       patch.dict(os.environ, {'OTEL_SDK_DISABLED': 'true', 'CREWAI_TELEMETRY_ENABLED': 'false', 'OPENAI_AGENTS_DISABLE_TRACING': '1'})]
        for guard in self.guards:
            guard.start()
            self.addCleanup(guard.stop)

    @unittest.skipUnless(FAMILY == 'a2a', 'Select installed a2a family')
    def test_actual_a2a_card_serialization(self):
        from a2a.types import AgentCard, AgentSkill, AgentInterface, AgentCapabilities
        from google.protobuf.json_format import MessageToDict, ParseDict
        card = AgentCard(name='Academy local fixture', description='A deterministic protocol exercise, no LLM', version='1.0.0',
            default_input_modes=['text/plain'], default_output_modes=['text/plain'],
            capabilities=AgentCapabilities(streaming=False),
            supported_interfaces=[AgentInterface(url='http://127.0.0.1:9999', protocol_binding='JSONRPC', protocol_version='1.0')],
            skills=[AgentSkill(id='arithmetic', name='Order arithmetic', description='Compute a fixture order total', tags=['academy', 'fixture'])])
        encoded = MessageToDict(card)
        restored = ParseDict(encoded, AgentCard())
        self.assertEqual(restored.skills[0].id, 'arithmetic')
        self.assertEqual(restored.supported_interfaces[0].protocol_binding, 'JSONRPC')
        self.assertFalse(restored.capabilities.streaming)

    @unittest.skipUnless(FAMILY == 'a2a', 'Select installed a2a family')
    def test_actual_a2a_asgi_discovery_and_sdk_message_roundtrip(self):
        import httpx
        from a2a.client import A2ACardResolver, ClientConfig, create_client
        from a2a.helpers import new_text_message, get_message_text
        from a2a.types import Role, SendMessageRequest
        from examples.s21_a2a_server import make_app
        from examples.s21_inventory import lookup_stock
        import json
        async def exercise():
            transport = httpx.ASGITransport(app=make_app())
            async with httpx.AsyncClient(transport=transport, base_url='http://127.0.0.1:8765') as http:
                card = await A2ACardResolver(httpx_client=http, base_url='http://127.0.0.1:8765').get_agent_card()
                self.assertEqual([skill.id for skill in card.skills], ['stock-check'])
                client = await create_client(agent=card, client_config=ClientConfig(streaming=False, httpx_client=http))
                try:
                    request = SendMessageRequest(message=new_text_message('ECA-KEY-01', role=Role.ROLE_USER))
                    messages = []
                    async for result in client.send_message(request):
                        messages.append(result)
                    self.assertEqual(len(messages), 1)
                    self.assertTrue(messages[0].HasField('message'))
                    self.assertEqual(json.loads(get_message_text(messages[0].message)), lookup_stock('ECA-KEY-01'))
                finally:
                    await client.close()
        asyncio.run(exercise())

    @unittest.skipUnless(FAMILY == 'openai-agents', 'Select installed OpenAI family')
    def test_actual_agents_function_schema_and_handoff(self):
        from agents import Agent, function_tool, set_tracing_disabled
        from frameworks.common import line_total
        set_tracing_disabled(True)
        tool = function_tool(line_total)
        specialist = Agent(name='Order specialist', model='offline-placeholder', tools=[tool])
        router = Agent(name='Router', model='offline-placeholder', handoffs=[specialist])
        self.assertEqual(tool.name, 'line_total')
        self.assertEqual(tool.params_json_schema['properties']['quantity']['type'], 'integer')
        self.assertEqual(router.handoffs[0].name, specialist.name)

    @unittest.skipUnless(FAMILY == 'autogen', 'Select installed AutoGen family')
    def test_actual_autogen_agent_constructs_and_closes(self):
        from autogen_agentchat.agents import AssistantAgent
        from autogen_ext.models.openai import OpenAIChatCompletionClient
        from frameworks.common import line_total
        client = OpenAIChatCompletionClient(model='gpt-4o-mini', api_key='academy-offline-placeholder')
        try:
            agent = AssistantAgent('academy_order_assistant', model_client=client, tools=[line_total])
            self.assertEqual(agent.name, 'academy_order_assistant')
        finally:
            asyncio.run(client.close())

    @unittest.skipUnless(FAMILY == 'agno', 'Select installed Agno family')
    def test_actual_agno_agent_constructs(self):
        from agno.agent import Agent
        from agno.models.openai import OpenAIChat
        from frameworks.common import line_total
        agent = Agent(model=OpenAIChat(id='offline-placeholder', api_key='academy-offline-placeholder'), tools=[line_total])
        self.assertEqual(agent.model.id, 'offline-placeholder')
        self.assertEqual(len(agent.tools), 1)

    @unittest.skipUnless(FAMILY == 'microsoft', 'Select installed Microsoft family')
    def test_actual_microsoft_foundry_agent_constructs(self):
        from agent_framework import Agent
        from agent_framework.foundry import FoundryChatClient
        from azure.identity import AzureCliCredential
        from frameworks.common import line_total
        with AzureCliCredential() as credential:
            client = FoundryChatClient(project_endpoint='https://academy-fixture.services.ai.azure.com/api/projects/offline', model='offline-placeholder', credential=credential)
            agent = Agent(client=client, name='academy_orders', instructions='Use synthetic arithmetic only.', tools=[line_total])
            self.assertEqual(agent.name, 'academy_orders')

    @unittest.skipUnless(FAMILY == 'google-adk', 'Select installed Google ADK family')
    def test_actual_adk_agent_constructs(self):
        from frameworks.google_adk_agent import build_agent
        with patch.dict(os.environ, {'GOOGLE_MODEL': 'offline-placeholder'}):
            agent = build_agent()
        self.assertEqual(agent.name, 'academy_order_assistant')
        self.assertEqual(len(agent.tools), 1)

    @unittest.skipUnless(FAMILY == 'pydantic-ai', 'Select installed Pydantic AI family')
    def test_actual_pydantic_test_model_and_typed_dependencies(self):
        from pydantic import BaseModel
        from pydantic_ai import Agent, RunContext
        from pydantic_ai.models.test import TestModel
        from frameworks.pydantic_typed import OrderContext
        from frameworks.common import line_total
        class Summary(BaseModel):
            total: str
        agent = Agent(TestModel(custom_output_args={'total': '37.50'}), deps_type=OrderContext, output_type=Summary)
        def order_total(ctx):
            """Compute this fixture's order total."""
            return line_total(ctx.deps.unit_price, ctx.deps.quantity)
        order_total.__annotations__ = {'ctx': RunContext[OrderContext], 'return': str}
        agent.tool(order_total)
        result = agent.run_sync('Total the fixture', deps=OrderContext('12.50', 3))
        self.assertEqual(result.output.total, '37.50')
        # The SDK's explicit TestModel is a simulated model, not a provider response.
        self.assertIn('37.50', str(result.all_messages()))

    @unittest.skipUnless(FAMILY == 'pydantic-ai', 'Select installed Pydantic AI family')
    def test_native_triage_confidence_matches_raw_numeric_boundary(self):
        """Explicit TestModel fixtures exercise coercion, not provider quality."""
        from pydantic_ai.models.test import TestModel
        from pydantic_ai.exceptions import UnexpectedModelBehavior
        from examples.s22_agents import build_pydantic
        from examples.s22_policy import PolicyService, RequestContext, validate_triage
        context = RequestContext('native-confidence-fixture', 'T-001', PolicyService())
        valid = dict(ticket_id='T-001', category='damaged', rationale='Synthetic missing-key fixture',
            policy_ids=['POL-KEY-1'], confidence=0.7, unresolved=['No photo supplied'])
        for confidence in (0.0, 0.7, 1.0, 0, 1, True, False):
            with self.subTest(confidence=confidence):
                payload = dict(valid, confidence=confidence)
                agent = build_pydantic(TestModel(call_tools=[], custom_output_args=payload))
                if type(confidence) is bool:
                    with self.assertRaises(ValueError):
                        validate_triage(payload, context)
                    with self.assertRaises(UnexpectedModelBehavior):
                        agent.run_sync('Validate the synthetic fixture.', deps=context)
                else:
                    expected = validate_triage(payload, context)
                    actual = agent.run_sync('Validate the synthetic fixture.', deps=context).output.model_dump()
                    self.assertEqual(actual['confidence'], expected['confidence'])
                    self.assertEqual(actual['policy_ids'], expected['policy_ids'])

    @unittest.skipUnless(FAMILY == 'agno', 'Select installed Agno family')
    def test_actual_agno_output_schema_binds_ticket_and_article_evidence(self):
        """Schema construction only; all candidates below are synthetic values."""
        from pydantic import ValidationError
        from examples.s24_triage import build_agno, validate_triage_response
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'academy-offline-placeholder'}):
            schema = build_agno('offline-placeholder').output_schema
        valid = dict(ticket_id='T-001', summary='Synthetic citation-boundary fixture',
                     article_ids=['A-001'], unresolved=[])
        self.assertEqual(schema.model_validate(valid).article_ids, ['A-001'])
        for ids in (['A-999'], ['A-002'], [], ['A-001', 'A-001']):
            with self.subTest(article_ids=ids), self.assertRaises(ValidationError):
                schema.model_validate(dict(valid, article_ids=ids))
        # Another ticket's internally valid result still cannot answer this request.
        other = dict(valid, ticket_id='T-002', article_ids=['A-002'])
        self.assertEqual(schema.model_validate(other).ticket_id, 'T-002')
        with self.assertRaisesRegex(ValueError, 'requested_ticket_mismatch'):
            validate_triage_response(other, requested_ticket_id='T-001')
        self.assertEqual(validate_triage_response(valid, requested_ticket_id='T-001').ticket_id, 'T-001')

    @unittest.skipUnless(FAMILY == 'strands', 'Select installed Strands family')
    def test_actual_strands_tool_and_bedrock_model_construct(self):
        from strands import Agent, tool
        from strands.models import BedrockModel
        from frameworks.common import line_total
        # Explicit synthetic credentials prevent the SDK probing metadata/default profiles.
        import boto3
        session = boto3.Session(aws_access_key_id='academy-offline-placeholder', aws_secret_access_key='academy-offline-placeholder', region_name='us-east-1')
        model = BedrockModel(model_id='offline-placeholder', boto_session=session)
        decorated = tool(line_total)
        agent = Agent(model=model, tools=[decorated])
        self.assertIsNotNone(agent)
        self.assertEqual(decorated.tool_name, 'line_total')

    @unittest.skipUnless(FAMILY in {'google-adk', 'pydantic-ai', 'strands', 'autogen', 'microsoft', 'agno'}, 'Select an actual course adapter family')
    def test_actual_stage21_24_course_adapter_construction(self):
        if FAMILY == 'google-adk':
            from examples.s21_adk import build_agent
            agent, toolset = build_agent('offline-placeholder')
            self.assertEqual(agent.name, 'academy_stock_support')
            self.assertEqual(len(agent.tools), 2)
            self.assertIsNone(toolset)
        elif FAMILY == 'pydantic-ai':
            from examples.s22_agents import build_pydantic
            from pydantic_ai.models.test import TestModel
            agent = build_pydantic(TestModel())
            self.assertIsNotNone(agent)
        elif FAMILY == 'strands':
            from examples.s22_agents import build_strands
            with patch.dict(os.environ, {'AWS_REGION':'us-east-1', 'BEDROCK_MODEL_ID':'offline-placeholder', 'AWS_ACCESS_KEY_ID':'academy-offline-placeholder','AWS_SECRET_ACCESS_KEY':'academy-offline-placeholder','AWS_EC2_METADATA_DISABLED':'true'}):
                agent = build_strands()
            self.assertIsNotNone(agent)
        elif FAMILY == 'autogen':
            from examples.s23_framework_agents import build_autogen
            with patch.dict(os.environ, {'OPENAI_API_KEY':'academy-offline-placeholder'}):
                agent, client = build_autogen('gpt-4o-mini')
            try:
                self.assertEqual(agent.name, 'academy_policy')
            finally:
                asyncio.run(client.close())
        elif FAMILY == 'microsoft':
            from agent_framework.foundry import FoundryChatClient
            from azure.identity import AzureCliCredential
            from examples.s23_framework_agents import build_microsoft
            with AzureCliCredential() as credential:
                client = FoundryChatClient(project_endpoint='https://academy-fixture.services.ai.azure.com/api/projects/offline', model='offline-placeholder', credential=credential)
                self.assertIsNotNone(build_microsoft(client))
        elif FAMILY == 'agno':
            from examples.s24_triage import build_agno, build_team
            with patch.dict(os.environ, {'OPENAI_API_KEY':'academy-offline-placeholder'}):
                agent = build_agno('offline-placeholder')
                team = build_team('offline-placeholder')
            self.assertEqual(agent.name, 'Academy triage')
            self.assertEqual(len(team.members), 2)

    @unittest.skipUnless(FAMILY == 'crewai', 'Select installed CrewAI family')
    def test_actual_crewai_context_and_sequential_construction(self):
        from crewai import Agent, Crew, LLM, Process, Task
        llm = LLM(model='openai/gpt-4o-mini', api_key='academy-offline-placeholder')
        analyst = Agent(role='Analyst', goal='Calculate fixture values', backstory='Academy fixture analyst', llm=llm)
        reviewer = Agent(role='Reviewer', goal='Review fixture values', backstory='Academy fixture reviewer', llm=llm)
        first = Task(description='Calculate the fixture margin', expected_output='A fixture calculation', agent=analyst)
        second = Task(description='Review the arithmetic', expected_output='A checked calculation', agent=reviewer, context=[first])
        crew = Crew(agents=[analyst, reviewer], tasks=[first, second], process=Process.sequential, tracing=False)
        self.assertEqual(crew.tasks[1].context[0].id, first.id)
        self.assertEqual(crew.process, Process.sequential)

if __name__ == '__main__':
    unittest.main()
