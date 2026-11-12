"""Correlated spans with conservative allowlisted payloads and explicit usage unknowns."""
from contextlib import contextmanager
from datetime import datetime, timezone
from decimal import Decimal
import json
import time
import uuid

# Do not export prompt bodies, exception strings, credentials or arbitrary nested data.
SAFE_FIELDS = {'symbol', 'quantity', 'allowed', 'reason_code', 'order_id', 'evidence_id', 'model', 'operation'}

class Trace:
    def __init__(self, run_id=None):
        self.run_id = run_id or str(uuid.uuid4())
        self.events = []
        self._parents = []

    @contextmanager
    def span(self, name, kind, **fields):
        if kind not in {'agent', 'tool', 'approval', 'order', 'model', 'workflow'}:
            raise ValueError('unsupported span kind')
        event = {'run_id': self.run_id, 'span_id': str(uuid.uuid4()),
                 'parent_span_id': self._parents[-1] if self._parents else None,
                 'name': name, 'kind': kind, 'started_at': datetime.now(timezone.utc).isoformat(),
                 'fields': {k: v for k, v in fields.items() if k in SAFE_FIELDS and isinstance(v, (str, bool, int, type(None)))}}
        start = time.monotonic()
        self._parents.append(event['span_id'])
        try:
            yield event
            event['outcome'] = 'success'
        except BaseException as exc:
            event['outcome'] = 'failed'
            event['error_type'] = type(exc).__name__  # exception message might contain secrets
            raise
        finally:
            self._parents.pop()
            event['duration_seconds'] = time.monotonic() - start
            self.events.append(event)

    def export(self, path):
        # Whitelist again because caller receives a mutable span handle.
        records = []
        for event in self.events:
            row = {k: event[k] for k in ('run_id', 'span_id', 'parent_span_id', 'name', 'kind', 'started_at', 'duration_seconds', 'outcome')}
            row['fields'] = {k: v for k, v in event['fields'].items() if k in SAFE_FIELDS and isinstance(v, (str, int, bool, type(None)))}
            if 'error_type' in event: row['error_type'] = event['error_type']
            records.append(json.dumps(row, sort_keys=True))
        path.write_text('\n'.join(records) + '\n')


def usage_report(calls, prices):
    """Input leaf model calls only; duplicate call IDs fail rather than double count.

    prices: model -> dated {input_per_million, cached_per_million, output_per_million}.
    input_tokens includes cached_input_tokens. Unknown usage/prices => unknown cost.
    """
    seen = set(); rows = []; total = Decimal(0); unknown = 0
    for call in calls:
        if call['call_id'] in seen: raise ValueError('duplicate leaf call')
        seen.add(call['call_id'])
        counts = [call.get(k) for k in ('input_tokens', 'cached_input_tokens', 'output_tokens')]
        if any(x is not None and (type(x) is not int or x < 0) for x in counts):
            raise ValueError('invalid token count')
        price = prices.get(call['model'])
        cost = None
        if all(x is not None for x in counts):
            inp, cached, out = counts
            if cached > inp: raise ValueError('cached tokens exceed input')
            if price is not None:
                rates = [Decimal(str(price[k])) for k in ('input_per_million', 'cached_per_million', 'output_per_million')]
                if not price.get('as_of') or any(not r.is_finite() or r < 0 for r in rates):
                    raise ValueError('dated finite prices required')
                cost = ((inp-cached)*rates[0]+cached*rates[1]+out*rates[2])/Decimal(1000000)
                total += cost
        if cost is None: unknown += 1
        rows.append({'call_id': call['call_id'], 'cost': str(cost) if cost is not None else None})
    return {'calls': rows, 'known_subtotal': str(total), 'unknown_calls': unknown,
            'total_cost': None if unknown else str(total)}
