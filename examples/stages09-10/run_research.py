"""Offline research capstone; run from repository root."""
import asyncio
import argparse
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
PROJECT=ROOT/'projects/03-deep-research'
sys.path.insert(0,str(PROJECT))
from research_lab.runtime import run, save_checkpoint
from research_lab.search import FixtureSearch
from research_lab.reporting import export_bundle, markdown
from research_lab.evaluation import evaluate
from research_lab.interface import build_ui
parser=argparse.ArgumentParser()
parser.add_argument('--question',default='Community workshop scheduling')
parser.add_argument('--export',type=Path)
parser.add_argument('--ui',action='store_true')
args=parser.parse_args()
records=json.loads((PROJECT/'data/s09-workshop-sources.json').read_text())['records']
if args.ui:
    build_ui(records).queue().launch(server_name='127.0.0.1',share=False)
else:
    bundle=asyncio.run(run(args.question,FixtureSearch(records)))
    print(markdown(bundle)); print(json.dumps(evaluate(bundle),indent=2))
    if args.export:
        export_bundle(bundle,args.export); save_checkpoint(bundle,args.export/'checkpoint.json')
