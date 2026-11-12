"""Stage 23: AutoGen AgentChat API, not legacy 0.2 imports. Optional live run."""
import asyncio
from frameworks.common import line_total, require_run

async def run(model):
    from autogen_agentchat.agents import AssistantAgent
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    client = OpenAIChatCompletionClient(model=model)
    try:
        agent = AssistantAgent("academy_order_assistant", model_client=client, tools=[line_total],
            system_message="Use line_total for fixture arithmetic. Never claim a purchase.", reflect_on_tool_use=True)
        result = await agent.run(task="Total three items at 12.50 each.")
        print(result.messages[-1].content)
    finally:
        await client.close()

def main():
    env = require_run("OPENAI_API_KEY", "COURSE_MODEL")
    asyncio.run(run(env["COURSE_MODEL"]))

if __name__ == "__main__":
    main()
