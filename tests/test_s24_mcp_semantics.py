"""Genuine installed Agno/MCP discovery/read/cleanup, never model generation.

Central QA must invoke in its pinned Agno environment. No mocks or desired model
answers are substituted. A skipped SDK suite is not runtime acceptance.
"""
import importlib.util
import unittest


@unittest.skipUnless(importlib.util.find_spec('agno'), 'Requires central pinned Agno environment')
class GenuineAgnoMcp(unittest.IsolatedAsyncioTestCase):
    async def test_discovery_agent_binding_and_real_fixture_reads(self):
        from agno.agent import Agent
        from examples.s24_triage import build_mcp_agent
        async with build_mcp_agent('gpt-4.1-mini', api_key='unused-no-provider-call') as agent:
            self.assertIsInstance(agent, Agent)
            toolkit=agent.tools[0]
            self.assertEqual(set(toolkit.functions), {'lookup_ticket','search_articles'})
            # These entrypoints are genuinely discovered MCP remote functions,
            # not direct calls to the local deterministic fixture implementation.
            ticket=await toolkit.functions['lookup_ticket'].entrypoint(ticket_id='T-001')
            articles=await toolkit.functions['search_articles'].entrypoint(product_id='P-KEY')
            self.assertIn('T-001', str(ticket))
            self.assertIn('A-001', str(articles))
            unknown=await toolkit.functions['lookup_ticket'].entrypoint(ticket_id='T-999')
            self.assertIn('unknown_ticket', str(unknown))
        self.assertIsNone(toolkit.session)
        self.assertFalse(toolkit._initialized)

    async def test_cleanup_on_consumer_error(self):
        from examples.s24_triage import build_mcp_agent
        toolkit=None
        with self.assertRaisesRegex(RuntimeError, 'consumer_failure'):
            async with build_mcp_agent('gpt-4.1-mini',api_key='unused-no-provider-call') as agent:
                toolkit=agent.tools[0]
                raise RuntimeError('consumer_failure')
        self.assertIsNotNone(toolkit)
        self.assertIsNone(toolkit.session)
        self.assertFalse(toolkit._initialized)

    async def test_configuration_rejected_before_spawn(self):
        from examples.s24_triage import build_mcp_agent
        with self.assertRaisesRegex(ValueError,'Explicit model'):
            async with build_mcp_agent(''):
                self.fail('must not enter')
