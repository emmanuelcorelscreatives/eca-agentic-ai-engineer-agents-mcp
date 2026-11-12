"""Real optional CrewAI hierarchical market workflow; never called on import."""
import argparse
import json
from pathlib import Path
from market import Criteria, FixtureSource, run


def build_crew(model: str, data: Path, criteria: Criteria):
    from crewai import Agent, Crew, Task, Process, LLM
    from crewai.tools import tool
    from pydantic import BaseModel, ConfigDict

    class FinalReport(BaseModel):
        model_config = ConfigDict(extra='forbid')
        summary: str
        profiles: list[dict]
        uncertainties: list[str]
        fictional: bool

    reference = run(FixtureSource(data), criteria)

    @tool('fictional_company_research')
    def company_research() -> str:
        """Return the complete approved fictional company metrics and risk evidence."""
        return data.read_text()

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
    analyst = agent('Market analyst', 'Explain sector coverage and explicitly absent live-market evidence.', [company_research])
    screener = agent('Screening analyst', 'Apply the exact deterministic criteria without modifying scores.', [screening_report])
    reviewer = agent('Risk and evidence reviewer', 'Produce a fully supported fictional comparison with uncertainties.', [screening_report])
    research = Task(description='Collect all company profiles, metrics, provenance and concentration risks.',
                    expected_output='Complete fictional company profiles with source locators.', agent=researcher)
    analysis = Task(description='Analyze sector context using only approved data; state there are no live signals.',
                    expected_output='Sector context and explicit data limitations.', agent=analyst, context=[research])
    ranking = Task(description='Call transparent_screening_report and retain its exact profiles ordering and all profile fields.',
                   expected_output='Exact scored profiles, criteria and supporting rule-by-rule evidence.', agent=screener,
                   context=[research, analysis])
    review = Task(description='Review evidence and risks. Return fictional=true, summary, uncertainties and the exact '
                  'profiles array from transparent_screening_report without omitting or changing any field.',
                  expected_output='Structured FinalReport with exact deterministic profiles and explicit uncertainty.',
                  agent=reviewer, context=[research, analysis, ranking], output_pydantic=FinalReport)
    crew = Crew(agents=[researcher, analyst, screener, reviewer], tasks=[research, analysis, ranking, review],
                process=Process.hierarchical, manager_llm=llm, memory=False, verbose=False, max_rpm=10)
    return crew, reference


def validate_output(output: dict, reference: dict):
    if output.get('fictional') is not True or output.get('profiles') != reference['profiles']:
        raise ValueError('model changed or omitted authoritative evidence/scores; report held')
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
