"""Deterministic application exercises; these are not SDK/model observations."""
from __future__ import annotations

import asyncio
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re
import sqlite3
import uuid
from collections.abc import Awaitable, Callable

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / 'data/s06-catalogue.json'
CASES = ROOT / 'data/s07-support-cases.json'


@dataclass(frozen=True)
class Course:
    course_id: str
    title: str
    level: str
    prerequisites: list[str]

    @classmethod
    def parse(cls, raw: dict) -> 'Course':
        if set(raw) != {'course_id', 'title', 'level', 'prerequisites'}:
            raise ValueError('unexpected course fields')
        if not isinstance(raw['course_id'], str) or not re.fullmatch(r'ECA-[0-9]{3}', raw['course_id']):
            raise ValueError('course_id must match ECA-NNN')
        if raw['level'] not in {'beginner', 'intermediate', 'advanced'}:
            raise ValueError('unknown level')
        if not isinstance(raw['title'], str) or not raw['title'].strip():
            raise ValueError('title required')
        if not isinstance(raw['prerequisites'], list) or any(not isinstance(x, str) for x in raw['prerequisites']):
            raise ValueError('prerequisites must be a string list')
        return cls(**raw)


def lookup_course(course_id: str) -> dict:
    if not isinstance(course_id, str) or not re.fullmatch(r'ECA-[0-9]{3}', course_id):
        raise ValueError('invalid course id')
    courses = [Course.parse(x) for x in json.loads(CATALOG.read_text())]
    match = next((asdict(x) for x in courses if x.course_id == course_id), None)
    return {'found': match is not None, 'course': match}


class LocalTrace:
    """Records application events, never claims to be an SDK-hosted trace."""
    def __init__(self, run_id: str | None = None):
        self.run_id = run_id or str(uuid.uuid4())
        self.events: list[dict] = []

    def emit(self, kind: str, *, parent: str | None = None, role: str = 'manager', **fields) -> str:
        # Explicit allowlist avoids logging arbitrary user messages, credentials or PII.
        allowed = {'course_id', 'request_id', 'operation', 'status', 'attempt', 'destination'}
        if set(fields) - allowed:
            raise ValueError('unapproved trace fields')
        if parent is not None and parent not in {x['span_id'] for x in self.events}:
            raise ValueError('parent span does not exist')
        span_id = f'span-{len(self.events) + 1}'
        self.events.append(dict(run_id=self.run_id, span_id=span_id, parent_span_id=parent,
                                kind=kind, role=role, **fields))
        return span_id


class SQLiteHistory:
    """Small app-owned store for comparison; real SDK SQLiteSession is in sdk_adapter.py."""
    def __init__(self, path: str | Path):
        self.path = path
        with sqlite3.connect(path) as db:
            db.execute('CREATE TABLE IF NOT EXISTS turns (id INTEGER PRIMARY KEY, session TEXT NOT NULL, role TEXT NOT NULL, content TEXT NOT NULL)')

    def add(self, session: str, role: str, content: str) -> None:
        if not session or role not in {'user', 'assistant'}:
            raise ValueError('valid session and role required')
        with sqlite3.connect(self.path) as db:
            db.execute('INSERT INTO turns(session,role,content) VALUES (?,?,?)', (session, role, content))

    def items(self, session: str) -> list[dict]:
        with sqlite3.connect(self.path) as db:
            rows = db.execute('SELECT role,content FROM turns WHERE session=? ORDER BY id', (session,)).fetchall()
        return [dict(role=role, content=content) for role, content in rows]

    def clear(self, session: str) -> None:
        with sqlite3.connect(self.path) as db:
            db.execute('DELETE FROM turns WHERE session=?', (session,))


async def catalogue_run(course_id: str, trace: LocalTrace | None = None) -> dict:
    trace = trace or LocalTrace()
    root = trace.emit('start', course_id=course_id)
    try:
        result = lookup_course(course_id)
        trace.emit('tool', parent=root, operation='lookup_course', status='ok')
    except ValueError:
        trace.emit('tool', parent=root, operation='lookup_course', status='invalid_input')
        trace.emit('terminal', parent=root, status='failed')
        raise
    trace.emit('terminal', parent=root, status='complete')
    return {'mode': 'deterministic-offline', 'final_output': result, 'last_agent': 'catalogue',
            'events': trace.events, 'usage': None}


