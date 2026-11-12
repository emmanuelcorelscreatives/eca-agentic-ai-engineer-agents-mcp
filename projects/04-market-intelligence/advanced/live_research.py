"""Explicit live hierarchical run with real task traces and validated custom memory."""
import argparse
from dataclasses import asdict
from importlib.metadata import version
import importlib.util
import json
from pathlib import Path
import sys
from research_lab import BASE, ResearchMemory, canonical, digest, evidence_registry, review_numeric_claims, market


def build(model: str, trace_path: Path):
    # Lazy loading: offline tools never import a provider or optional SDK.
    sys.path.insert(0,str(BASE))
    try:
        spec=importlib.util.spec_from_file_location('eca_market_live_adapter_advanced',BASE/'crewai_adapter.py')
        adapter=importlib.util.module_from_spec(spec);spec.loader.exec_module(adapter)
    finally:sys.path.pop(0)
    from crewai.tools import tool
    source=market.FixtureSource(BASE/'companies.json')
    defects=review_numeric_claims(source.companies(),evidence_registry())
    if defects:raise ValueError(defects)
    criteria=market.Criteria()
    crew,reference=adapter.build_crew(model,BASE/'companies.json',criteria)
    source_sha=digest({'companies':json.loads((BASE/'companies.json').read_text()),
                       'ledger':json.loads((BASE/'synthetic-ledger.json').read_text())})
    memory=ResearchMemory();memory.put(source_sha,asdict(criteria),reference,reference)

    @tool('validated_research_memory')
    def read_memory() -> str:
        """Read exact validated research for the current source and criteria identity."""
        return json.dumps(memory.get(source_sha,asdict(criteria)))

    for agent in crew.agents:
        agent.tools=[*agent.tools,read_memory]
    if trace_path.exists():raise ValueError('never overwrite a prior run trace')
    with trace_path.open('x') as handle:
        handle.write(json.dumps(dict(event='run_configuration',crewai_version=version('crewai'),
            model=model,source_sha256=source_sha,process='hierarchical',fictional=True,
            memory='validated custom tool; framework embedding memory disabled',
            max_iter_per_specialist=6,max_rpm=10,provider_calls='not yet started'))+'\n')
    def retain_actual_task(output):
        # Callback records actual SDK task outputs, never synthetic execution traces.
        payload=output.model_dump(mode='json') if hasattr(output,'model_dump') else {'raw':str(output)}
        with trace_path.open('a') as handle:
            handle.write(json.dumps(dict(event='actual_task_output',output=payload))+'\n')
    for task in crew.tasks:task.callback=retain_actual_task
    return crew,reference,adapter


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-live',action='store_true');parser.add_argument('--model',required=True)
    parser.add_argument('--trace',type=Path,required=True)
    args=parser.parse_args()
    if not args.run_live:parser.error('--run-live required; invokes your configured model/provider')
    crew,reference,adapter=build(args.model,args.trace)
    output=crew.kickoff()
    if output.pydantic is None:raise RuntimeError('structured output missing; no approval')
    report=adapter.validate_output(output.pydantic.model_dump(),reference)
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
