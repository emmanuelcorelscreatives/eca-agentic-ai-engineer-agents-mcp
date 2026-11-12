"""Stages 17–18: real state graph/checkpoint/interrupt; no language model or provider required."""
from typing import TypedDict
from frameworks.common import line_total

class State(TypedDict, total=False):
    price: str
    quantity: int
    total: str
    approved: bool
    disposition: str

def calculate(state: State) -> dict:
    return {"total": line_total(state["price"], state["quantity"])}

def approval(state: State) -> dict:
    from langgraph.types import interrupt
    approved = interrupt({"question": "Approve this fixture order?", "total": state["total"]})
    if type(approved) is not bool:
        raise ValueError("approval must be a boolean")
    return {"approved": approved, "disposition": "approved for review; nothing purchased" if approved else "rejected"}

def build_graph():
    from langgraph.graph import StateGraph, START, END
    from langgraph.checkpoint.memory import InMemorySaver
    builder = StateGraph(State)
    builder.add_node("calculate", calculate)
    builder.add_node("approval", approval)
    builder.add_edge(START, "calculate")
    builder.add_edge("calculate", "approval")
    builder.add_edge("approval", END)
    return builder.compile(checkpointer=InMemorySaver())

def main():
    from langgraph.types import Command
    graph = build_graph()
    config = {"configurable": {"thread_id": "academy-fixture-order"}}
    paused = graph.invoke({"price": "12.50", "quantity": 3}, config)
    print("Paused:", paused)
    # This is a scripted fixture rejection, not a human approval observation.
    print("Resumed:", graph.invoke(Command(resume=False), config))

if __name__ == "__main__":
    main()
