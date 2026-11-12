"""Stages 6–10: function tool and explicit specialist handoff. Optional live run."""
from frameworks.common import line_total, require_run

def main():
    env = require_run("OPENAI_API_KEY", "COURSE_MODEL")
    from agents import Agent, Runner, function_tool, set_tracing_disabled
    set_tracing_disabled(True)
    tool = function_tool(line_total)
    specialist = Agent(name="Order specialist", model=env["COURSE_MODEL"],
        instructions="Calculate fixture order totals using line_total. Never send email or place orders.", tools=[tool])
    router = Agent(name="Course router", model=env["COURSE_MODEL"],
        instructions="Delegate order arithmetic to the order specialist.", handoffs=[specialist])
    result = Runner.run_sync(router, "Find the total for three units at 12.50 each.", max_turns=4)
    print(result.final_output)

if __name__ == "__main__":
    main()
