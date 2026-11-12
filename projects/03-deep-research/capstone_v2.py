"""Finite opt-in actual SDK + Brave capstone, with no automatic transport retries."""
import argparse
import asyncio
import hashlib
import json
import os
from pathlib import Path
from research_lab.brave_search import BraveSearch
from research_lab.sdk_v2 import build_team
from research_lab.pipeline_v2 import run_research
from research_lab.exports_v2 import export
from research_lab.quality_v2 import trace_summary

async def execute(args):
    from openai import AsyncOpenAI
    from agents import OpenAIResponsesModel
    client=AsyncOpenAI(api_key=os.environ['OPENAI_API_KEY'],max_retries=0,
                       **({'base_url':os.environ['OPENAI_BASE_URL']} if os.environ.get('OPENAI_BASE_URL') else {}))
    team=build_team(OpenAIResponsesModel(model=os.environ['ACADEMY_MODEL'],openai_client=client))
    backend=BraveSearch(os.environ['BRAVE_SEARCH_API_KEY'],enabled=True)
    files={path.name:hashlib.sha256(path.read_bytes()).hexdigest() for path in (Path(__file__).parent/'research_lab').glob('*.py')}
    manifest={'source_revision':args.source_revision,'source_ids':[],
              'code_sha256':files,'model':os.environ['ACADEMY_MODEL'],'search_provider':backend.identity}
    try:
        bundle=await run_research(args.question,backend,team.plan,team.analyze,args.state,
            input_manifest=manifest,workers=args.workers,
            callback=lambda row:print(json.dumps(row),flush=True))
        bundle['actual_sdk_usage']=team.observed_usage
        bundle['trace_summary']=trace_summary(bundle['events'])
        export(bundle,args.output)
    finally:await client.close()

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--live',action='store_true')
    parser.add_argument('--question',required=True)
    parser.add_argument('--source-revision',required=True)
    parser.add_argument('--state',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--workers',type=int,default=3)
    args=parser.parse_args()
    if not args.live:parser.error('--live explicitly authorizes finite real model and search requests')
    for key in ('OPENAI_API_KEY','ACADEMY_MODEL','BRAVE_SEARCH_API_KEY'):
        if not os.environ.get(key):parser.error('missing configured '+key+'; do not print credentials')
    asyncio.run(execute(args))
if __name__=='__main__':main()