async def offline_stream(course_id: str):
    """Synthetic typed event exercise, explicitly separate from real SDK streaming."""
    yield {'type': 'agent_updated_stream_event', 'agent': 'catalogue', 'synthetic': True}
    result = await catalogue_run(course_id)
    for chunk in json.dumps(result['final_output']).split(' '):
        yield {'type': 'raw_response_event', 'delta': chunk + ' ', 'synthetic': True}
    yield {'type': 'run_item_stream_event', 'status': 'complete', 'synthetic': True}


@dataclass(frozen=True)
class RequestContext:
    request_id: str
    product_id: str
    policy_version: str
    # No email/address/credentials are required by either specialist.

    def __post_init__(self):
        if not re.fullmatch(r'REQ-[0-9]{3}', self.request_id):
            raise ValueError('invalid request id')
        if self.product_id not in {'KB-01', 'MS-02'} or self.policy_version != '2026-11-demo':
            raise ValueError('unknown synthetic product or policy')


PERMISSIONS = {'research': {'inventory'}, 'policy': {'policy'}, 'shipping': {'shipping'},
               'manager': {'delegate'}}


def capability(role: str, operation: str, ctx: RequestContext) -> dict:
    if operation not in PERMISSIONS.get(role, set()):
        raise PermissionError(f'{role} cannot {operation}')
    if operation == 'inventory':
        return {'request_id': ctx.request_id, 'product_id': ctx.product_id,
                'stock': {'KB-01': 7, 'MS-02': 0}[ctx.product_id], 'source': 'synthetic-inventory'}
    if operation == 'policy':
        return {'request_id': ctx.request_id, 'policy_version': ctx.policy_version,
                'return_days': 30, 'source': 'synthetic-policy'}
    if operation == 'shipping':
        return {'request_id': ctx.request_id, 'delivery_days': 3, 'source': 'synthetic-shipping'}
    return {'request_id': ctx.request_id, 'operation': 'delegate'}


class TransientLookupError(Exception):
    pass


async def bounded_read(operation: Callable[[], Awaitable[dict]], *, attempts: int = 2,
                       timeout: float = 1.0) -> dict:
    """Retry only explicitly classified transient errors on read-only operations."""
    if attempts not in range(1, 4) or timeout <= 0:
        raise ValueError('attempts must be 1..3 and timeout positive')
    for attempt in range(attempts):
        try:
            return await asyncio.wait_for(operation(), timeout=timeout)
        except TransientLookupError:
            if attempt + 1 == attempts:
                raise
    raise AssertionError('unreachable')


async def specialists(ctx: RequestContext, *, trace: LocalTrace | None = None,
                      operations: dict[str, Callable[[], Awaitable[dict]]] | None = None) -> dict:
    trace = trace or LocalTrace()
    root = trace.emit('start', request_id=ctx.request_id)

    async def call(role, operation):
        span = trace.emit('delegation', parent=root, role=role, operation=operation)
        async def default():
            await asyncio.sleep(0)
            return capability(role, operation, ctx)
        try:
            value = await bounded_read((operations or {}).get(role, default))
            if value.get('request_id') != ctx.request_id:
                raise ValueError('cross-request result')
            if role == 'research' and (type(value.get('stock')) is not int or value.get('product_id') != ctx.product_id):
                raise ValueError('invalid inventory result')
            if role == 'policy' and (type(value.get('return_days')) is not int or value.get('policy_version') != ctx.policy_version):
                raise ValueError('invalid policy result')
            trace.emit('tool', parent=span, role=role, operation=operation, status='ok')
            return {'role': role, 'result': value, 'error': None}
        except (TransientLookupError, TimeoutError, ValueError) as error:
            trace.emit('tool', parent=span, role=role, operation=operation, status=type(error).__name__)
            return {'role': role, 'result': None, 'error': type(error).__name__}
    # gather preserves input order even if specialists finish in a different order.
    results = await asyncio.gather(call('research', 'inventory'), call('policy', 'policy'))
    missing = [x['role'] for x in results if x['error']]
    trace.emit('synthesis', parent=root, status='partial' if missing else 'complete')
    trace.emit('terminal', parent=root, status='partial' if missing else 'complete')
    return {'mode': 'deterministic-offline', 'owner': 'manager', 'results': results,
            'unresolved': missing, 'trace': trace.events}


