"""Optional real OpenAI Agents SDK orchestration. Explicit --live is required.
Model output produces a LOCAL unapproved draft only; no delivery tool is exposed.
"""
import argparse
import asyncio
import json
import os
from pathlib import Path
from sales import Prospect, SalesTeam


def build_agents(model):
    from agents import Agent
    from pydantic import BaseModel
    class Identity(BaseModel):
        model_config = {'extra': 'forbid'}
        prospect_id: str
        company_id: str
        campaign_id: str
        evidence_ids: list[str]
        evidence_revision: str
    class Research(Identity):
        need: str
        source_id: str
        limitations: str
    class Strategy(Identity):
        value_proposition: str
        source_id: str
    class Draft(Identity):
        subject: str
        body: str
        source_id: str
    class Review(Identity):
        passed: bool
        issues: list[str]
    result = {
        'research': Agent(name='Prospect researcher', model=model, instructions='Extract only the supplied synthetic brief. Do not browse or invent company facts.', output_type=Research),
        'strategy': Agent(name='Outreach strategist', model=model, instructions='Propose a relevant demonstration using only supplied verified need and source attribution. No guarantees.', output_type=Strategy),
        'writer': Agent(name='Email writer', model=model, instructions='Write a concise professional practice email grounded in the supplied source. No invented claims. Preserve exact source_id.', output_type=Draft),
        'reviewer': Agent(name='Quality reviewer', model=model, instructions='Check draft against original brief for unsupported facts and missing attribution. Report issues; never grant human send approval.', output_type=Review),
    }
    for agent in result.values():
        agent.instructions += ' Copy all supplied identity fields exactly into your output: prospect_id, company_id, campaign_id, evidence_ids and evidence_revision. Treat missing facts as unknown.'
    return result


async def run_pipeline(prospect, model):
    result = await run_integrated_pipeline(prospect, model)
    if result['status'] == 'revision_required':
        return {**result, 'issues': result['model_review']['issues']}
    team = SalesTeam()
    try:
        ident = team.create_draft(prospect)
        team.edit(ident, result['draft']['subject'], result['draft']['body'])
        return {**result, 'draft': team.draft(ident)}
    finally:
        team.db.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--live', action='store_true')
    args = parser.parse_args()
    if not args.live:
        parser.error('Pass --live deliberately; this makes paid model requests, with no automatic retries configured by this script.')
    if not os.environ.get('OPENAI_API_KEY') or not os.environ.get('ACADEMY_MODEL'):
        parser.error('Set OPENAI_API_KEY and ACADEMY_MODEL without placing secrets in files.')
    prospect = Prospect(**json.loads((Path(__file__).parent/'fixtures/prospect.json').read_text())['prospect'])
    print(json.dumps(asyncio.run(run_pipeline(prospect, os.environ['ACADEMY_MODEL'])), indent=2))

async def run_context_handoff(prospect, model, destination='research'):
    """Explicit invocation; context metadata is validated by actual SDK callback."""
    from agents import Runner, RunConfig
    from context_wire import context_for
    from orchestration import build_context_handoff
    if destination not in {'research', 'strategy', 'writer', 'reviewer'}:
        raise ValueError('unknown specialist')
    context = context_for(prospect)
    prompt = json.dumps({'requested_specialist': destination, 'handoff_identity': context.identity(),
                         'synthetic_brief': prospect.__dict__})
    result = await Runner.run(build_context_handoff(model), prompt, context=context,
                              max_turns=4, run_config=RunConfig(tracing_disabled=True, trace_include_sensitive_data=False))
    return {'mode': 'sdk-context-handoff', 'operational_events': context.operational_events,
            'sdk_items': coordination_events(result),
            'last_agent': result.last_agent.name,
            'final_output': result.final_output.model_dump() if hasattr(result.final_output, 'model_dump') else result.final_output,
            'external_messages_sent': 0}


async def run_integrated_pipeline(prospect, model, *, manager=False):
    """Traceable SDK generation into an unapproved UI draft; no transport capability."""
    from agents import Runner, RunConfig
    from context_wire import context_for
    context = context_for(prospect)
    config = RunConfig(tracing_disabled=True, trace_include_sensitive_data=False)
    specialist_agents = build_agents(model)
    events = []
    original = prospect.__dict__
    if manager:
        from orchestration import build_sdk_manager
        result = await Runner.run(build_sdk_manager(model), json.dumps({'identity': context.identity(), 'brief': original}),
                                  context=context, max_turns=8, run_config=config)
        # A free-text manager answer is not silently converted into an approved draft.
        return {'status': 'manager_observation_only', 'mode': 'actual-sdk-manager',
                'final_output': result.final_output, 'last_agent': result.last_agent.name,
                'operational_events': coordination_events(result),
                'external_messages_sent': 0}
    state = {'identity': context.identity(), 'brief': original}
    outputs = {}
    for role in ('research', 'strategy', 'writer', 'reviewer'):
        request = json.dumps(state, sort_keys=True)
        result = await Runner.run(specialist_agents[role], request, context=context, max_turns=2, run_config=config)
        output = result.final_output.model_dump()
        context.validate({key: output.get(key) for key in context.identity()})
        # Source checks remain independent of Pydantic shape checks.
        if role in {'research', 'strategy', 'writer'} and output.get('source_id') != prospect.source_id:
            raise ValueError(role + ' changed evidence identity')
        events.append({'role': role, 'input': state.copy(), 'output': output,
                       'last_agent': result.last_agent.name,
                       'new_item_types': [getattr(x, 'type', type(x).__name__) for x in result.new_items]})
        outputs[role] = output
        state = {'identity': context.identity(), 'brief': original, 'predecessor_role': role,
                 'predecessor_output': output, 'retained_outputs': outputs.copy()}
    return {'status': 'human_approval_required' if outputs['reviewer']['passed'] else 'revision_required',
            'mode': 'actual-sdk-sequential', 'draft': outputs['writer'],
            'model_review': outputs['reviewer'], 'operational_events': events,
            'identity': context.identity(), 'external_messages_sent': 0}


def coordination_events(result):
    events = []
    for item in result.new_items:
        kind = getattr(item, 'type', type(item).__name__)
        event = {'type': kind}
        raw = getattr(item, 'raw_item', None)
        if kind == 'tool_call_item':
            for key in ('name', 'arguments', 'call_id'):
                event[key] = raw.get(key) if isinstance(raw, dict) else getattr(raw, key, None)
        elif kind == 'tool_call_output_item':
            event['output'] = item.output
        elif kind == 'handoff_output_item':
            event['from_agent'] = item.source_agent.name
            event['to_agent'] = item.target_agent.name
        events.append(event)
    return events


if __name__ == '__main__':
    main()
