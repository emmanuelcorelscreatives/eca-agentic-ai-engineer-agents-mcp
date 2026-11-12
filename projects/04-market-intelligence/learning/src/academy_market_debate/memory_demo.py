"""Optional genuine CrewAI memory probe; SDK/model/embedder calls are explicit."""
from pathlib import Path
import uuid

def probe_memory(model, embedder, storage, *, authorize_provider=False):
    if not authorize_provider: raise PermissionError('memory may call a model and embedding provider')
    from crewai import Memory
    root=Path(storage)
    root.mkdir(parents=True,exist_ok=False)
    memory=Memory(llm=model,embedder=embedder,storage=str(root))
    run_scope='/academy/'+uuid.uuid4().hex
    scoped=memory.scope(run_scope)
    scoped.remember('F1: Fictional Alder Retail delivered 184 of 200 trial orders on time.')
    matches=scoped.recall('How many fictional trial orders arrived on time?',limit=3)
    before=[m.record.content for m in matches]
    if not before: raise RuntimeError('genuine backend returned no observation; do not report success')
    memory.reset(scope=run_scope)
    after=[m.record.content for m in scoped.recall('trial orders',limit=3)]
    if after: raise RuntimeError('backend reset did not clear this scope')
    return {'actual_backend':True,'scope':run_scope,'before':before,'after':after}
