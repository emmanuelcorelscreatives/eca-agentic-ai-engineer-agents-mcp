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
from pydantic import BaseModel, ConfigDict, Field, model_validator
from workflows import lookup_course, capability, RequestContext
from sdk_observation import ObservationHooks, LocalSDKTraceProcessor, complete_lineage_observed
from stream_receipt import consume_sdk_stream
from typing import Literal


class CatalogueRecord(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    course_id: str = Field(pattern=r'^ECA-[0-9]{3}$')
    title: str = Field(min_length=1)
    level: Literal['beginner', 'intermediate', 'advanced']
    prerequisites: list[str]


class CatalogueToolResult(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    found: bool
    course: CatalogueRecord | None

    @model_validator(mode='after')
    def consistent_variant(self):
        if self.found != (self.course is not None):
            raise ValueError('found and course payload disagree')
        return self


def validated_catalogue_result(raw, requested_id: str) -> dict:
    """Validate the TOOL RETURN before the SDK serializes it for the model.

    Shape validation and current-fixture factual validation are separate checks.
    A well-typed but invented title or cross-request ID is still rejected.
    """
    value = CatalogueToolResult.model_validate(raw).model_dump()
    if value != lookup_course(requested_id):
        raise ValueError('tool return disagrees with requested current catalogue record')
    return value


class CourseAnswer(BaseModel):
    model_config = ConfigDict(extra='forbid')
    found: bool
    course_id: str | None = Field(pattern=r'^ECA-[0-9]{3}$')
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


def make_agents(model: str, *, hooks=None, run_config=None):
    @function_tool
    def catalogue_lookup(course_id: str) -> dict:
        """Read one synthetic Academy course by its ECA-NNN ID."""
        return validated_catalogue_result(lookup_course(course_id), course_id)

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
                               parameters=SpecialistInput, include_input_schema=True, max_turns=4,
                               hooks=hooks, run_config=run_config),
               policy_agent.as_tool(tool_name='ask_policy', tool_description='Read returns policy',
                                    parameters=SpecialistInput, include_input_schema=True, max_turns=4,
                                    hooks=hooks, run_config=run_config)])
    triage = Agent[RequestContext](name='Delivery triage', model=model,
        instructions='For delivery requests hand off to shipping; do not answer delivery facts yourself.',
        handoffs=[handoff(shipping_agent)])
    synthesizer = Agent[RequestContext](name='Delivery synthesizer', model=model,
        tools=[shipping], output_type=SupportAnswer,
        instructions='Use shipping. Synthesize the inventory and policy specialist results already in '
        'conversation with the returned delivery fact. Cite only their source IDs. Preserve missing '
        'facts as unresolved. You own the final answer after handoff; no message is sent.')
    complete = Agent[RequestContext](name='Complete support manager', model=model,
        tools=list(manager.tools), handoffs=[handoff(synthesizer)],
        instructions='First call ask_inventory and ask_policy for this request. Then hand off to '
        'Delivery synthesizer, preserving the conversation. Do not produce the final answer yourself. '
        'Only the delivery synthesizer combines the attributed facts. No sending or write actions.')
    return dict(catalogue=catalogue, manager=manager, triage=triage, complete=complete,
                synthesizer=synthesizer,
                research=research, policy=policy_agent, shipping=shipping_agent)


async def run_live(*, model: str, mode: str, db: str, hosted_tracing: bool, stream: bool,
                   trace_file=None, cancel_after_deltas=None, prompt_override=None,
                   session_id=None):
    if not os.environ.get('OPENAI_API_KEY'):
        raise RuntimeError('OPENAI_API_KEY required for explicit live mode')
    local = LocalSDKTraceProcessor() if trace_file else None
    if local is not None:
        from agents import add_trace_processor, set_trace_processors
        if hosted_tracing:
            add_trace_processor(local)
        else:
            # CLI/standalone teaching process only. No hosted HTTP exporter remains installed.
            set_trace_processors([local])
    config = RunConfig(tracing_disabled=not (hosted_tracing or local), trace_include_sensitive_data=False,
                       workflow_name='Academy synthetic stage 06-07')
    hooks = ObservationHooks()
    agents = make_agents(model, hooks=hooks, run_config=config)
    context = RequestContext('REQ-001', 'KB-01', '2026-11-demo')
    prompt = {'catalogue': 'Find ECA-101 and explain prerequisites using the catalogue tool.',
              'manager': 'Report stock and returns for this request. Cite both sources.',
              'triage': 'Please explain delivery timing for this request.',
              'complete': 'Collect stock, returns and delivery for this request, then provide the combined answer.'}[mode]
    prompt = prompt_override if prompt_override is not None else prompt
    session = SQLiteSession(session_id or 'academy-synthetic-stage06-' + mode, db_path=db)
    kwargs = dict(context=context, session=session, max_turns=8, run_config=config, hooks=hooks)
    before = await session.get_items()
    started = __import__('time').perf_counter()
    result = None
    try:
        with trace('Academy synthetic stage 06-07', disabled=config.tracing_disabled) as actual_trace:
            if stream:
                result = Runner.run_streamed(agents[mode], prompt, **kwargs)
                receipt = await consume_sdk_stream(result, cancel_after_deltas=cancel_after_deltas,
                    on_delta=lambda delta: print(delta, end='', flush=True))
                print(json.dumps({'stream_receipt': receipt.export()}), file=sys.stderr)
                if receipt.status != 'complete':
                    raise RuntimeError('Incomplete stream retained; partial text is not a final answer')
            else:
                result = await Runner.run(agents[mode], prompt, **kwargs)
            output = result.final_output
            print(output.model_dump_json() if isinstance(output, BaseModel) else output)
            history = result.to_input_list() if callable(getattr(result, 'to_input_list', None)) else None
            report = {'last_agent': result.last_agent.name, 'mode': 'actual-sdk-live',
                      'model': model, 'hosted_upload_requested': hosted_tracing,
                      'hosted_upload_proven': False,
                      'trace_id': None if config.tracing_disabled else actual_trace.trace_id,
                      'duration_seconds': __import__('time').perf_counter() - started,
                      'session_items_before': len(before),
                      'session_items_after': len(await session.get_items()),
                      'to_input_list_item_count': len(history) if history is not None else None,
                      'observation': hooks.export()}
            if mode == 'complete':
                report['complete_lineage_observed'] = complete_lineage_observed(hooks.events)
            print(json.dumps(report))
            return report
    except BaseException as error:
        print(json.dumps({'status': 'interrupted', 'error_type': type(error).__name__,
                          'observation': hooks.export(), 'automatic_retry': False}), file=sys.stderr)
        raise
    finally:
        if local is not None:
            local.write(trace_file)


