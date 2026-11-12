"""Representative synthetic failure scenarios; no remote outage or model claims."""
import hashlib
import json
from pathlib import Path
from .observability import Trace

HERE=Path(__file__).parent

def load_suite(path=HERE/'scenarios-v2.json'):
    from datetime import datetime
    raw=path.read_bytes(); data=json.loads(raw)
    market_raw=(HERE.parent/'fixtures/market.json').read_bytes(); market=json.loads(market_raw)
    if set(data)!={'schema_version','synthetic','market_as_of','cases'} or data['schema_version']!=2 or data['synthetic'] is not True:
        raise ValueError('invalid suite')
    if data['market_as_of']!=market['as_of']: raise ValueError('market as-of mismatch')
    ids=set(); families={}
    required={'id','family','split','symbol','quantity','side','evidence_ids','as_of','fault','expected_state'}
    for row in data['cases']:
        if set(row)!=required or row['id'] in ids: raise ValueError('invalid/duplicate case')
        ids.add(row['id'])
        if row['split'] not in {'development','held-out'} or families.setdefault(row['family'],row['split'])!=row['split']:
            raise ValueError('family split leak')
        if type(row['quantity']) is not int or row['quantity']<1 or row['side'] not in {'BUY','SELL'}: raise ValueError('invalid order')
        if row['fault'] not in {None,'stale','conflicting-price','timeout','missing-evidence','agent-error'}: raise ValueError('invalid fault')
        if row['expected_state'] not in {'AWAITING_HUMAN_APPROVAL','RISK_REJECTED','RESEARCH_REJECTED','INCOMPLETE'}: raise ValueError('invalid expectation')
        if row['evidence_ids'] != [market['companies'][row['symbol']]['evidence_id']]: raise ValueError('unknown evidence')
        datetime.fromisoformat(row['as_of'].replace('Z','+00:00'))
    return data,{'suite_sha256':hashlib.sha256(raw).hexdigest(),'market_sha256':hashlib.sha256(market_raw).hexdigest(),'case_count':len(ids)}


def run_case(floor,case):
    trace=Trace(); before=floor.state()
    try:
        with trace.span('workflow','workflow'):
            with trace.span('research','tool'):
                if case['fault']=='timeout': raise TimeoutError('injected local fixture timeout')
                if case['fault']=='agent-error': raise RuntimeError('injected local agent error')
                research=floor.research(case['symbol'])
                if case['fault']=='missing-evidence': research.pop('evidence_id')
                if case['fault']=='conflicting-price': research['price']='0.01'
                if case['as_of']!=floor.market['as_of'] or research.get('evidence_id') not in case['evidence_ids'] or research['price']!=floor.market['companies'][case['symbol']]['price']:
                    state='RESEARCH_REJECTED'
                else:
                    with trace.span('risk','tool'):
                        p=floor.propose(case['symbol'],case['quantity'],case['side']); risk=floor.risk(p)
                    state='AWAITING_HUMAN_APPROVAL' if risk['allowed'] else 'RISK_REJECTED'
    except (TimeoutError,RuntimeError): state='INCOMPLETE'
    after=floor.state()
    if before!=after: raise AssertionError('scenario evaluation must not execute trades')
    return {'case_id':case['id'],'state':state,'expected':case['expected_state'],
            'passed':state==case['expected_state'],'ledger_unchanged':True,'trace':trace}
