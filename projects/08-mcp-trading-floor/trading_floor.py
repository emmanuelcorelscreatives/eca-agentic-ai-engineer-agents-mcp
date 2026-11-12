"""Deterministic synthetic paper market; never connects to a broker or network."""
from __future__ import annotations
import argparse
from dataclasses import asdict, dataclass
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import sqlite3
import time
import uuid
from datetime import datetime, timezone

FIXTURES = Path(__file__).parent / 'fixtures' / 'market.json'


def amount(value: str) -> Decimal:
    try:
        result = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError('invalid decimal') from exc
    if not result.is_finite() or result <= 0:
        raise ValueError('amount must be finite and positive')
    return result


@dataclass(frozen=True)
class Proposal:
    symbol: str
    side: str
    quantity: int
    price: str
    evidence_id: str

    def digest(self) -> str:
        return hashlib.sha256(json.dumps(asdict(self), sort_keys=True).encode()).hexdigest()


class TradingFloor:
    def __init__(self, database: str = ':memory:', fixtures: Path = FIXTURES, *, clock=time.time):
        self.clock = clock
        self.market = json.loads(Path(fixtures).read_text())
        self.db = sqlite3.connect(database, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS account (id INTEGER PRIMARY KEY CHECK(id=1), cash TEXT NOT NULL);
        INSERT OR IGNORE INTO account VALUES (1, '10000.00');
        CREATE TABLE IF NOT EXISTS positions(symbol TEXT PRIMARY KEY, quantity INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS approvals(digest TEXT PRIMARY KEY, reviewer TEXT NOT NULL, used INTEGER NOT NULL DEFAULT 0);
        CREATE TABLE IF NOT EXISTS orders(request_id TEXT PRIMARY KEY, digest TEXT NOT NULL, result TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS memory(id INTEGER PRIMARY KEY, kind TEXT NOT NULL, payload TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS traces(id INTEGER PRIMARY KEY, event TEXT NOT NULL, payload TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS account_meta(id INTEGER PRIMARY KEY CHECK(id=1), account_id TEXT NOT NULL, revision INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS proposals(digest TEXT PRIMARY KEY, payload TEXT NOT NULL, status TEXT NOT NULL, created_at REAL NOT NULL);
        ''')
        self.db.execute('INSERT OR IGNORE INTO account_meta VALUES (1,?,0)', (uuid.uuid4().hex,))
        columns = {row['name'] for row in self.db.execute('PRAGMA table_info(approvals)')}
        for name, sql_type in [('account_id','TEXT'), ('revision','INTEGER'), ('expires_at','REAL')]:
            if name not in columns:
                try: self.db.execute(f'ALTER TABLE approvals ADD COLUMN {name} {sql_type}')
                except sqlite3.OperationalError as exc:
                    if 'duplicate column name' not in str(exc): raise

    def close(self):
        self.db.close()

    def trace(self, event: str, payload: dict):
        self.db.execute('INSERT INTO traces(event,payload) VALUES (?,?)', (event, json.dumps(payload, sort_keys=True)))

    def research(self, symbol: str) -> dict:
        record = self.market['companies'].get(symbol)
        if record is None:
            raise ValueError('unknown synthetic symbol')
        result = {'symbol': symbol, **record, 'synthetic': True, 'as_of': self.market['as_of']}
        self.db.execute('INSERT INTO memory(kind,payload) VALUES (?,?)', ('research', json.dumps(result)))
        self.trace('research', {'symbol': symbol, 'evidence_id': record['evidence_id']})
        return result

    def propose(self, symbol: str, quantity: int, side: str = 'BUY') -> Proposal:
        research = self.research(symbol)
        proposal = Proposal(symbol, side, quantity, research['price'], research['evidence_id'])
        self._validate(proposal)
        self.trace('proposal', {'digest': proposal.digest(), **asdict(proposal)})
        self.db.execute('INSERT OR IGNORE INTO proposals VALUES (?,?,?,?)',
                        (proposal.digest(), json.dumps(asdict(proposal)), 'PROPOSED', self.clock()))
        return proposal

    def _validate(self, proposal: Proposal):
        if type(proposal.quantity) is not int or proposal.quantity <= 0:
            raise ValueError('quantity must be a positive integer')
        if proposal.side not in ('BUY', 'SELL'):
            raise ValueError('unsupported side')
        current = self.market['companies'].get(proposal.symbol)
        if current is None or proposal.price != current['price'] or proposal.evidence_id != current['evidence_id']:
            raise ValueError('proposal does not match current fixture quote/evidence')
        amount(proposal.price)

    def state(self) -> dict:
        cash = Decimal(self.db.execute('SELECT cash FROM account WHERE id=1').fetchone()['cash'])
        positions = {r['symbol']: r['quantity'] for r in self.db.execute('SELECT * FROM positions')}
        value = cash + sum((Decimal(self.market['companies'][s]['price']) * q for s, q in positions.items()), Decimal(0))
        meta = self.db.execute('SELECT * FROM account_meta WHERE id=1').fetchone()
        return {'cash': str(cash), 'positions': positions, 'equity': str(value), 'synthetic': True,
                'account_id': meta['account_id'], 'revision': meta['revision'],
                'valuation_as_of': self.market['as_of'], 'quote_mode': 'fixed historical synthetic snapshot'}

    def risk(self, proposal: Proposal, *, reference_time: datetime | None = None, max_quote_age_seconds: int = 300) -> dict:
        self._validate(proposal)
        state = self.state()
        cost = amount(proposal.price) * proposal.quantity
        existing = state['positions'].get(proposal.symbol, 0)
        reasons = []
        if reference_time is not None:
            if reference_time.tzinfo is None: raise ValueError('reference time must include timezone')
            quote_time = datetime.fromisoformat(self.market['as_of'].replace('Z', '+00:00'))
            age = (reference_time - quote_time).total_seconds()
            if age < 0 or age > max_quote_age_seconds: reasons.append('stale_or_future_quote')
        if proposal.side == 'BUY':
            if cost > Decimal(state['cash']): reasons.append('insufficient_cash')
            if cost > Decimal('2000.00'): reasons.append('order_limit')
            if Decimal(proposal.price) * (existing + proposal.quantity) > Decimal(state['equity']) * Decimal('0.25'):
                reasons.append('position_limit')
        elif proposal.quantity > existing:
            reasons.append('short_sales_disabled')
        return {'allowed': not reasons, 'reasons': reasons, 'notional': str(cost), 'digest': proposal.digest(),
                'account_id': state['account_id'], 'account_revision': state['revision'],
                'quote_as_of': self.market['as_of'], 'quote_mode': 'freshness checked' if reference_time else 'historical fixture replay'}

    def approve(self, proposal: Proposal, reviewer: str, *, ttl_seconds: int = 900) -> dict:
        """Human entry point: transport must authenticate a reviewer before calling."""
        if not reviewer.strip(): raise ValueError('reviewer is required')
        if type(ttl_seconds) is not int or ttl_seconds <= 0: raise ValueError('positive approval lifetime required')
        decision = self.risk(proposal)
        if not decision['allowed']: raise ValueError('risk rejected: ' + ','.join(decision['reasons']))
        self.db.execute('''INSERT INTO approvals(digest,reviewer,used,account_id,revision,expires_at)
          VALUES (?,?,0,?,?,?) ON CONFLICT(digest) DO UPDATE SET reviewer=excluded.reviewer,
          used=0,account_id=excluded.account_id,revision=excluded.revision,expires_at=excluded.expires_at''',
          (proposal.digest(), reviewer, decision['account_id'], decision['account_revision'], self.clock()+ttl_seconds))
        self.db.execute('UPDATE proposals SET status=? WHERE digest=?', ('APPROVED', proposal.digest()))
        self.trace('human_approval', {'digest': proposal.digest(), 'reviewer': reviewer,
                                    'account_id': decision['account_id'], 'revision': decision['account_revision']})
        return decision

    def execute(self, proposal: Proposal, request_id: str) -> dict:
        if not request_id.strip(): raise ValueError('request_id is required')
        self.db.execute('BEGIN IMMEDIATE')
        try:
            prior = self.db.execute('SELECT * FROM orders WHERE request_id=?', (request_id,)).fetchone()
            if prior:
                if prior['digest'] != proposal.digest(): raise ValueError('idempotency key reused for different order')
                self.db.execute('COMMIT')
                return json.loads(prior['result'])
            decision = self.risk(proposal)
            if not decision['allowed']: raise ValueError('risk rejected: ' + ','.join(decision['reasons']))
            approval = self.db.execute('SELECT * FROM approvals WHERE digest=?', (proposal.digest(),)).fetchone()
            if not approval or approval['used']: raise ValueError('unused human approval required')
            state = self.state()
            if approval['account_id'] != state['account_id'] or approval['revision'] != state['revision']:
                raise ValueError('account changed since approval; review again')
            if approval['expires_at'] is None or approval['expires_at'] <= self.clock():
                raise ValueError('approval expired; review again')
            sign = 1 if proposal.side == 'BUY' else -1
            quantity = state['positions'].get(proposal.symbol, 0) + sign * proposal.quantity
            cash = Decimal(state['cash']) - sign * Decimal(proposal.price) * proposal.quantity
            self.db.execute('UPDATE account SET cash=? WHERE id=1', (str(cash),))
            self.db.execute('INSERT INTO positions VALUES (?,?) ON CONFLICT(symbol) DO UPDATE SET quantity=excluded.quantity', (proposal.symbol, quantity))
            self.db.execute('UPDATE approvals SET used=1 WHERE digest=?', (proposal.digest(),))
            self.db.execute('UPDATE account_meta SET revision=revision+1 WHERE id=1')
            self.db.execute('UPDATE proposals SET status=? WHERE digest=?', ('PAPER_FILLED', proposal.digest()))
            result = {'request_id': request_id, 'digest': proposal.digest(), 'status': 'PAPER_FILLED', 'cash': str(cash),
                      'account_id': state['account_id'], 'revision': state['revision']+1, 'executed_at': self.clock()}
            self.db.execute('INSERT INTO orders VALUES (?,?,?)', (request_id, proposal.digest(), json.dumps(result)))
            self.trace('paper_execution', result)
            self.db.execute('COMMIT')
            return result
        except Exception:
            self.db.execute('ROLLBACK')
            raise

    def history(self) -> list[dict]:
        return [dict(row) for row in self.db.execute('SELECT * FROM traces ORDER BY id')]

    def transactions(self) -> list[dict]:
        return [json.loads(row['result']) for row in self.db.execute('SELECT result FROM orders ORDER BY rowid')]

    def proposal_history(self) -> list[dict]:
        return [{**dict(row), 'proposal': json.loads(row['payload'])}
                for row in self.db.execute('SELECT * FROM proposals ORDER BY created_at')]

    def reject(self, proposal: Proposal, reviewer: str, reason: str) -> dict:
        self._validate(proposal)
        if not reviewer.strip() or not reason.strip(): raise ValueError('reviewer and rejection reason required')
        self.db.execute('DELETE FROM approvals WHERE digest=?', (proposal.digest(),))
        self.db.execute('UPDATE proposals SET status=? WHERE digest=?', ('REJECTED', proposal.digest()))
        result = {'digest': proposal.digest(), 'reviewer': reviewer, 'reason': reason, 'status': 'REJECTED'}
        self.trace('human_rejection', result)
        return result


def demo(database: str = ':memory:') -> dict:
    start = time.perf_counter()
    floor = TradingFloor(database)
    try:
        proposal = floor.propose('ACA', 5)
        floor.approve(proposal, 'academy-local-reviewer')
        result = floor.execute(proposal, 'demo-order-001')
        return {'result': result, 'portfolio': floor.state(), 'trace': floor.history(),
                'metrics': {'elapsed_seconds': round(time.perf_counter() - start, 6), 'model_calls': 0, 'tokens': 0, 'cost_usd': '0.00'}}
    finally:
        floor.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database', default=':memory:')
    args = parser.parse_args()
    print(json.dumps(demo(args.database), indent=2))
