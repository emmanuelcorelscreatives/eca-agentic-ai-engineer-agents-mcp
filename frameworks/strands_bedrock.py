"""Stage 22: explicitly configured Bedrock provider and read-only local tool. Optional live run."""
from frameworks.common import line_total, require_run

def main():
    env = require_run("AWS_REGION", "BEDROCK_MODEL_ID")
    from strands import Agent, tool
    from strands.models import BedrockModel
    model = BedrockModel(model_id=env["BEDROCK_MODEL_ID"], region_name=env["AWS_REGION"])
    agent = Agent(model=model, tools=[tool(line_total)],
        system_prompt="Use line_total for synthetic order arithmetic; no purchases or email.")
    print(agent("Total three items priced 12.50 each."))

if __name__ == "__main__":
    main()
