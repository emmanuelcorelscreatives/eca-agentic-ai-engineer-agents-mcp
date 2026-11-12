"""Optional genuine LangGraph checkpoint/interrupt integration over TaskStore.

No model calls. Use SqliteSaver for persistent graph checkpoints and a distinct
TaskStore DB for actual execution outcomes. See FRAMEWORKS.md for the API sources.
"""
import json
from typing import TypedDict
from sidekick import Step

class GraphState(TypedDict):
    task_id: str
    status: str

def build_graph(store, executor, checkpointer):
    from langgraph.graph import StateGraph, START, END
    from langgraph.types import interrupt

    def execute(state):
        return {'status':store.advance(state['task_id'],executor)}
    def approval(state):
        rows=[row for row in store.checklist(state['task_id']) if row['state']!='complete']
        if not rows or rows[0]['state']!='awaiting_approval':
            raise ValueError('approval target is no longer current')
        row=rows[0]; step=Step(**json.loads(row['payload']))
        # LangGraph re-runs this node on resume: there are deliberately no
        # effects before interrupt, and the returned hash must still match.
        answer=interrupt({'task_id':state['task_id'],'number':row['number'],
                          'step':json.loads(row['payload']),'step_sha256':step.digest()})
        if not isinstance(answer,dict) or answer.get('step_sha256')!=step.digest():
            raise ValueError('approval does not bind the current step')
        decision=answer.get('decision')
        if decision not in {'approve','reject','edit'}: raise ValueError('invalid approval decision')
        replacement=Step(**answer['replacement']) if decision=='edit' else None
        store.decide(state['task_id'],row['number'],decision,replacement)
        return {'status':'decision_recorded'}
    builder=StateGraph(GraphState)
    builder.add_node('execute',execute); builder.add_node('approval',approval)
    builder.add_edge(START,'execute')
    builder.add_conditional_edges('execute',lambda state: 'approval' if state['status']=='awaiting_approval' else ('execute' if state['status']=='step_complete' else END),
                                  {'approval':'approval','execute':'execute',END:END})
    builder.add_edge('approval','execute')
    return builder.compile(checkpointer=checkpointer)
