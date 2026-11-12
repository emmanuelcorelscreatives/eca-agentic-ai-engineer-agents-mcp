"""SQLite teaching implementation; not a substitute for the actual LangGraph saver lab.
All actions are local mock deliveries. Checkpoints are immutable; replay/fork have explicit lineage.
"""
from __future__ import annotations
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import sqlite3
from uuid import uuid4


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


class Sessions:
    def __init__(self, database):
        self.database = str(database)
        if self.database == ':memory:' or not Path(self.database).parent.is_dir():
            raise ValueError('existing parent and durable SQLite path required')
        with self.connect() as db:
            db.executescript('''
              CREATE TABLE IF NOT EXISTS checkpoints(
                id TEXT PRIMARY KEY, thread TEXT NOT NULL, parent TEXT,
                kind TEXT NOT NULL, state TEXT NOT NULL);
              CREATE TABLE IF NOT EXISTS heads(thread TEXT PRIMARY KEY, checkpoint TEXT NOT NULL);
              CREATE TABLE IF NOT EXISTS deliveries(action_id TEXT PRIMARY KEY, payload TEXT NOT NULL,
                payload_sha TEXT NOT NULL, reviewer TEXT NOT NULL, decision TEXT NOT NULL);
            ''')

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.database, isolation_level=None, timeout=5)
        db.row_factory = sqlite3.Row
        try:
            db.execute('BEGIN IMMEDIATE')
            yield db
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()

    @staticmethod
    def _load(db, thread, checkpoint=None):
        if type(thread) is not str or not thread.strip():
            raise ValueError('application-owned thread required')
        if checkpoint:
            row = db.execute('SELECT * FROM checkpoints WHERE id=? AND thread=?', (checkpoint, thread)).fetchone()
        else:
            row = db.execute('SELECT c.* FROM checkpoints c JOIN heads h ON h.checkpoint=c.id WHERE h.thread=?', (thread,)).fetchone()
        if not row:
            if checkpoint:
                raise ValueError('unknown checkpoint in this thread')
            return None, {'messages': [], 'action': None, 'status': 'ready'}
        return row['id'], json.loads(row['state'])

    @staticmethod
    def _save(db, thread, parent, kind, state):
        checkpoint = str(uuid4())
        db.execute('INSERT INTO checkpoints VALUES(?,?,?,?,?)', (checkpoint, thread, parent, kind, json.dumps(state, sort_keys=True)))
        db.execute('INSERT INTO heads VALUES(?,?) ON CONFLICT(thread) DO UPDATE SET checkpoint=excluded.checkpoint', (thread, checkpoint))
        return checkpoint

    def load(self, thread, checkpoint=None):
        with self.connect() as db:
            key, state = self._load(db, thread, checkpoint)
            return {'checkpoint': key, 'state': state}

    def turn(self, thread, message, *, replace=False):
        if type(message) is not str or not message:
            raise ValueError('nonempty message required')
        with self.connect() as db:
            parent, state = self._load(db, thread)
            state['messages'] = [message] if replace else [*state['messages'], message]
            return self._save(db, thread, parent, 'replace-history' if replace else 'turn', state)

    def fork(self, thread, checkpoint, new_thread, *, message=None, replay=False):
        if thread == new_thread or not new_thread:
            raise ValueError('new thread required')
        with self.connect() as db:
            if db.execute('SELECT 1 FROM heads WHERE thread=?', (new_thread,)).fetchone():
                raise ValueError('fork target exists')
            parent, state = self._load(db, thread, checkpoint)
            if message is not None:
                if replay or type(message) is not str:
                    raise ValueError('replay must preserve state; fork edit must be text')
                state['messages'] = [*state['messages'], message]
            state['lineage'] = {'source_thread': thread, 'source_checkpoint': checkpoint, 'operation': 'replay' if replay else 'fork'}
            return self._save(db, new_thread, parent, state['lineage']['operation'], state)

    def propose(self, thread, payload):
        if type(payload) is not dict or set(payload) != {'recipient', 'text'} or any(type(v) is not str or not v for v in payload.values()):
            raise ValueError('strict mock action schema')
        if payload['recipient'] != 'academy-fixture':
            raise ValueError('only local mock recipient allowed')
        with self.connect() as db:
            parent, state = self._load(db, thread)
            if state['status'] == 'awaiting-review':
                raise ValueError('pending action cannot be overwritten')
            state.update(status='awaiting-review', action={'id': str(uuid4()), 'payload': payload, 'sha256': digest(payload)})
            return self._save(db, thread, parent, 'interrupt-before-action', state)

    def decide(self, thread, *, checkpoint, payload_sha, reviewer, decision, edited=None, fail_before_commit=False):
        if reviewer not in {'academy-human-reviewer'} or decision not in {'approve', 'edit', 'reject'}:
            raise ValueError('authorized application reviewer and exact decision required')
        with self.connect() as db:
            parent, state = self._load(db, thread)
            action = state.get('action')
            if parent != checkpoint or state['status'] != 'awaiting-review' or not action or action['sha256'] != payload_sha:
                raise ValueError('stale approval or payload')
            payload = action['payload']
            if decision == 'edit':
                if type(edited) is not dict or set(edited) != {'recipient', 'text'} or edited['recipient'] != 'academy-fixture' or type(edited['text']) is not str or not edited['text']:
                    raise ValueError('invalid edited payload')
                payload = edited
            elif edited is not None:
                raise ValueError('edits require edit decision')
            if decision != 'reject':
                existing = db.execute('SELECT payload_sha FROM deliveries WHERE action_id=?', (action['id'],)).fetchone()
                if existing and existing['payload_sha'] != digest(payload):
                    raise ValueError('conflicting repeated action')
                db.execute('INSERT OR IGNORE INTO deliveries VALUES(?,?,?,?,?)', (action['id'], json.dumps(payload, sort_keys=True), digest(payload), reviewer, decision))
            state.update(status='rejected' if decision == 'reject' else 'delivered', decision=decision, reviewer=reviewer)
            key = self._save(db, thread, parent, 'human-decision', state)
            if fail_before_commit:
                raise InterruptedError('synthetic interruption; transaction rolls back')
            return key

    def deliveries(self):
        with self.connect() as db:
            return [dict(row) for row in db.execute('SELECT * FROM deliveries ORDER BY action_id')]


