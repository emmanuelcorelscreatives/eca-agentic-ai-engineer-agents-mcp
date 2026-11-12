"""Opt-in actual CrewAI memory connected to the debate's agents/tasks.

Importing/construction alone is not recall evidence. The dictionary-only
ScopedMemory teaching harness remains separate and is never mislabeled here.
"""
from pathlib import Path
import re
from .core import load_facts
from .crew import build_crew

def build_memory_crew(model, fact_path, embedder, storage, run_id, *, authorize_provider=False):
    if not authorize_provider: raise PermissionError('model and embedding memory require explicit authorization')
    if not isinstance(run_id, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,48}', run_id):
        raise ValueError('safe explicit run ID required')
    if not isinstance(embedder, dict) or not embedder.get('provider'):
        raise ValueError('explicit embedding provider configuration required')
    load_facts(fact_path)  # Validate before allocating a fresh store.
    from crewai import Memory
    root = Path(storage)
    root.mkdir(parents=True, exist_ok=False)
    memory = Memory(llm=model, embedder=embedder, storage=str(root))
    shared_scope = '/academy/' + run_id + '/approved'
    # Every task may retrieve approved research. No agent gets a root/private view.
    approved = memory.scope(shared_scope)
    roles = {role: approved for role in ('advocate', 'skeptic', 'reviewer')}
    crew, pack, search = build_crew(model, fact_path, memory_backend=approved, role_memory=roles)
    return crew, pack, search, memory, shared_scope

def run_memory_crew(model, fact_path, embedder, storage, run_id, *, authorize_provider=False):
    crew, pack, search, memory, scope = build_memory_crew(
        model, fact_path, embedder, storage, run_id, authorize_provider=authorize_provider)
    approved = memory.scope(scope)
    fact = pack['facts'][0]
    approved.remember(fact['id'] + ': ' + fact['text'])
    query = fact['id'] + ' ' + fact['text'][:80]
    before = [item.record.content for item in approved.recall(query, limit=3)]
    if not before: raise RuntimeError('actual memory retrieval empty; hold before crew execution')
    result = crew.kickoff(inputs={'topic': pack['topic']})
    if result.pydantic is None: raise ValueError('structured verdict absent; preserve this run evidence')
    from .core import validate_verdict
    verdict = validate_verdict(result.pydantic.model_dump(), pack)
    # Scoped reset: do not reset stores belonging to any other exercise/run.
    memory.reset(scope=scope)
    after = [item.record.content for item in approved.recall(query, limit=3)]
    if after: raise RuntimeError('actual memory reset left records; hold result')
    return {'execution': 'actual-memory-and-provider', 'scope': scope, 'memory_before': before,
            'memory_after_reset': after, 'verdict': verdict, 'tool_calls': search.calls,
            'task_outputs': [task.model_dump(mode='json') for task in result.tasks_output]}
