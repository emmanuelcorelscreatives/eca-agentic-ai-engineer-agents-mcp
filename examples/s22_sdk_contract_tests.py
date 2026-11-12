"""Central-QA-only actual Pydantic FunctionToolset contracts; zero model calls.
Author has NOT executed this new suite. TestModel is an explicitly simulated
schema context, never an observed provider result.
"""
import unittest
from pydantic_ai import RunContext
from pydantic_ai.models.test import TestModel
from pydantic_ai.usage import RunUsage
from examples.s22_policy import RequestContext,PolicyService,escalation_draft
from examples.s22_toolsets import make_role_toolsets,require_capability

class RoleToolsetContracts(unittest.IsolatedAsyncioTestCase):
    def context(self,role):
        return RunContext(deps=RequestContext('request-'+role,'T-001',PolicyService(),role=role),
                          model=TestModel(),usage=RunUsage())
    async def test_named_reusable_reader_toolset_exposes_only_lookup(self):
        selected=make_role_toolsets('reader')
        self.assertEqual([s.id for s in selected],['academy-policy-read-v1'])
        self.assertEqual(set(await selected[0].get_tools(self.context('reader'))),{'lookup_policy'})
    async def test_triager_has_two_explicit_named_toolsets(self):
        selected=make_role_toolsets('triager')
        self.assertEqual([s.id for s in selected],['academy-policy-read-v1','academy-escalation-draft-v1'])
        names=set()
        for toolset in selected:names.update(await toolset.get_tools(self.context('triager')))
        self.assertEqual(names,{'lookup_policy','draft_escalation'})
    async def test_reader_cannot_execute_draft_even_via_direct_dispatch(self):
        reader=self.context('reader')
        with self.assertRaises(PermissionError):
            escalation_draft(reader.deps,'Review damage')
        triager_toolsets=make_role_toolsets('triager')
        draft=triager_toolsets[1].tools['draft_escalation'].function
        with self.assertRaises(PermissionError):draft(reader,reason='Attempt role escalation')
    async def test_role_substitution_is_denied_on_read_tool(self):
        reader_toolset=make_role_toolsets('reader')[0]
        function=reader_toolset.tools['lookup_policy'].function
        with self.assertRaises(PermissionError):function(self.context('triager'),product_id='P-KEY')
    async def test_allowed_tool_uses_same_fixture_and_remains_unsent(self):
        selected=make_role_toolsets('triager');ctx=self.context('triager')
        lookup=selected[0].tools['lookup_policy'].function
        self.assertEqual(lookup(ctx,product_id='P-KEY')['policies'][0]['id'],'POL-KEY-1')
        draft=selected[1].tools['draft_escalation'].function(ctx,reason='Reported physical damage')
        self.assertEqual(draft['status'],'draft_only');self.assertNotIn('sent',draft)
    async def test_unsupported_role_rejected_before_sdk_agent_or_provider(self):
        with self.assertRaises(ValueError):make_role_toolsets('administrator')

if __name__=='__main__':unittest.main()