async def handoff_shipping(ctx: RequestContext, trace: LocalTrace) -> dict:
    root = trace.emit('start', request_id=ctx.request_id, role='triage')
    trace.emit('handoff', parent=root, role='triage', destination='shipping')
    result = capability('shipping', 'shipping', ctx)
    trace.emit('tool', parent=root, role='shipping', operation='shipping', status='ok')
    trace.emit('terminal', parent=root, role='shipping', status='complete')
    return {'owner': 'shipping', 'result': result, 'trace': trace.events}


async def orchestration_comparison(ctx: RequestContext) -> dict:
    """Local comparison counts boundary invocations, never provider latency/tokens."""
    generalist = {'inventory': capability('research', 'inventory', ctx),
                  'policy': capability('policy', 'policy', ctx)}
    coordinated = await specialists(ctx)
    return {'single_application': generalist, 'coordinated': coordinated,
            'measurement': {'kind': 'local-event-count', 'specialist_calls': 2,
                            'provider_latency': None, 'tokens': None}}


def escalation_fallback(ctx: RequestContext, role: str, reason: str) -> dict:
    """An explicitly different recovery action, not a fabricated replacement fact.

    A failed specialist produces a draft escalation rather than an invented stock
    quantity, policy or delivery promise. Nothing is sent or externally queued.
    """
    if role not in {'research', 'policy'} or reason not in {
            'TransientLookupError', 'TimeoutError', 'ValueError'}:
        raise ValueError('unrecognized fallback attribution')
    return {'request_id': ctx.request_id, 'failed_role': role,
            'trigger': reason, 'action': 'draft_manual_review',
            'source': 'application-failure-policy-v1',
            'facts_recovered': False, 'sent': False,
            'requires_human_review': True}


async def specialists_with_fallback(ctx: RequestContext, *, operations=None) -> dict:
    result = await specialists(ctx, operations=operations)
    result['fallbacks'] = [escalation_fallback(ctx, row['role'], row['error'])
                           for row in result['results'] if row['error']]
    # Existing healthy facts and failed/unknown attribution are preserved unchanged.
    return result


async def connected_application_run(ctx: RequestContext) -> dict:
    """One connected local lineage, clearly NOT an SDK/model execution.

    The manager collects two specialist facts as tool results, transfers ownership
    to shipping, and that owner synthesizes all three attributed facts. This teaches
    the lineage contract separately from observing actual model routing.
    """
    trace = LocalTrace()
    root = trace.emit('start', request_id=ctx.request_id)
    facts = []
    for role, operation in [('research', 'inventory'), ('policy', 'policy')]:
        delegation = trace.emit('delegation', parent=root, role=role, operation=operation)
        value = capability(role, operation, ctx)
        trace.emit('tool', parent=delegation, role=role, operation=operation, status='ok')
        facts.append(value)
    transfer = trace.emit('handoff', parent=root, destination='shipping')
    delivery = capability('shipping', 'shipping', ctx)
    trace.emit('tool', parent=transfer, role='shipping', operation='shipping', status='ok')
    facts.append(delivery)
    trace.emit('synthesis', parent=transfer, role='shipping', status='complete')
    trace.emit('terminal', parent=root, role='shipping', status='complete')
    return {'mode': 'deterministic-application-lineage-not-sdk', 'owner': 'shipping',
            'request_id': ctx.request_id, 'facts': facts,
            'source_ids': [row['source'] for row in facts], 'trace': trace.events}


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--stage', choices=['6', '7'], default='6')
    args = parser.parse_args()
    result = asyncio.run(catalogue_run('ECA-101') if args.stage == '6' else
                         specialists(RequestContext('REQ-001', 'KB-01', '2026-11-demo')))
    print(json.dumps(result, indent=2))
