# Genuine LangGraph integration

`langgraph_adapter.py` builds a real `StateGraph` over the tested task core, rather than labeling a handwritten state machine as LangGraph. Install `langgraph` and `langgraph-checkpoint-sqlite` in a dedicated environment and freeze the versions actually tested before recording.

```python
from pathlib import Path
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command
from sidekick import TaskStore, Step, FixtureBrowser, ArtifactTools
from langgraph_adapter import build_graph

store = TaskStore(Path('task-execution.sqlite'))
reader = FixtureBrowser(Path('fixtures'))
tools = ArtifactTools(reader, Path('artifacts'))
task = store.create('Save a synthetic finding', [
    Step('save', 'finding.txt', 'Synthetic workshop: USD 30', 'artifact saved')
])
config = {'configurable': {'thread_id': task}}
try:
    with SqliteSaver.from_conn_string('graph-checkpoints.sqlite') as checkpoints:
        graph = build_graph(store, tools, checkpoints)
        paused = graph.invoke({'task_id': task, 'status': 'new'}, config)
        print(paused)  # Inspect the proposed content and hash before approving.
        request = paused['__interrupt__'][0].value
        # This call is an explicit human decision, not automatic model approval.
        result = graph.invoke(Command(resume={
            'decision': 'approve', 'step_sha256': request['step_sha256']
        }), config)
        print(result)
finally:
    store.close()
```

The interrupt node does no effects before pausing. Exact step hashes bind decisions; edited actions need a fresh decision. TaskStore's persisted `executing` state prevents silent replay after an outcome becomes unknown. Set a bounded `recursion_limit` for long plans; do not interpret an exhausted graph recursion budget as a failed external action to retry.

Primary documentation checked 2026-11-12:

- [LangGraph interrupt and Command](https://reference.langchain.com/python/langgraph/types/interrupt)
- [SqliteSaver context manager](https://reference.langchain.com/python/langgraph.checkpoint.sqlite/SqliteSaver/from_conn_string)

A separate installed-SDK test actually ran the graph with SqliteSaver, paused before the file effect, closed/reopened the graph database, resumed with the exact approval hash, and verified the saved artifact and complete state. Direct pins and the resolved environment are included beside this file. This proves the checkpoint/interrupt integration, not live-model planning or all application behavior.
