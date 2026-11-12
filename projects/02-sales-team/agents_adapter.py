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
    class Research(BaseModel):
        need: str
        source_id: str
        limitations: str
    class Strategy(BaseModel):
        value_proposition: str
        source_id: str
    class Draft(BaseModel):
        subject: str
        body: str
        source_id: str
    class Review(BaseModel):
        passed: bool
        issues: list[str]
    return {
        'research': Agent(name='Prospect researcher', model=model, instructions='Extract only the supplied synthetic brief. Do not browse or invent company facts.', output_type=Research),
        'strategy': Agent(name='Outreach strategist', model=model, instructions='Propose a relevant demonstration using only supplied verified need and source attribution. No guarantees.', output_type=Strategy),
        'writer': Agent(name='Email writer', model=model, instructions='Write a concise professional practice email grounded in the supplied source. No invented claims. Preserve exact source_id.', output_type=Draft),
        'reviewer': Agent(name='Quality reviewer', model=model, instructions='Check draft against original brief for unsupported facts and missing attribution. Report issues; never grant human send approval.', output_type=Review),
    }


async def run_pipeline(prospect, model):
    from agents import Runner, RunConfig
    agents = build_agents(model)
    config = RunConfig(tracing_disabled=True)
    evidence = json.dumps(prospect.__dict__)
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
