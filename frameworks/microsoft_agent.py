"""Stage 23: Microsoft Agent Framework Foundry client. Optional live run."""
import asyncio
from frameworks.common import line_total, require_run

async def run(env):
    from agent_framework import Agent
    from agent_framework.foundry import FoundryChatClient
    from azure.identity import AzureCliCredential
    with AzureCliCredential() as credential:
        agent = Agent(client=FoundryChatClient(project_endpoint=env["FOUNDRY_PROJECT_ENDPOINT"],
            model=env["FOUNDRY_MODEL"], credential=credential),
            instructions="Use line_total to calculate synthetic order totals; never send orders.", tools=[line_total])
        print(await agent.run("Total three items at 12.50 each."))

def main():
    env = require_run("FOUNDRY_PROJECT_ENDPOINT", "FOUNDRY_MODEL")
    asyncio.run(run(env))

if __name__ == "__main__":
    main()
