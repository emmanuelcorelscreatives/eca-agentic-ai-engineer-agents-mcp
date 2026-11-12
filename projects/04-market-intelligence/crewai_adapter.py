"""Real optional CrewAI hierarchical market workflow; never called on import."""
import argparse
import json
from pathlib import Path
from market import Criteria, FixtureSource, run


def build_crew(model: str, data: Path, criteria: Criteria):
    from crewai import Agent, Crew, Task, Process, LLM
    from crewai.tools import tool
    from pydantic import BaseModel, ConfigDict
    from advanced.sources import FixtureResearchAdapter, research_snapshot

    class FinalReport(BaseModel):
        model_config = ConfigDict(extra='forbid')
        summary: str
        profiles: list[dict]
        uncertainties: list[str]
        fictional: bool
        company_research: dict[str, dict]
        market_research: dict[str, dict]
        research_source_sha256: str

    reference = run(FixtureSource(data), criteria)
    companies = FixtureSource(data).companies()
    research_source = FixtureResearchAdapter(Path(__file__).with_name('advanced') / 'research_sources.json')
    snapshot = research_snapshot(research_source, companies)
    if any(result['status'] == 'error' for group in ('companies', 'markets') for result in snapshot[group].values()):
        raise ValueError('research source failed validation; crew construction held')
    reference = {**reference, 'company_research': snapshot['companies'],
                 'market_research': snapshot['markets'],
                 'research_source_sha256': snapshot['source_sha256']}

    @tool('fictional_company_research')
    def company_research() -> str:
        """Return fictional business, product, competitor and numeric source records."""
        return json.dumps({'financial_records': json.loads(data.read_text()),
                           'company_research': snapshot['companies'],
                           'source_sha256': snapshot['source_sha256'], 'fictional': True})

    @tool('dated_market_conditions')
    def market_conditions() -> str:
        """Return dated fictional industry conditions and reproducible signals with citations."""
        return json.dumps({'market_research': snapshot['markets'],
                           'source_sha256': snapshot['source_sha256'], 'fictional': True})

    @tool('transparent_screening_report')
    def screening_report() -> str:
        """Calculate the authoritative deterministic criteria, scores and evidence report."""
        return json.dumps(reference)

    llm = LLM(model=model, temperature=0)
    def agent(role, goal, tools):
        return Agent(role=role, goal=goal,
                     backstory='Academy analyst using only the supplied fictional evidence. Never invent facts.',
                     llm=llm, tools=tools, allow_delegation=False, max_iter=6)
    researcher = agent('Company researcher', 'Collect every fictional company profile and source locator.', [company_research])
    analyst = agent('Market analyst', 'Evaluate the dated fictional sector conditions and signals; distinguish them from real markets.', [company_research, market_conditions])
    screener = agent('Screening analyst', 'Apply the exact deterministic criteria without modifying scores.', [screening_report])
    reviewer = agent('Risk and evidence reviewer', 'Produce a fully supported fictional comparison with uncertainties.', [screening_report])
    research = Task(description='Collect business model, products, competitive positioning, company metrics, provenance and risks. '
                    'Every business/product/competitor assertion must cite the exact supplied source-document ID; do not invent market shares.',
                    expected_output='Fictional company profiles covering business, product, competition, metrics and evidence IDs.', agent=researcher)
    analysis = Task(description='Call dated_market_conditions. Evaluate software demand/cost, hardware orders/lead-time and services inquiry '
                    'signals, retaining scenario dates, arithmetic, source IDs and uncertainty. These are fictional conditions, not live signals.',
                    expected_output='Dated fictional sector-condition analysis with source-backed signals and limitations.', agent=analyst, context=[research])
    ranking = Task(description='Call transparent_screening_report and retain its exact profiles ordering and all profile fields.',
                   expected_output='Exact scored profiles, criteria and supporting rule-by-rule evidence.', agent=screener,
                   context=[research, analysis])
    review = Task(description='Review evidence and risks. Return fictional=true, summary, uncertainties and the exact '
                  'profiles array, company_research, market_research and research_source_sha256 from transparent_screening_report '
                  'without omitting or changing any field. Reject unsupported business and sector assertions; preserve explicit missing-source states.',
                  expected_output='Structured FinalReport with exact company/market research, deterministic profiles and explicit uncertainty.',
                  agent=reviewer, context=[research, analysis, ranking], output_pydantic=FinalReport)
    crew = Crew(agents=[researcher, analyst, screener, reviewer], tasks=[research, analysis, ranking, review],
                process=Process.hierarchical, manager_llm=llm, memory=False, verbose=False, max_rpm=10)
    return crew, reference


def validate_output(output: dict, reference: dict):
    if output.get('fictional') is not True or output.get('profiles') != reference['profiles']:
        raise ValueError('model changed or omitted authoritative evidence/scores; report held')
    for field in ('company_research', 'market_research', 'research_source_sha256'):
        if field in reference and output.get(field) != reference[field]:
            raise ValueError(f'model changed or omitted authoritative {field}; report held')
    return output


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run-live', action='store_true')
    p.add_argument('--model', required=True, help='Explicit configured CrewAI provider/model identifier')
    p.add_argument('--data', type=Path, default=Path(__file__).with_name('companies.json'))
    args = p.parse_args()
    if not args.run_live: p.error('--run-live is required: this invokes a paid/configured provider')
    crew, reference = build_crew(args.model, args.data, Criteria())
    result = crew.kickoff()
    if result.pydantic is None: raise RuntimeError('structured output missing; report held')
    output = validate_output(result.pydantic.model_dump(), reference)
    print(json.dumps(dict(report=output, deterministic_reference=reference), indent=2))

if __name__ == '__main__': main()
