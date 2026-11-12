"""Stages 11–15: two-agent sequential work with explicit task context. Optional live run."""
from frameworks.common import require_run

def main():
    env = require_run("OPENAI_API_KEY", "COURSE_MODEL")
    from crewai import Agent, Crew, LLM, Process, Task
    llm = LLM(model="openai/" + env["COURSE_MODEL"], temperature=0)
    researcher = Agent(role="Fixture analyst", goal="Analyze only the supplied educational company data",
        backstory="An Academy analyst who distinguishes synthetic fixtures from live markets.", llm=llm, allow_delegation=False)
    reviewer = Agent(role="Evidence reviewer", goal="Flag claims unsupported by the fixture",
        backstory="An Academy reviewer who checks numerical statements.", llm=llm, allow_delegation=False)
    research = Task(description="Fixture company A has revenue 120 and cost 90. Calculate operating margin; label this synthetic.",
        expected_output="Revenue, cost, margin and the synthetic-data label.", agent=researcher)
    review = Task(description="Check the preceding arithmetic and label; do not recommend investments.",
        expected_output="A concise checked explanation, including any errors.", agent=reviewer, context=[research])
    result = Crew(agents=[researcher, reviewer], tasks=[research, review], process=Process.sequential, verbose=False).kickoff()
    print(result)

if __name__ == "__main__":
    main()
