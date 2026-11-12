"""Real OpenAI Agents SDK adapter. Import/build performs no model calls.

Paid execution requires both --live and OPENAI_API_KEY; model is an explicit argument.
Tracing is disabled by default. --hosted-tracing opts in to uploading non-private
synthetic run inputs. No email/message sending or write tools are exposed.
"""
from __future__ import annotations
import argparse
import asyncio
from dataclasses import dataclass
import json
import os
import sys
from pathlib import Path

from agents import Agent, Runner, RunConfig, RunContextWrapper, SQLiteSession, function_tool, handoff, trace
from pydantic import BaseModel, ConfigDict, Field
from workflows import lookup_course, capability, RequestContext


class CourseAnswer(BaseModel):
    model_config = ConfigDict(extra='forbid')
    found: bool
    course_id: str = Field(pattern=r'^ECA-[0-9]{3}$')
    title: str | None
    level: str | None
    prerequisites: list[str]


class SupportAnswer(BaseModel):
    model_config = ConfigDict(extra='forbid')
    request_id: str = Field(pattern=r'^REQ-[0-9]{3}$')
    answer: str
    source_ids: list[str]
    unresolved: list[str]


class SpecialistInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    question: str = Field(min_length=1, max_length=400)


def make_agents(model: str):
    @function_tool
    def catalogue_lookup(course_id: str) -> dict:
        """Read one synthetic Academy course by its ECA-NNN ID."""
        return lookup_course(course_id)

    @function_tool
    def inventory(ctx: RunContextWrapper[RequestContext]) -> dict:
        """Read synthetic stock for the product in application-owned context."""
        return capability('research', 'inventory', ctx.context)

    @function_tool
    def policy(ctx: RunContextWrapper[RequestContext]) -> dict:
        """Read the synthetic policy version fixed in application context."""
        return capability('policy', 'policy', ctx.context)

    @function_tool
    def shipping(ctx: RunContextWrapper[RequestContext]) -> dict:
        """Read synthetic delivery information for this request."""
        return capability('shipping', 'shipping', ctx.context)

    catalogue = Agent(name='Academy catalogue', model=model, tools=[catalogue_lookup],
        instructions='Read catalogue_lookup. Report only returned facts. Unknown IDs are unknown; never invent a course.',
        output_type=CourseAnswer)
    research = Agent[RequestContext](name='Inventory researcher', model=model, tools=[inventory],
        instructions='Use inventory only; return its synthetic inventory facts. No policy decisions or sending messages.')
    policy_agent = Agent[RequestContext](name='Policy specialist', model=model, tools=[policy],
        instructions='Use policy only. Cite synthetic-policy and its version. Do not invent exceptions.')
    shipping_agent = Agent[RequestContext](name='Shipping specialist', model=model, tools=[shipping],
        instructions='Use shipping and own the final delivery answer. State it is synthetic.', output_type=SupportAnswer)
    manager = Agent[RequestContext](name='Support manager', model=model, output_type=SupportAnswer,
        instructions='For stock and returns call both specialists. Synthesize cited facts; record missing results as unresolved. Never send a message.',
        tools=[research.as_tool(tool_name='ask_inventory', tool_description='Read stock for this request',
                               parameters=SpecialistInput, include_input_schema=True, max_turns=4),
               policy_agent.as_tool(tool_name='ask_policy', tool_description='Read returns policy',
                                    parameters=SpecialistInput, include_input_schema=True, max_turns=4)])
    triage = Agent[RequestContext](name='Delivery triage', model=model,
        instructions='For delivery requests hand off to shipping; do not answer delivery facts yourself.',
        handoffs=[handoff(shipping_agent)])
    return dict(catalogue=catalogue, manager=manager, triage=triage,
                research=research, policy=policy_agent, shipping=shipping_agent)


async def run_live(*, model: str, mode: str, db: str, hosted_tracing: bool, stream: bool):
    if not os.environ.get('OPENAI_API_KEY'):
        raise RuntimeError('OPENAI_API_KEY required for explicit live mode')
    agents = make_agents(model)
    config = RunConfig(tracing_disabled=not hosted_tracing, trace_include_sensitive_data=False,
                       workflow_name='Academy synthetic stage 06-07')
    context = RequestContext('REQ-001', 'KB-01', '2026-11-demo')
    prompt = {'catalogue': 'Find ECA-101 and explain prerequisites using the catalogue tool.',
              'manager': 'Report stock and returns for this request. Cite both sources.',
              'triage': 'Please explain delivery timing for this request.'}[mode]
    session = SQLiteSession('academy-synthetic-stage06-' + mode, db_path=db)
    kwargs = dict(context=context, session=session, max_turns=8, run_config=config)
    if stream:
        result = Runner.run_streamed(agents[mode], prompt, **kwargs)
        async for event in result.stream_events():
            # Separate machine-readable event kinds from final output. No invented deltas.
            print(json.dumps({'event_type': event.type}), file=sys.stderr, flush=True)
            if event.type == 'raw_response_event' and getattr(event.data, 'type', None) == 'response.output_text.delta':
                print(event.data.delta, end='', flush=True)
        output = result.final_output
    else:
        result = await Runner.run(agents[mode], prompt, **kwargs)
        output = result.final_output
    print(output.model_dump_json() if isinstance(output, BaseModel) else output)
    print(json.dumps({'last_agent': result.last_agent.name, 'mode': 'actual-sdk-live',
                      'model': model, 'hosted_tracing': hosted_tracing}))


async def run_parallel_live(agents, ctx: RequestContext, *, config: RunConfig):
    """Independent read-only SDK calls; context is immutable, results keep input order."""
    return await asyncio.gather(
        Runner.run(agents['research'], 'Read stock', context=ctx, max_turns=4, run_config=config),
        Runner.run(agents['policy'], 'Read policy', context=ctx, max_turns=4, run_config=config))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--live', action='store_true')
    p.add_argument('--model', required=True)
    p.add_argument('--mode', choices=['catalogue', 'manager', 'triage'], default='catalogue')
    p.add_argument('--db', default='academy-stage06.sqlite')
    p.add_argument('--stream', action='store_true')
    p.add_argument('--hosted-tracing', action='store_true')
    args = p.parse_args()
    if not args.live:
        p.error('No implicit provider calls. Use --live deliberately or workflows.py for offline exercises.')
    asyncio.run(run_live(model=args.model, mode=args.mode, db=args.db,
                         hosted_tracing=args.hosted_tracing, stream=args.stream))
