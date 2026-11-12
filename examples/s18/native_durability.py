"""Native LangGraph persistence labs; no model, network, or real deliveries.

SqliteSaver owns graph checkpoints. MockLedger is a SEPARATE local teaching
ledger, not a distributed transaction with LangGraph. It deduplicates completed
mock effects and refuses ambiguous outcomes. Replaying a checkpoint executes
nodes again; it does not undo external effects. Fixture reviewer labels below
are not authentication or evidence of a real human reviewing an action.

add_messages replaces only the message with the same ID. It does not erase
earlier assistant quotations, observations, or historical SQLite checkpoints.
Message correction is not a privacy-erasure mechanism; thread isolation is
demonstrated separately from retention and deletion policy.
"""
from __future__ import annotations

from contextlib import contextmanager
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
from typing import Annotated, Any, TypedDict

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.types import Command, interrupt
from langgraph.checkpoint.sqlite import SqliteSaver


class State(TypedDict, total=False):
    messages: Annotated[list[AnyMessage], add_messages]
    request: str
    response: str
    proposal: dict[str, str]
    decision: str
    approved_sha256: str
    run_id: str
    failure: str
    progress: str


def digest(value: Any) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def thread_config(thread: str) -> RunnableConfig:
    if type(thread) is not str or not thread.strip() or len(thread) > 120:
        raise ValueError('nonempty application-owned thread identity required')
    return {'configurable': {'thread_id': thread}}


def _thread(config: RunnableConfig) -> str:
    value = config.get('configurable', {}).get('thread_id')
    thread_config(value)
    return value


def _durable_path(path: str | Path) -> str:
    path = Path(path)
    if str(path) == ':memory:' or not path.parent.is_dir():
        raise ValueError('existing directory and durable SQLite filename required')
    return str(path)


def checked_proposal(value: Any) -> dict[str, str]:
    if (type(value) is not dict or set(value) != {'action_id', 'recipient', 'text'}
            or any(type(v) is not str or not v.strip() for v in value.values())
            or value['recipient'] != 'academy-fixture'
            or len(value['action_id']) > 120 or len(value['text']) > 4000):
        raise ValueError('bounded local mock proposal required')
    return dict(value)


class UncertainOutcome(RuntimeError):
    """Requires reconciliation; never automatically repeats the mock dispatch."""


class TerminalValidation(ValueError):
    """An unchanged invalid run stays terminal rather than using transient retry."""


