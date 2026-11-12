"""Actual grounded SDK adapter; an explicit caller authorizes any paid run."""
import argparse
import asyncio
import json
import os
from config import profile_path
from context import assemble_context,ContextBudget
from prompts import SYSTEM_PROMPT,IDENTITY
from twin import DigitalTwin


def build_agent(model):
    from agents import Agent
    from pydantic import BaseModel
    class Answer(BaseModel):
        answer: str
        cited_section_ids: list[str]
        insufficient_evidence: bool
    return Agent(name='Professional digital twin',model=model,instructions=SYSTEM_PROMPT,output_type=Answer)


async def answer(question,model,history=(),tool_results=(),budget=None):
    from agents import Runner,RunConfig
    if question.strip().lower() in ("who are you?","who are you","are you amara?","are you amara"):
        return {"answer":IDENTITY,"citations":[],"status":"identity_disclosure"}
    core=DigitalTwin(json.loads(profile_path().read_text())['sections'])
    try:
        evidence=core.retrieve(question)
        if not evidence:return core.answer(question)
        allocation=assemble_context(question,evidence,history,tool_results,budget or ContextBudget())
        context=allocation['context']
        result=(await Runner.run(build_agent(model),json.dumps(context,ensure_ascii=False),max_turns=2,run_config=RunConfig(tracing_disabled=True,trace_include_sensitive_data=False))).final_output
        allowed={s['section_id'] for s in context['evidence']}
        if not set(result.cited_section_ids).issubset(allowed):raise ValueError('invented evidence citation')
        if not result.insufficient_evidence and not result.cited_section_ids:raise ValueError('supported answer requires citations')
        return {'model_answer':result.model_dump(),'approved_evidence':context['evidence'],'allocation':allocation['allocation'],'scope':'Actual generated wording still requires independent factual/tone evaluation; citation validation alone does not prove claims.'}
    finally:core.db.close()

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('question');parser.add_argument('--live',action='store_true');args=parser.parse_args()
    if not args.live or not os.environ.get('OPENAI_API_KEY') or not os.environ.get('ACADEMY_MODEL'):parser.error('Explicit --live, OPENAI_API_KEY and ACADEMY_MODEL required; this makes paid model requests.')
    print(json.dumps(asyncio.run(answer(args.question,os.environ['ACADEMY_MODEL'])),indent=2))
