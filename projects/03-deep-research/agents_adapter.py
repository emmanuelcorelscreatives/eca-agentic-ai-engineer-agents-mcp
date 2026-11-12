"""Optional actual SDK research planner and analyst over an attributable local corpus.
No live web search is implied; paid model execution requires explicit --live.
"""
import argparse
import asyncio
import json
import os
from pathlib import Path
from research import Evidence, investigate


def build_agents(model):
    from agents import Agent
    from pydantic import BaseModel
    class Plan(BaseModel):
        objectives: list[str]
        questions: list[str]
    class Analysis(BaseModel):
        summary: str
        cited_source_ids: list[str]
        uncertainties: list[str]
    return (
        Agent(name='Research planner', model=model, instructions='Plan research of the supplied question using only the available synthetic corpus. Never claim to have searched the web.', output_type=Plan),
        Agent(name='Evidence analyst', model=model, instructions='Analyze only supplied evidence. Preserve every conflict explicitly and distinguish unsupported conclusions. Cite source IDs; no invented facts or live search claims.', output_type=Analysis),
    )


async def run_pipeline(question, corpus, model):
    from agents import Runner, RunConfig
    planner, analyst = build_agents(model)
    config = RunConfig(tracing_disabled=True)
    planned = (await Runner.run(planner, question, max_turns=2, run_config=config)).final_output
    # Canonical deterministic evidence report remains visible beside model interpretation.
    report = investigate(question, corpus)
    if not report['sources']:
        return {'plan': planned.model_dump(), 'evidence_report': report, 'analysis': None}
    result = (await Runner.run(analyst, json.dumps(report), max_turns=2, run_config=config)).final_output
    allowed = {source['source_id'] for source in report['sources']}
    if not set(result.cited_source_ids).issubset(allowed):
        raise ValueError('model invented a source identifier')
    if not result.cited_source_ids:
        raise ValueError('analysis has no source attribution')
    return {'plan': planned.model_dump(), 'evidence_report': report, 'model_interpretation': result.model_dump(), 'status': 'requires_human_evidence_review'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--live', action='store_true')
    parser.add_argument('--question', default='Cedar Library weekly reporting time')
    args = parser.parse_args()
    if not args.live:
        parser.error('--live is required; model execution is paid. No automatic retries are configured by this script.')
    if not os.environ.get('OPENAI_API_KEY') or not os.environ.get('ACADEMY_MODEL'):
        parser.error('Set OPENAI_API_KEY and ACADEMY_MODEL outside the repository.')
    data = json.loads((Path(__file__).parent/'fixtures/evidence.json').read_text())
    print(json.dumps(asyncio.run(run_pipeline(args.question, [Evidence(**e) for e in data['evidence']], os.environ['ACADEMY_MODEL'])), indent=2))

if __name__ == '__main__':
    main()
