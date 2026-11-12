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
    def __init__(self, database: str = ':memory:', fixtures: Path = FIXTURES):
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
        ''')

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
        return {'cash': str(cash), 'positions': positions, 'equity': str(value), 'synthetic': True}

    def risk(self, proposal: Proposal) -> dict:
        self._validate(proposal)
        state = self.state()
        cost = amount(proposal.price) * proposal.quantity
        existing = state['positions'].get(proposal.symbol, 0)
        reasons = []
        if proposal.side == 'BUY':
            if cost > Decimal(state['cash']): reasons.append('insufficient_cash')
            if cost > Decimal('2000.00'): reasons.append('order_limit')
            if Decimal(proposal.price) * (existing + proposal.quantity) > Decimal(state['equity']) * Decimal('0.25'):
                reasons.append('position_limit')
        elif proposal.quantity > existing:
            reasons.append('short_sales_disabled')
        return {'allowed': not reasons, 'reasons': reasons, 'notional': str(cost), 'digest': proposal.digest()}

    def approve(self, proposal: Proposal, reviewer: str) -> dict:
        """Human entry point: transport must authenticate a reviewer before calling."""
        if not reviewer.strip(): raise ValueError('reviewer is required')
        decision = self.risk(proposal)
        if not decision['allowed']: raise ValueError('risk rejected: ' + ','.join(decision['reasons']))
        self.db.execute('INSERT OR IGNORE INTO approvals(digest,reviewer) VALUES (?,?)', (proposal.digest(), reviewer))
        self.trace('human_approval', {'digest': proposal.digest(), 'reviewer': reviewer})
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
            sign = 1 if proposal.side == 'BUY' else -1
            quantity = state['positions'].get(proposal.symbol, 0) + sign * proposal.quantity
            cash = Decimal(state['cash']) - sign * Decimal(proposal.price) * proposal.quantity
            self.db.execute('UPDATE account SET cash=? WHERE id=1', (str(cash),))
            self.db.execute('INSERT INTO positions VALUES (?,?) ON CONFLICT(symbol) DO UPDATE SET quantity=excluded.quantity', (proposal.symbol, quantity))
            self.db.execute('UPDATE approvals SET used=1 WHERE digest=?', (proposal.digest(),))
            result = {'request_id': request_id, 'digest': proposal.digest(), 'status': 'PAPER_FILLED', 'cash': str(cash)}
            self.db.execute('INSERT INTO orders VALUES (?,?,?)', (request_id, proposal.digest(), json.dumps(result)))
            self.trace('paper_execution', result)
            self.db.execute('COMMIT')
            return result
        except Exception:
            self.db.execute('ROLLBACK')
            raise

    def history(self) -> list[dict]:
        return [dict(row) for row in self.db.execute('SELECT * FROM traces ORDER BY id')]


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