class MockLedger:
    """Append-only observations plus idempotent, transaction-local mock effects.

    No external tool is dispatched. A crash in the simulated external boundary
    leaves an uncertain row, so restarting cannot silently repeat the action.
    SQLite's local transaction guarantee is not a claim of remote exactly-once.
    """
    def __init__(self, path: str | Path):
        self.path = _durable_path(path)
        with self.connect() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS observations(
                  sequence INTEGER PRIMARY KEY, thread TEXT NOT NULL,
                  node TEXT NOT NULL, detail TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS effects(
                  thread TEXT NOT NULL, action_id TEXT NOT NULL,
                  payload_sha TEXT NOT NULL, payload TEXT NOT NULL,
                  status TEXT NOT NULL CHECK(status IN ('done','uncertain')),
                  PRIMARY KEY(thread,action_id));
                CREATE TABLE IF NOT EXISTS failures(
                  thread TEXT NOT NULL, run_id TEXT NOT NULL, kind TEXT NOT NULL,
                  PRIMARY KEY(thread,run_id));
            ''')

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=5)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    def observe(self, thread: str, node: str, detail: Any) -> None:
        with self.connect() as db:
            db.execute('INSERT INTO observations(thread,node,detail) VALUES(?,?,?)',
                       (thread, node, json.dumps(detail, sort_keys=True)))

    def observations(self, thread: str) -> list[dict]:
        with self.connect() as db:
            return [dict(r) for r in db.execute(
                'SELECT * FROM observations WHERE thread=? ORDER BY sequence', (thread,))]

    def effects(self, thread: str) -> list[dict]:
        with self.connect() as db:
            return [dict(r) for r in db.execute(
                'SELECT * FROM effects WHERE thread=? ORDER BY action_id', (thread,))]

    def effect(self, thread: str, proposal: dict, *, ambiguous: bool = False) -> str:
        proposal = checked_proposal(proposal)
        encoded = json.dumps(proposal, sort_keys=True)
        uncertain = False
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute('SELECT * FROM effects WHERE thread=? AND action_id=?',
                             (thread, proposal['action_id'])).fetchone()
            if row:
                if row['payload_sha'] != digest(proposal):
                    raise ValueError('idempotency key already binds a different payload')
                if row['status'] == 'uncertain':
                    raise UncertainOutcome('reconcile original outcome; replay prohibited')
                return 'deduplicated'
            db.execute('INSERT INTO effects VALUES(?,?,?,?,?)',
                       (thread, proposal['action_id'], digest(proposal), encoded,
                        'uncertain' if ambiguous else 'done'))
            uncertain = ambiguous
        # Deliberately AFTER commit: uncertain evidence survives node failure.
        if uncertain:
            raise UncertainOutcome('simulated response loss: reconcile; do not redispatch')
        return 'delivered'

    def fail_once(self, thread: str, run_id: str) -> None:
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            changed = db.execute('INSERT OR IGNORE INTO failures VALUES(?,?,?)',
                                 (thread, run_id, 'transient-once')).rowcount
        if changed:
            raise InterruptedError('fixture transient failure after completed first step')

    def terminal(self, thread: str, run_id: str) -> None:
        with self.connect() as db:
            db.execute('INSERT OR IGNORE INTO failures VALUES(?,?,?)',
                       (thread, run_id, 'terminal-validation'))
        raise TerminalValidation('invalid fixture input is terminal; repair the input explicitly')


def build_graph(saver: SqliteSaver, ledger: MockLedger, *, mode: str = 'conversation'):
    builder = StateGraph(State)
    if mode == 'conversation':
        def prepare(state: State, config: RunnableConfig):
            thread = _thread(config)
            messages = state.get('messages', [])
            if not messages or not isinstance(messages[-1], HumanMessage):
                raise ValueError('a user message must end this turn')
            request = messages[-1].content
            if type(request) is not str or not request.strip():
                raise ValueError('text-only fixture request required')
            ledger.observe(thread, 'prepare', {'request': request})
            return {'request': request}

        def respond(state: State, config: RunnableConfig):
            thread = _thread(config)
            # Deterministic teaching responder; not a model or provider result.
            humans = [m.content for m in state['messages'] if isinstance(m, HumanMessage)]
            response = f"Fixture response: {state['request']} | user turns: {len(humans)}"
            ledger.observe(thread, 'respond', {'request': state['request'], 'response': response})
            return {'response': response,
                    'messages': [AIMessage(content=response,
                                           id='reply-' + digest([thread, state['request'], humans]))]}

        builder.add_node('prepare', prepare)
        builder.add_node('respond', respond)
        builder.add_edge(START, 'prepare')
        builder.add_edge('prepare', 'respond')
        builder.add_edge('respond', END)
    elif mode == 'review':
        def review(state: State, config: RunnableConfig):
            _thread(config)
            proposal = checked_proposal(state['proposal'])
            proposal_sha = digest(proposal)
            decision = interrupt({'proposal': proposal, 'proposal_sha256': proposal_sha,
                                  'question': 'Fixture review: approve, edit, or reject?'})
            if (type(decision) is not dict
                    or decision.get('reviewer') != 'academy-fixture-reviewer'
                    or decision.get('proposal_sha256') != proposal_sha
                    or decision.get('decision') not in {'approve', 'edit', 'reject'}):
                raise ValueError('exact current proposal and application fixture reviewer required')
            kind = decision['decision']
            allowed_keys = {'reviewer', 'proposal_sha256', 'decision'} | ({'edited'} if kind == 'edit' else set())
            if set(decision) != allowed_keys:
                raise ValueError('unexpected decision fields')
            if kind == 'edit':
                edited = checked_proposal(decision['edited'])
                if edited == proposal or edited['action_id'] == proposal['action_id']:
                    raise ValueError('edit requires changed payload and new action identity')
                # Empty approval invalidates all former approval; next node is review AGAIN.
                return {'proposal': edited, 'decision': 'edited', 'approved_sha256': ''}
            return {'decision': kind, 'approved_sha256': proposal_sha if kind == 'approve' else ''}

        def dispatch(state: State, config: RunnableConfig):
            proposal = checked_proposal(state['proposal'])
            if state.get('decision') != 'approve' or state.get('approved_sha256') != digest(proposal):
                raise ValueError('dispatch requires exact current approval')
            status = ledger.effect(_thread(config), proposal)
            return {'progress': status}

        builder.add_node('review', review)
        builder.add_node('dispatch', dispatch)
        builder.add_edge(START, 'review')
        builder.add_conditional_edges('review',
            lambda s: 'review' if s['decision'] == 'edited' else
            ('dispatch' if s['decision'] == 'approve' else END),
            {'review': 'review', 'dispatch': 'dispatch', END: END})
        builder.add_edge('dispatch', END)
    elif mode == 'recovery':
        def validate(state: State, config: RunnableConfig):
            thread = _thread(config)
            run_id = state.get('run_id')
            if type(run_id) is not str or not run_id.strip() or len(run_id) > 100:
                raise ValueError('bounded explicit run_id required')
            failure = state.get('failure', 'none')
            if failure not in {'none', 'once', 'unknown', 'validation'}:
                raise ValueError('unknown fixture failure type')
            if failure == 'validation':
                ledger.terminal(thread, run_id)
            ledger.observe(thread, 'validate', {'run_id': run_id})
            return {'progress': 'validated'}

        def first(state: State, config: RunnableConfig):
            thread = _thread(config)
            proposal = {'action_id': state['run_id'] + '-first', 'recipient': 'academy-fixture',
                        'text': 'completed first local step'}
            status = ledger.effect(thread, proposal)
            ledger.observe(thread, 'first', {'effect': status})
            return {'progress': 'first-done'}

        def second(state: State, config: RunnableConfig):
            thread = _thread(config)
            ledger.observe(thread, 'second-enter', {'run_id': state['run_id']})
            if state.get('failure') == 'once':
                ledger.fail_once(thread, state['run_id'])
            proposal = {'action_id': state['run_id'] + '-second', 'recipient': 'academy-fixture',
                        'text': 'completed second local step'}
            status = ledger.effect(thread, proposal, ambiguous=state.get('failure') == 'unknown')
            return {'progress': 'complete:' + status}

        builder.add_node('validate', validate)
        builder.add_node('first', first)
        builder.add_node('second', second)
        builder.add_edge(START, 'validate')
        builder.add_edge('validate', 'first')
        builder.add_edge('first', 'second')
        builder.add_edge('second', END)
    else:
        raise ValueError('unknown native graph mode')
    return builder.compile(checkpointer=saver)


@contextmanager
def sqlite_graph(database: str | Path, ledger: str | Path, *, mode: str = 'conversation'):
    database, ledger = _durable_path(database), _durable_path(ledger)
    if Path(database).resolve() == Path(ledger).resolve():
        raise ValueError('separate checkpoint and effect ledger files required')
    with SqliteSaver.from_conn_string(database) as saver:
        yield build_graph(saver, MockLedger(ledger), mode=mode)


def _main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('database')
    parser.add_argument('ledger')
    parser.add_argument('thread')
    parser.add_argument('--mode', choices=['conversation', 'review', 'recovery'], default='conversation')
    parser.add_argument('--message')
    parser.add_argument('--message-id')
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--run-id')
    parser.add_argument('--failure', choices=['none', 'once', 'unknown', 'validation'], default='none')
    parser.add_argument('--proposal-json')
    parser.add_argument('--decision-json')
    args = parser.parse_args()
    config = thread_config(args.thread)
    if args.mode == 'conversation':
        if args.resume or not args.message:
            parser.error('conversation requires --message (history is restored automatically)')
        data = {'messages': [HumanMessage(content=args.message, id=args.message_id)]}
    elif args.mode == 'review':
        if args.resume:
            if not args.decision_json:
                parser.error('review --resume requires --decision-json')
            data = Command(resume=json.loads(args.decision_json))
        else:
            if not args.proposal_json:
                parser.error('review requires --proposal-json')
            data = {'proposal': checked_proposal(json.loads(args.proposal_json))}
    else:
        data = None if args.resume else {'run_id': args.run_id, 'failure': args.failure}
    with sqlite_graph(args.database, args.ledger, mode=args.mode) as graph:
        result = graph.invoke(data, config)
        snapshot = graph.get_state(config)
        output = {'checkpoint_id': snapshot.config['configurable']['checkpoint_id'],
                  'next': list(snapshot.next),
                  'messages': [m.model_dump() for m in result.get('messages', [])],
                  'response': result.get('response'), 'progress': result.get('progress'),
                  'interrupts': [item.value for item in result.get('__interrupt__', [])],
                  'effects': MockLedger(args.ledger).effects(args.thread)}
        print(json.dumps(output, sort_keys=True))


if __name__ == '__main__':
    _main()
