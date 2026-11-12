"""Tool calling and evidence primitives; no hidden model calls or external actions."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Any
import json
import sqlite3
import time

@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    schema: dict
    run: Callable[..., Any]
    requires_approval: bool = False

@dataclass(frozen=True)
class ToolRequest:
    id: str
    name: str
    arguments: dict

@dataclass
class AgentResult:
    text: str
    events: list[dict] = field(default_factory=list)
    stopped_reason: str = 'complete'

class ToolRegistry:
    def __init__(self, tools: list[Tool]):
        self.tools = {t.name:t for t in tools}
        if len(self.tools) != len(tools): raise ValueError('Duplicate tool name')

    def execute(self, call: ToolRequest, approved: bool = False):
        if call.name not in self.tools: raise ValueError('Unknown tool')
        tool=self.tools[call.name]
        required=tool.schema.get('required', [])
        properties=tool.schema.get('properties', {})
        if set(call.arguments)-set(properties): raise ValueError('Unexpected arguments')
        if any(k not in call.arguments for k in required): raise ValueError('Missing required argument')
        types={'string':str,'integer':int,'number':(float,int),'boolean':bool,'array':list,'object':dict}
        for k,v in call.arguments.items():
            expected=properties[k].get('type')
            if expected not in types: raise ValueError('Unsupported schema type')
            if not isinstance(v,types[expected]) or (expected in ('integer','number') and isinstance(v,bool)):
                raise ValueError(f'Invalid type: {k}')
        if tool.requires_approval and not approved: raise PermissionError('Human approval required')
        return tool.run(**call.arguments)

def run_agent(model: Callable[[list[dict]],dict], prompt: str, registry: ToolRegistry,
              max_steps: int=6, max_seconds: float=30.0) -> AgentResult:
    """Provider-independent loop. The caller supplies and labels the model adapter.

    Automatically requested tools never receive approval. External side effects must
    be approved and dispatched by a separate human-reviewed application action.
    """
    if max_steps < 1 or max_seconds <= 0: raise ValueError('Positive budgets required')
    messages=[{'role':'user','content':prompt}]; events=[]; started=time.monotonic(); seen=set()
    for step in range(max_steps):
        if time.monotonic()-started > max_seconds:
            return AgentResult('',events,'time_budget')
        response=model(list(messages))
        if not isinstance(response,dict): raise ValueError('Model response must be an object')
        if response.get('text') is not None:
            return AgentResult(str(response['text']),events)
        calls=response.get('tool_calls')
        if not isinstance(calls,list) or not calls: raise ValueError('Text or tool calls required')
        messages.append({'role':'assistant','tool_calls':calls})
        for data in calls:
            call=ToolRequest(**data)
            if call.id in seen: raise ValueError('Duplicate tool call ID')
            seen.add(call.id)
            try:
                result=registry.execute(call)
                event={'step':step,'id':call.id,'tool':call.name,'ok':True,'result':result}
            except (ValueError,PermissionError) as error:
                event={'step':step,'id':call.id,'tool':call.name,'ok':False,'error':str(error)}
            events.append(event)
            messages.append({'role':'tool','tool_call_id':call.id,'content':json.dumps(event,sort_keys=True)})
    return AgentResult('',events,'step_budget')

class Sessions:
    def __init__(self, path: str):
        self.db=sqlite3.connect(path)
        self.db.execute('CREATE TABLE IF NOT EXISTS events (session TEXT NOT NULL, position INTEGER NOT NULL, payload TEXT NOT NULL, PRIMARY KEY(session,position))')
    def append(self, session: str, payload: dict):
        with self.db:
            position=self.db.execute('SELECT COALESCE(MAX(position),0)+1 FROM events WHERE session=?',(session,)).fetchone()[0]
            self.db.execute('INSERT INTO events VALUES(?,?,?)',(session,position,json.dumps(payload,sort_keys=True)))
    def load(self, session: str):
        return [json.loads(row[0]) for row in self.db.execute('SELECT payload FROM events WHERE session=? ORDER BY position',(session,))]
    def close(self): self.db.close()

def score_grounding(claims: list[dict], sources: dict[str,str]) -> dict:
    """Exact cited-excerpt coverage, not a semantic truth or model-quality score."""
    checks=[]
    for claim in claims:
        source=sources.get(claim.get('source_id'))
        excerpt=claim.get('excerpt','')
        checks.append(bool(source is not None and excerpt and excerpt in source))
    return {'supported':sum(checks),'total':len(checks),'ratio':sum(checks)/len(checks) if checks else 0.0,'checks':checks}
