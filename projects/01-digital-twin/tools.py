"""Typed lead/question tools with atomic SQLite dedupe and durable outbox.

Calls are idempotent across service restarts. The same ID with changed arguments
is rejected. run() isolates bad calls in order, capped at eight per agent turn.
Notification dispatch is separate from lead storage: a delivery failure cannot
create a second contact. The adapter sees only a local record ID, never contact
personal data. This is not an exactly-once remote-delivery claim.
"""
from dataclasses import asdict, dataclass
import hashlib
import json
import re
from collections.abc import Mapping
from typing import Any

from storage import SQLiteStore
from notifications import LOCAL_DRY_RUN, NotificationAdapter


def _text(value, label, maximum, *, empty=False):
    if not isinstance(value, str) or len(value) > maximum or (not empty and not value.strip()):
        raise ValueError(f'{label} must be text of 1..{maximum} characters' if not empty else f'{label} must be text up to {maximum} characters')
    return value.strip()


@dataclass(frozen=True)
class Lead:
    name: str
    email: str
    message: str
    consent: bool
    opportunity: str = ''

    def __post_init__(self):
        if self.consent is not True:
            raise PermissionError('explicit lead-storage consent is required')
        for name, limit in [('name', 200), ('email', 254), ('message', 2000), ('opportunity', 1000)]:
            object.__setattr__(self, name, _text(getattr(self, name), name, limit, empty=name == 'opportunity'))
        if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', self.email):
            raise ValueError('valid email required')


@dataclass(frozen=True)
class Question:
    question: str
    consent: bool

    def __post_init__(self):
        if self.consent is not True:
            raise PermissionError('explicit question-storage consent is required')
        object.__setattr__(self, 'question', _text(self.question, 'question', 4000))


@dataclass(frozen=True)
class ToolCall:
    name: str
    args: Mapping[str, Any]
    call_id: str

    def __post_init__(self):
        _text(self.name, 'tool name', 80)
        _call_id(self.call_id)
        if not isinstance(self.args, Mapping) or any(not isinstance(key, str) for key in self.args):
            raise ValueError('tool arguments must be an object with string keys')
        if 'call_id' in self.args:
            raise ValueError('call_id belongs on the tool call, not in its arguments')


def _call_id(value):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}', value):
        raise ValueError('call_id must be a stable 1..128 character identifier')
    return value


