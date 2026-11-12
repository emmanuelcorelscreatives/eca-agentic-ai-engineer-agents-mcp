"""Real Strands and Pydantic AI factories; no model calls during import/build."""
import os
from examples.s22_policy import PolicyService, RequestContext, validate_triage, escalation_draft

def build_strands():
    region = os.environ.get('AWS_REGION', '').strip()
    model_id = os.environ.get('BEDROCK_MODEL_ID', '').strip()
    if not region or not model_id:
        raise ValueError('Set AWS_REGION and BEDROCK_MODEL_ID; use the AWS credential chain')
    from strands import Agent, tool
    from strands.models import BedrockModel
    service = PolicyService()
    @tool
    def lookup_policy(product_id: str) -> dict:
        """Return only fixture-backed policies for one exact product ID."""
        return service.lookup(product_id)
    return Agent(model=BedrockModel(model_id=model_id, region_name=region), tools=[lookup_policy],
        system_prompt='Triage synthetic tickets using lookup_policy. Cite policy IDs; report uncertainty. No external changes.')

def build_pydantic(model=None, *, toolsets=None, role='triager'):
    model = model or os.environ.get('PYDANTIC_MODEL', '').strip()
    if not model:
        raise ValueError('Set PYDANTIC_MODEL to a provider:model identifier')
    from pydantic import BaseModel, Field
    from pydantic_ai import Agent, RunContext, ModelRetry
    from typing import Literal
    from examples.s22_toolsets import make_role_toolsets
    selected_toolsets=make_role_toolsets(role)
    class Triage(BaseModel):
        ticket_id: str
        category: Literal['damaged','delivery','unknown']
        rationale: str
        policy_ids: list[str]
        confidence: float = Field(ge=0, le=1)
        unresolved: list[str]
    agent = Agent(model, deps_type=RequestContext, output_type=Triage, toolsets=[*selected_toolsets, *(toolsets or [])],
        instructions='Triage the supplied synthetic ticket. Look up and cite real fixture policies. Do not send anything.')
    def verify(ctx, output):
        try:
            validate_triage(output.model_dump(), ctx.deps)
        except ValueError as exc:
            raise ModelRetry(str(exc)) from exc
        return output
    verify.__annotations__ = {'ctx':RunContext[RequestContext], 'output':Triage, 'return':Triage}
    agent.output_validator(verify)
    return agent

def pydantic_with_mcp(model, *, role='triager'):
    """Actual pinned Pydantic MCP toolset; caller enters async agent context."""
    from pydantic_ai.mcp import MCPToolset
    from fastmcp.client.transports import StdioTransport
    import sys
    server = MCPToolset(StdioTransport(command=sys.executable,args=['-m','examples.s22_policy_mcp']))
    # Only the actual read-only policy tool is exposed; reject wildcard remote capabilities.
    server=server.filtered(lambda ctx,definition: definition.name=='lookup_policy' and ctx.deps.role==role).prefixed('mcp')
    return build_pydantic(model,toolsets=[server],role=role)

if __name__ == '__main__':
    import sys
    if '--run' not in sys.argv:
        raise SystemExit('Explicit --run required; no request sent')
    context = RequestContext('academy-demo', 'T-001', PolicyService())
    ticket = context.policies.ticket(context.ticket_id)
    if '--bedrock' in sys.argv:
        print(build_strands()(str(ticket)))
    else:
        print(build_pydantic().run_sync(str(ticket), deps=context).output.model_dump_json())
