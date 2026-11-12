"""Async task-local parentage and actual dispatch boundaries, with append-only JSONL."""
from contextlib import contextmanager, asynccontextmanager
from contextvars import ContextVar
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from threading import Lock
import time
import uuid

_parent = ContextVar('academy_trace_parent', default=None)

class CorrelatedTrace:
    def __init__(self, path, run_id=None):
        self.path = Path(path)
        self.run_id = run_id or str(uuid.uuid4())
        self._lock = Lock()
        # Exclusive creation prevents accidental append into a different historical run.
        self.fd = os.open(self.path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_APPEND, 0o600)

    def _write(self, event):
        body = (json.dumps(event, sort_keys=True) + '\n').encode()
        with self._lock:
            offset = 0
            while offset < len(body): offset += os.write(self.fd, body[offset:])
            os.fsync(self.fd)

    @contextmanager
    def span(self, name, kind, *, model=None):
        if name not in {'workflow', 'research', 'proposal', 'risk', 'approval', 'execute', 'model_dispatch', 'mcp_dispatch', 'recovery'}:
            raise ValueError('use a fixed span identifier, not user content')
        if kind not in {'workflow', 'agent', 'model', 'tool', 'approval', 'order'}:
            raise ValueError('invalid span kind')
        old_parent = _parent.get()
        event = {'run_id': self.run_id, 'span_id': str(uuid.uuid4()),
                 'parent_span_id': old_parent[1] if old_parent and old_parent[0] == self.run_id else None,
                 'name': name, 'kind': kind, 'at': datetime.now(timezone.utc).isoformat()}
        if model is not None: event['model'] = model
        token = _parent.set((self.run_id, event['span_id']))
        start = time.monotonic()
        self._write({**event, 'phase': 'started'})
        try:
            yield event
        except BaseException as exc:
            event['outcome'] = 'failed'
            event['error_type'] = type(exc).__name__
            raise
        else: event['outcome'] = 'success'
        finally:
            _parent.reset(token)
            event['duration_seconds'] = time.monotonic() - start
            # Dispatch hooks add only validated counts/hashes; no prompt/response bodies.
            allowed = {'run_id', 'span_id', 'parent_span_id', 'name', 'kind', 'at', 'model',
                       'outcome', 'error_type', 'duration_seconds', 'input_sha256',
                       'response_sha256', 'input_tokens', 'output_tokens', 'cached_input_tokens'}
            self._write({**{k:v for k,v in event.items() if k in allowed}, 'phase':'finished'})

    @asynccontextmanager
    async def aspan(self, name, kind, **kwargs):
        with self.span(name, kind, **kwargs) as event: yield event

    def close(self):
        with self._lock:
            if self.fd is not None: os.close(self.fd); self.fd = None


def _sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def _usage(event, response):
    event['response_sha256'] = _sha(response)
    usage = response.get('usage') if isinstance(response, dict) else None
    if isinstance(usage, dict):
        details = usage.get('prompt_tokens_details') or {}
        for destination, value in (
            ('input_tokens', usage.get('prompt_tokens', usage.get('input_tokens'))),
            ('output_tokens', usage.get('completion_tokens', usage.get('output_tokens'))),
            ('cached_input_tokens', details.get('cached_tokens'))):
            if type(value) is int and value >= 0: event[destination] = value


def dispatch_model(trace, invoke, *, model, payload):
    """invoke receives the ACTUAL request; this hook does not mock provider output."""
    with trace.span('model_dispatch', 'model', model=model) as event:
        event['input_sha256'] = _sha(payload)
        result = invoke(model=model, payload=payload)
        _usage(event, result)
        return result


async def dispatch_mcp(trace, session, *, tool_name, arguments):
    """Wrap an actual MCP ClientSession.call_tool coroutine. No model approval implied."""
    async with trace.aspan('mcp_dispatch', 'tool') as event:
        event['input_sha256'] = _sha({'tool':tool_name, 'arguments':arguments})
        result = await session.call_tool(tool_name, arguments=arguments)
        # Do not serialize opaque SDK internals or tool text into public telemetry.
        event['response_sha256'] = _sha(result.model_dump(mode='json'))
        if getattr(result, 'isError', False): raise RuntimeError('MCP tool returned error')
        return result
