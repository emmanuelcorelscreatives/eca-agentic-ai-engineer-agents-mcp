"""Named reusable Pydantic AI toolsets with application-enforced capabilities.

The selected role is server configuration. RequestContext must agree with it;
a model cannot promote its role by supplying another tool argument.
"""
from examples.s22_policy import RequestContext,escalation_draft
ROLE_CAPABILITIES={'reader':frozenset({'lookup_policy'}),
                   'triager':frozenset({'lookup_policy','draft_escalation'})}

def require_capability(context: RequestContext, capability: str, *, configured_role: str):
    if configured_role not in ROLE_CAPABILITIES or context.role != configured_role:
        raise PermissionError('Request role differs from the configured agent role')
    if capability not in ROLE_CAPABILITIES[configured_role]:
        raise PermissionError('Capability denied for this role')

def make_role_toolsets(role: str):
    from pydantic_ai import RunContext
    from pydantic_ai.toolsets import FunctionToolset
    if role not in ROLE_CAPABILITIES:
        raise ValueError('Choose reader or triager before constructing an agent')
    policy=FunctionToolset(id='academy-policy-read-v1')
    def lookup_policy(ctx, product_id: str) -> dict:
        """Read the injected synthetic product policy, subject to configured role."""
        require_capability(ctx.deps,'lookup_policy',configured_role=role)
        return ctx.deps.policies.lookup(product_id)
    lookup_policy.__annotations__['ctx']=RunContext[RequestContext]
    policy.tool(lookup_policy)
    selected=[policy]
    if role=='triager':
        drafts=FunctionToolset(id='academy-escalation-draft-v1')
        def draft_escalation(ctx, reason: str) -> dict:
            """Create an unsent escalation draft for the current authorized ticket."""
            require_capability(ctx.deps,'draft_escalation',configured_role=role)
            return escalation_draft(ctx.deps,reason)
        draft_escalation.__annotations__['ctx']=RunContext[RequestContext]
        drafts.tool(draft_escalation)
        selected.append(drafts)
    return selected
