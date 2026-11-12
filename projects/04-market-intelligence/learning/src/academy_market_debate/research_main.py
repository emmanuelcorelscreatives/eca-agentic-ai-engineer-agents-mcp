"""External-source lesson CLI: direct HTTPS observation or explicitly opted-in crew."""
import argparse
import json
from pathlib import Path
from .external_research import ExternalResearch, ResearchQuery, run_research

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--query',required=True)
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--observe-http',action='store_true',help='Make bounded real HTTPS requests, without any model')
    mode.add_argument('--run-crew',action='store_true',help='Explicitly invoke external HTTPS plus configured model')
    parser.add_argument('--model')
    parser.add_argument('--source',action='append',choices=['crewai-tools','crewai-tasks','crewai-memory'])
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    query=ResearchQuery(args.query)
    if args.output.exists(): parser.error('output already exists; preserve previous evidence')
    search=ExternalResearch(source_ids=tuple(args.source or ['crewai-tools','crewai-tasks']))
    # Reserve the output before starting I/O; failures retain their real type, not a fake report.
    with args.output.open('x') as output:
        try:
            if args.run_crew:
                if not args.model: parser.error('--model required for crew execution')
                result=run_research(args.model,query.query,authorize_external_and_provider=True,search=search)
            else:
                result={'execution':'actual-https-no-model','query':query.query,
                        'results':search.search(query.query),'http_attempts':search.requests}
            output.write(json.dumps(result,indent=2)+'\n')
        except Exception as error:
            output.write(json.dumps({'execution':'FAILED_RETAINED_DO_NOT_AUTOMATICALLY_REPLAY',
                                     'error_type':type(error).__name__,'http_attempts':search.requests,
                                     'known_observations':search.observations})+'\n')
            raise
    print(str(args.output))

if __name__=='__main__':main()
