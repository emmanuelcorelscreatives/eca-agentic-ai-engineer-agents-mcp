"""Validate real fixture references and measure ordinary risk-rule outcomes."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def validate_dataset(path=Path(__file__).with_name('scenarios.json')):
    raw = path.read_bytes(); data = json.loads(raw)
    market_raw = (ROOT / 'fixtures/market.json').read_bytes(); market = json.loads(market_raw)
    if data.get('synthetic') is not True or data['as_of'] != market['as_of']:
        raise ValueError('synthetic/as-of mismatch')
    ids = set(); families = {}
    for row in data['cases']:
        if row['id'] in ids: raise ValueError('duplicate scenario')
        ids.add(row['id'])
        if row['split'] not in {'development', 'held-out'}: raise ValueError('invalid split')
        if families.setdefault(row['family'], row['split']) != row['split']:
            raise ValueError('family leaks across splits')
        if type(row['expected_allowed']) is not bool or type(row['quantity']) is not int or row['quantity'] <= 0:
            raise ValueError('invalid expected decision/quantity')
        if row['side'] not in {'BUY', 'SELL'}: raise ValueError('invalid side')
        if market['companies'][row['symbol']]['evidence_id'] != row['evidence_id']:
            raise ValueError('unknown evidence fixture')
    return data, {'dataset_sha256': hashlib.sha256(raw).hexdigest(),
                  'market_sha256': hashlib.sha256(market_raw).hexdigest(), 'cases': len(ids)}


def decision_metrics(rows):
    total = len(rows)
    observed = [r for r in rows if type(r.get('actual_allowed')) is bool]
    correct = sum(r['actual_allowed'] == r['expected_allowed'] for r in observed)
    return {'total': total, 'observed': len(observed), 'unavailable': total-len(observed),
            'correct': correct, 'accuracy_on_observed': correct/len(observed) if observed else None}


def evaluate():
    from trading_floor import TradingFloor
    data, manifest = validate_dataset(); rows = []
    for case in data['cases']:
        floor = TradingFloor()
        try:
            proposal = floor.propose(case['symbol'], case['quantity'], case['side'])
            result = floor.risk(proposal)
            rows.append({'id': case['id'], 'expected_allowed': case['expected_allowed'],
                         'actual_allowed': result['allowed'], 'reasons': result['reasons']})
        finally: floor.close()
    return {'manifest': manifest, 'results': rows, 'metrics': decision_metrics(rows),
            'model_calls': 0, 'scope': 'deterministic synthetic risk decisions only'}

if __name__ == '__main__': print(json.dumps(evaluate(), indent=2))
