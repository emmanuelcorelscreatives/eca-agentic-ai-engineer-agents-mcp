"""Application-owned approval/state/telemetry around real framework agents.
This coordinator is ordinary Python, not a claim of SDK workflow execution.
"""
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
import json
import os
import tempfile

@dataclass(frozen=True)
class Approval:
    ticket_id: str
    draft_sha256: str
    approved: bool
    reviewer: str

def digest(draft):
    return hashlib.sha256(json.dumps(draft,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def route(ticket):
    return {'damaged':'policy','delivery':'delivery'}.get(ticket['category'],'human_review')

def approved_transition(draft, approval: Approval):
    if not isinstance(approval, Approval) or not approval.approved or not approval.reviewer.strip():
        raise PermissionError('Explicit reviewer approval required')
    if approval.ticket_id != draft['ticket_id'] or approval.draft_sha256 != digest(draft):
        raise PermissionError('Approval does not bind this exact draft')
    return {'status':'approved_local_draft','draft':dict(draft),'reviewer':approval.reviewer,
            'sent':False}

def save_state(path: Path, state: dict):
    """Atomic application envelope; SDK save_state output may be nested in payload."""
    payload = json.dumps({'schema_version':1,'payload':state},sort_keys=True)
    path.parent.mkdir(parents=True,exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=path.parent,prefix='.state-')
    try:
        with os.fdopen(fd,'w') as stream:
            stream.write(payload); stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary,path)
    finally:
        if os.path.exists(temporary): os.unlink(temporary)

def load_state(path: Path):
    envelope=json.loads(path.read_text())
    if envelope.get('schema_version') != 1 or not isinstance(envelope.get('payload'),dict):
        raise ValueError('Unsupported state envelope')
    return envelope['payload']

async def coordinate(ticket, specialists, *, run_id):
    name = route(ticket)
    trace = [{'run_id':run_id,'step':'route','specialist':name,'ticket_id':ticket['id']}]
    if name == 'human_review':
        return {'status':'held','trace':trace,'result':None}
    if name not in specialists:
        raise ValueError('Configured specialist missing')
    result = await specialists[name](dict(ticket))
    trace.append({'run_id':run_id,'step':'specialist_result','specialist':name,'ticket_id':ticket['id']})
    return {'status':'draft_only','trace':trace,'result':result}
