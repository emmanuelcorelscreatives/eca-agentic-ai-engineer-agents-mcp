"""Stage 22: typed output and dependency injection. Optional live run."""
from dataclasses import dataclass
from frameworks.common import line_total, require_run

@dataclass
class OrderContext:
    unit_price: str
    quantity: int

def main():
    env = require_run("OPENAI_API_KEY", "COURSE_MODEL")
    from pydantic import BaseModel
    from pydantic_ai import Agent, RunContext
    class Summary(BaseModel):
        total: str
        fixture_only: bool
    agent = Agent("openai:" + env["COURSE_MODEL"], deps_type=OrderContext, output_type=Summary,
        instructions="Get the total using order_total. This is a synthetic order; set fixture_only true.")
    # Publish the runtime annotation: postponed/local references are avoided for SDK introspection.
    def order_total(ctx):
        """Return the exact total for the current synthetic order."""
        return line_total(ctx.deps.unit_price, ctx.deps.quantity)
    order_total.__annotations__ = {"ctx": RunContext[OrderContext], "return": str}
    agent.tool(order_total)
    print(agent.run_sync("Summarize this order.", deps=OrderContext("12.50", 3)).output)

if __name__ == "__main__":
    main()
