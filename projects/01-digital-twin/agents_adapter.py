"""Optional grounded SDK answer generation. No contact/write tools are exposed."""
import argparse
import asyncio
import json
import os
from pathlib import Path
from twin import DigitalTwin
from workflow import SYSTEM_INSTRUCTIONS


def build_agent(model):
    from agents import Agent
    from pydantic import BaseModel
    class Answer(BaseModel):
        answer: str
        cited_section_ids: list[str]
        insufficient_evidence: bool
    return Agent(name='Professional digital twin',model=model,instructions=SYSTEM_INSTRUCTIONS+' Respond from only the supplied approved evidence. Never imply that you performed external actions.',output_type=Answer)


async def answer(question,model):
    from agents import Runner,RunConfig
    twin=DigitalTwin(json.loads((Path(__file__).parent/'fixtures/profile.json').read_text())['sections'])
    try:
        evidence=twin.retrieve(question)
        if not evidence:
            return twin.answer(question)
        payload={'question':question,'approved_evidence':[{'id':s.id,'text':s.text} for s in evidence]}
        result=(await Runner.run(build_agent(model),json.dumps(payload),max_turns=2,run_config=RunConfig(tracing_disabled=True))).final_output
        allowed={s.id for s in evidence}
        if not set(result.cited_section_ids).issubset(allowed):raise ValueError('invented evidence citation')
        if not result.insufficient_evidence and not result.cited_section_ids:raise ValueError('supported answer requires citations')
        return {'model_answer':result.model_dump(),'approved_evidence':payload['approved_evidence'],'scope':'Generated wording requires factual evaluation; citation validation alone does not prove every claim.'}
    finally:twin.db.close()

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('question');parser.add_argument('--live',action='store_true');args=parser.parse_args()
    if not args.live or not os.environ.get('OPENAI_API_KEY') or not os.environ.get('ACADEMY_MODEL'):parser.error('Explicit --live, OPENAI_API_KEY and ACADEMY_MODEL required; this makes paid model requests.')
    print(json.dumps(asyncio.run(answer(args.question,os.environ['ACADEMY_MODEL'])),indent=2))
