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
    from agents import Runner, RunConfig
    agents = build_agents(model)
    config = RunConfig(tracing_disabled=True)
    from context_wire import context_for
    evidence = json.dumps({'brief': prospect.__dict__, 'identity': context_for(prospect).identity()})
    research = (await Runner.run(agents['research'], evidence, max_turns=2, run_config=config)).final_output
    if research.source_id != prospect.source_id:
        raise ValueError('research source attribution changed')
    strategy = (await Runner.run(agents['strategy'], research.model_dump_json(), max_turns=2, run_config=config)).final_output
    draft = (await Runner.run(agents['writer'], evidence + '\n' + strategy.model_dump_json(), max_turns=2, run_config=config)).final_output
    if draft.source_id != prospect.source_id:
        raise ValueError('draft source attribution changed')
    review = (await Runner.run(agents['reviewer'], evidence + '\n' + draft.model_dump_json(), max_turns=2, run_config=config)).final_output
    if not review.passed:
        return {'status': 'revision_required', 'issues': review.issues, 'draft': draft.model_dump()}
    team = SalesTeam()
    try:
        ident = team.create_draft(prospect)
        team.edit(ident, draft.subject, draft.body)
        return {'status': 'human_approval_required', 'draft': team.draft(ident), 'model_review': review.model_dump(), 'external_messages_sent': 0}
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

if __name__ == '__main__':
    main()


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
                'operational_events': [{'role': 'manager', 'new_item_types': [getattr(x, 'type', type(x).__name__) for x in result.new_items]}],
                'external_messages_sent': 0}
    state = {'identity': context.identity(), 'brief': original}
    outputs = {}
    for role in ('research', 'strategy', 'writer', 'reviewer'):
        request = json.dumps(state, sort_keys=True)
        result = await Runner.run(specialist_agents[role], request, context=context, max_turns=2, run_config=config)
        output = result.final_output.model_dump()
        context.validate({key: output[key] for key in context.identity()})
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