def build_persistent_langgraph(saver):
    """Genuine LangGraph state, interrupt and Command-compatible graph. No network tools."""
    from typing import TypedDict
    from langgraph.graph import StateGraph, START, END
    from langgraph.types import interrupt

    class State(TypedDict, total=False):
        payload: dict
        decision: str

    def review(state):
        decision = interrupt({'payload': state['payload'], 'question': 'Approve or reject mock action?'})
        if decision not in {'approve', 'reject'}:
            raise ValueError('explicit application decision required')
        return {'decision': decision}

    builder = StateGraph(State)
    builder.add_node('review', review)
    builder.add_edge(START, 'review')
    builder.add_edge('review', END)
    return builder.compile(checkpointer=saver)


@contextmanager
def actual_langgraph_sqlite(path):
    from langgraph.checkpoint.sqlite import SqliteSaver
    with SqliteSaver.from_conn_string(str(path)) as saver:
        yield build_persistent_langgraph(saver)


@contextmanager
def actual_langgraph_postgres(connection_string):
    """Caller supplies a dedicated course database. setup performs actual schema setup."""
    from langgraph.checkpoint.postgres import PostgresSaver
    with PostgresSaver.from_conn_string(connection_string) as saver:
        saver.setup()
        yield build_persistent_langgraph(saver)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('database')
    parser.add_argument('thread')
    parser.add_argument('--message')
    args = parser.parse_args()
    sessions = Sessions(args.database)
    if args.message:
        sessions.turn(args.thread, args.message)
    print(json.dumps(sessions.load(args.thread), indent=2))
