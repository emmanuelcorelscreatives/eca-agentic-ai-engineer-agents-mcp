"""Real CrewAI adapters. Building requires SDK; kickoff additionally requires credentials."""
import json
from .core import configuration, load_facts, FactSearch, validate_verdict

def verdict_model():
    from pydantic import BaseModel, ConfigDict, Field
    from typing import Literal
    class DebateVerdict(BaseModel):
        model_config = ConfigDict(extra='forbid')
        decision: Literal['bounded_pilot','defer']
        fact_ids: list[str] = Field(min_length=2, max_length=4)
        rationale: str = Field(min_length=1, max_length=2000)
        uncertainties: list[str] = Field(min_length=1, max_length=5)
        fictional: Literal[True]
    return DebateVerdict

def build_tools(search):
    from crewai.tools import tool
    @tool('search_fictional_retailer_facts')
    def search_facts(query: str, max_results: int = 4) -> str:
        """Search the fixed fictional course fact pack; '*' retrieves all four facts. No internet access."""
        return json.dumps(search.search(query, max_results))
    return search_facts

def build_crew(model, fact_path, process='sequential'):
    from crewai import Agent, Task, Crew, Process, LLM
    if process not in {'sequential','hierarchical'}: raise ValueError('unsupported process')
    pack=load_facts(fact_path)
    agents_cfg,tasks_cfg=configuration()
    search=FactSearch(pack,limit=6)
    tool=build_tools(search)
    llm=LLM(model=model,temperature=0,timeout=60,max_tokens=1200)
    agents={name:Agent(**cfg,llm=llm,tools=[tool],allow_delegation=False,
                       max_iter=4,max_retry_limit=0,max_execution_time=90,
                       respect_context_window=True,verbose=False) for name,cfg in agents_cfg.items()}
    tasks={}
    for name,cfg in tasks_cfg.items():
        kwargs=dict(description=cfg['description'],expected_output=cfg['expected_output'],
                    agent=agents[cfg['agent']],context=[tasks[k] for k in cfg['context']])
        if name=='verdict': kwargs['output_pydantic']=verdict_model()
        tasks[name]=Task(**kwargs)
    kwargs=dict(agents=list(agents.values()),tasks=list(tasks.values()),
                process=getattr(Process,process),memory=False,verbose=False,max_rpm=6)
    if process=='hierarchical': kwargs['manager_llm']=llm
    return Crew(**kwargs),pack,search

def run_live(model,fact_path,process='sequential'):
    crew,pack,search=build_crew(model,fact_path,process)
    output=crew.kickoff(inputs={'topic':pack['topic']})
    if output.pydantic is None: raise ValueError('structured output absent; held')
    verdict=validate_verdict(output.pydantic.model_dump(),pack)
    return {'execution':'actual-provider','process':process,'tool_calls':search.calls,
            'verdict':verdict,'tasks':[{'description':t.description,'raw':t.raw} for t in output.tasks_output]}

def make_flow(model,fact_path,process='sequential'):
    from crewai.flow.flow import Flow,start,listen
    class DebateFlow(Flow):
        @start()
        def prepare(self):
            pack=load_facts(fact_path)
            self.state['topic']=pack['topic']
            return pack['topic']
        @listen(prepare)
        def debate(self, topic):
            report=run_live(model,fact_path,process)
            self.state['decision']=report['verdict']['decision']
            return report
    return DebateFlow()