def _encode(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


class ToolsService:
    MAX_CALLS_PER_TURN = 8

    def __init__(self, database=':memory:'):
        self.store = SQLiteStore(database)

    def _record(self, call_id, tool, value):
        _call_id(call_id)
        arguments = asdict(value)
        fingerprint = hashlib.sha256(_encode({'tool': tool, 'arguments': arguments}).encode()).hexdigest()
        with self.store.transaction() as db:
            old = db.execute('SELECT fingerprint,result FROM twin_calls WHERE call_id=?', (call_id,)).fetchone()
            if old:
                if old['fingerprint'] != fingerprint:
                    raise ValueError('call_id already used with different arguments or tool')
                return json.loads(old['result'])
            now = self.store.clock()
            if tool == 'record_lead':
                cursor = db.execute('INSERT INTO twin_leads(name,email,message,consent,opportunity,created_at) VALUES(?,?,?,1,?,?)',
                                    (value.name, value.email, value.message, value.opportunity, now))
                record_id = cursor.lastrowid
                result = {'lead_id': record_id, 'contact_id': record_id}
                payload = {'kind': 'lead_received', 'lead_id': record_id}
            else:
                cursor = db.execute('INSERT INTO twin_questions(question,consent,created_at) VALUES(?,1,?)', (value.question, now))
                record_id = cursor.lastrowid
                result = {'question_id': record_id}
                payload = {'kind': 'question_received', 'question_id': record_id}
            # The provisional row and final receipt are in the same transaction.
            db.execute('INSERT INTO twin_calls(call_id,tool,fingerprint,result,created_at) VALUES(?,?,?,?,?)',
                       (call_id, tool, fingerprint, '{}', now))
            outbox_id = db.execute('INSERT INTO twin_outbox(call_id,payload,created_at,updated_at) VALUES(?,?,?,?)',
                                   (call_id, _encode(payload), now, now)).lastrowid
            result.update(outbox_id=outbox_id, status='stored_locally', notification='pending')
            db.execute('UPDATE twin_calls SET result=? WHERE call_id=?', (_encode(result), call_id))
            return result

    def record_lead(self, call_id, name, email, message, consent, opportunity=''):
        return self._record(call_id, 'record_lead', Lead(name, email, message, consent, opportunity))

    def capture_question(self, call_id, question, consent):
        return self._record(call_id, 'capture_question', Question(question, consent))

    def run(self, calls):
        if not isinstance(calls, (list, tuple)) or len(calls) > self.MAX_CALLS_PER_TURN:
            raise ValueError('a turn must contain at most eight tool calls')
        registry = {'record_lead': self.record_lead, 'record_contact': self.record_lead,
                    'capture_question': self.capture_question}
        results = []
        for raw in calls:
            call_id = raw.call_id if isinstance(raw, ToolCall) else raw.get('call_id') if isinstance(raw, Mapping) else None
            try:
                if isinstance(raw, ToolCall):
                    call = raw
                elif isinstance(raw, Mapping):
                    if set(raw) - {'name', 'args', 'arguments', 'call_id'} or ('args' in raw and 'arguments' in raw):
                        raise ValueError('tool call has unknown or conflicting fields')
                    call = ToolCall(raw.get('name'), raw.get('args', raw.get('arguments', {})), raw.get('call_id'))
                else:
                    raise ValueError('tool call must be a typed call or object')
                if call.name not in registry:
                    raise ValueError('unknown tool')
                result = registry[call.name](call.call_id, **dict(call.args))
                results.append({'call_id': call.call_id, 'status': 'ok', 'result': result})
            except (TypeError, ValueError, PermissionError) as error:
                results.append({'call_id': call_id, 'status': 'rejected', 'error': str(error)})
        return results

    def pending_outbox(self):
        return self.store.pending_outbox()

    def dispatch_once(self, outbox_id=None, *, adapter=None, allow_external=False, retry_local=False):
        adapter = LOCAL_DRY_RUN if adapter is None else adapter
        if not isinstance(adapter, NotificationAdapter):
            raise TypeError('wrap a configured callable in NotificationAdapter')
        if adapter.external and allow_external is not True:
            raise PermissionError('external delivery requires explicit per-dispatch permission')
        if self.store._depth:
            raise RuntimeError('notification dispatch cannot run within a caller transaction')
        with self.store.transaction() as db:
            if outbox_id is None:
                row = db.execute("SELECT * FROM twin_outbox WHERE status='pending' ORDER BY id LIMIT 1").fetchone()
            else:
                row = db.execute('SELECT * FROM twin_outbox WHERE id=?', (outbox_id,)).fetchone()
            if row is None:
                return {'status': 'nothing_pending'}
            if row['status'] != 'pending':
                if not (row['status'] == 'local_failed' and not row['external'] and not adapter.external and retry_local is True):
                    return {'outbox_id': row['id'], 'status': row['status'], 'dispatched': False}
            # A crash after this commit is UNKNOWN. A later process must not
            # turn dispatching into pending and replay an external operation.
            db.execute("UPDATE twin_outbox SET status='dispatching',adapter=?,external=?,attempts=attempts+1,updated_at=? WHERE id=?",
                       (adapter.name, int(adapter.external), self.store.clock(), row['id']))
            payload = json.loads(row['payload'])
            selected_id = row['id']
        try:
            receipt = adapter.send(payload)
            if not isinstance(receipt, Mapping):
                raise ValueError('notification adapter must return a structured receipt')
            encoded = _encode(dict(receipt))
            # Only an explicit provider delivery receipt may claim delivery.
            if adapter.external:
                if receipt.get('status') != 'delivered' or not receipt.get('receipt_id'):
                    raise ValueError('external delivery requires delivered status and receipt_id')
                status = 'delivered'
            else:
                # Local execution never claims that a remote owner was notified.
                status = 'dry_run'
        except Exception as error:
            status = 'unknown' if adapter.external else 'local_failed'
            with self.store.transaction() as db:
                db.execute('UPDATE twin_outbox SET status=?,error=?,updated_at=? WHERE id=?',
                           (status, type(error).__name__, self.store.clock(), selected_id))
            return {'outbox_id': selected_id, 'status': status, 'delivery': 'not_confirmed'}
        with self.store.transaction() as db:
            db.execute('UPDATE twin_outbox SET status=?,receipt=?,error=NULL,updated_at=? WHERE id=?',
                       (status, encoded, self.store.clock(), selected_id))
        return {'outbox_id': selected_id, 'status': status, 'receipt': dict(receipt)}

    def purge_retention(self, before_timestamp):
        return self.store.purge_retention(before_timestamp)

    def close(self):
        self.store.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


# JSON-compatible definitions for adapters that register function tools. The
# runtime dataclasses remain authoritative even when a model ignores a schema.
TOOL_SCHEMAS = {
    'record_lead': {
        'type': 'object', 'additionalProperties': False,
        'properties': {
            'name': {'type': 'string', 'minLength': 1, 'maxLength': 200},
            'email': {'type': 'string', 'format': 'email', 'maxLength': 254},
            'message': {'type': 'string', 'minLength': 1, 'maxLength': 2000},
            'consent': {'type': 'boolean', 'const': True},
            'opportunity': {'type': 'string', 'maxLength': 1000},
        },
        'required': ['name', 'email', 'message', 'consent'],
    },
    'capture_question': {
        'type': 'object', 'additionalProperties': False,
        'properties': {
            'question': {'type': 'string', 'minLength': 1, 'maxLength': 4000},
            'consent': {'type': 'boolean', 'const': True},
        },
        'required': ['question', 'consent'],
    },
}
