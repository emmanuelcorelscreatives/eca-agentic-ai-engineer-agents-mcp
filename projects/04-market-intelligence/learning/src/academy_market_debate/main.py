import argparse
import importlib.metadata
import json
from pathlib import Path
from .core import configuration,load_facts,FactSearch

def main():
    p=argparse.ArgumentParser(description='Fixed fictional market debate. Offline by default; no fabricated model responses.')
    p.add_argument('--facts',type=Path,required=True)
    p.add_argument('--run-live',action='store_true')
    p.add_argument('--flow',action='store_true')
    p.add_argument('--process',choices=['sequential','hierarchical'],default='sequential')
    p.add_argument('--model')
    p.add_argument('--output',type=Path)
    args=p.parse_args()
    pack=load_facts(args.facts)
    if args.run_live:
        if not args.model: p.error('--model is mandatory for a real provider run')
        from .crew import run_live,make_flow
        result=make_flow(args.model,args.facts,args.process).kickoff() if args.flow else run_live(args.model,args.facts,args.process)
    else:
        agents,tasks=configuration()
        result={'execution':'offline-configuration-and-search-only','fictional':True,
                'roles':list(agents),'task_order':list(tasks),'context_edges':{k:v['context'] for k,v in tasks.items()},
                'facts':FactSearch(pack).search('*'),'model_output':None}
    encoded=json.dumps(result,indent=2)
    if args.output:
        with args.output.open('x') as f: f.write(encoded+'\n')
    print(encoded)
if __name__=='__main__': main()
