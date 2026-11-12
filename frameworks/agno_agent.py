"""Stage 24: Agno function tool and explicit model. Optional live run."""
from frameworks.common import line_total, require_run

def main():
    env = require_run("OPENAI_API_KEY", "COURSE_MODEL")
    from agno.agent import Agent
    from agno.models.openai import OpenAIChat
    agent = Agent(model=OpenAIChat(id=env["COURSE_MODEL"]), tools=[line_total],
        instructions="Use line_total for synthetic order calculations; no purchases or external actions.")
    result = agent.run("Total three units at 12.50 each.")
    print(result.content)

if __name__ == "__main__":
    main()
