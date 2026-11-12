"""Stage 16: modern create_agent with a deterministic local function tool. Optional live run."""
from frameworks.common import line_total, require_run

def main():
    env = require_run("OPENAI_API_KEY", "COURSE_MODEL")
    from langchain.agents import create_agent
    from langchain_openai import ChatOpenAI
    agent = create_agent(model=ChatOpenAI(model=env["COURSE_MODEL"]), tools=[line_total],
        system_prompt="Use line_total for fixture arithmetic. Do not claim a purchase occurred.")
    result = agent.invoke({"messages": [{"role": "user", "content": "Total three items at 12.50 each."}]},
        config={"recursion_limit": 8})
    print(result["messages"][-1].content)

if __name__ == "__main__":
    main()
