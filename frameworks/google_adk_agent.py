"""Stage 21: root_agent factory for ADK CLI; import does not construct/run a model."""
import os
from frameworks.common import line_total

def build_agent():
    from google.adk.agents.llm_agent import Agent
    model = os.environ.get("GOOGLE_MODEL", "").strip()
    if not model:
        raise ValueError("Set GOOGLE_MODEL to an available Gemini model identifier")
    return Agent(name="academy_order_assistant", model=model,
        instruction="Use line_total for fixture calculations. Never send orders.", tools=[line_total])