async def run_dialogue_turn(*, model: str, db: str, step: str, session_id='academy-dialogue',
                            trace_file=None):
    """ONE real Runner call per invocation; SQLite alone carries prior conversation.

    Run seed in process A, followup in a fresh process B using the same file/session.
    Control uses an unrelated session and asks the same question. No add_items,
    to_input_list replay, hardcoded answer, or copied first-turn prompt is used.
    """
    prompts = {'seed': 'Remember that my chosen course is ECA-101. Look it up and confirm.',
               'followup': 'Which course did I choose earlier? Give its ID and prerequisites. If absent, say unknown.',
               'control': 'Which course did I choose earlier? Give its ID and prerequisites. If absent, say unknown.'}
    if step not in prompts:
        raise ValueError('step must be seed, followup or control')
    return await run_live(model=model, mode='catalogue', db=db, hosted_tracing=False,
        stream=False, trace_file=trace_file, prompt_override=prompts[step],
        session_id=session_id if step != 'control' else session_id + '-unrelated')


async def run_parallel_live(agents, ctx: RequestContext, *, config: RunConfig, hooks=None):
    """Independent read-only SDK calls; context is immutable, results keep input order."""
    return await asyncio.gather(
        Runner.run(agents['research'], 'Read stock', context=ctx, max_turns=4, run_config=config, hooks=hooks),
        Runner.run(agents['policy'], 'Read policy', context=ctx, max_turns=4, run_config=config, hooks=hooks),
        return_exceptions=True)


async def parallel_entry(model):
    if not os.environ.get('OPENAI_API_KEY'):
        raise RuntimeError('OPENAI_API_KEY required for explicit live mode')
    hooks = ObservationHooks()
    config = RunConfig(tracing_disabled=True, trace_include_sensitive_data=False)
    agents = make_agents(model, hooks=hooks, run_config=config)
    results = await run_parallel_live(agents, RequestContext('REQ-001', 'KB-01', '2026-11-demo'),
                                      config=config, hooks=hooks)
    rows = []
    for role, result in zip(('research', 'policy'), results):
        if isinstance(result, BaseException):
            rows.append({'role': role, 'status': 'failed_or_unknown',
                         'error_type': type(result).__name__, 'automatic_retry': False})
        else:
            rows.append({'role': role, 'status': 'complete', 'last_agent': result.last_agent.name,
                         'final_output': result.final_output})
    print(json.dumps({'mode': 'actual-sdk-parallel', 'results': rows,
                      'observation': hooks.export()}, default=str))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--live', action='store_true')
    p.add_argument('--model', required=True)
    p.add_argument('--mode', choices=['catalogue', 'manager', 'triage', 'complete', 'dialogue', 'parallel'], default='catalogue')
    p.add_argument('--db', default='academy-stage06.sqlite')
    p.add_argument('--stream', action='store_true')
    p.add_argument('--hosted-tracing', action='store_true')
    p.add_argument('--trace-file', help='New private local SDK span JSON; never overwrite prior evidence')
    p.add_argument('--cancel-after-deltas', type=int)
    p.add_argument('--dialogue-step', choices=['seed', 'followup', 'control'])
    p.add_argument('--session-id', default='academy-dialogue')
    args = p.parse_args()
    if not args.live:
        p.error('No implicit provider calls. Use --live deliberately or workflows.py for offline exercises.')
    # Provider retries are not the lesson's explicit, read-only local retry exercise.
    from openai import AsyncOpenAI
    from agents import set_default_openai_client
    set_default_openai_client(AsyncOpenAI(max_retries=0))
    if args.mode == 'dialogue':
        if not args.dialogue_step or args.stream or args.hosted_tracing:
            p.error('dialogue requires --dialogue-step; use separate nonstreaming invocations')
        asyncio.run(run_dialogue_turn(model=args.model, db=args.db, step=args.dialogue_step,
                                      session_id=args.session_id, trace_file=args.trace_file))
    elif args.mode == 'parallel':
        if args.stream or args.hosted_tracing or args.trace_file:
            p.error('parallel uses local lifecycle diagnostics; choose a normal mode for SDK spans')
        asyncio.run(parallel_entry(args.model))
    else:
        asyncio.run(run_live(model=args.model, mode=args.mode, db=args.db,
                             hosted_tracing=args.hosted_tracing, stream=args.stream,
                             trace_file=args.trace_file, cancel_after_deltas=args.cancel_after_deltas))
