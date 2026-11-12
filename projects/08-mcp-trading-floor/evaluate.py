"""Repeatable risk evaluation; does not masquerade as an LLM judge."""
import json
from trading_floor import TradingFloor

CASES = [
    {'id':'bounded-buy','symbol':'ACA','side':'BUY','quantity':5,'allowed':True},
    {'id':'oversized-buy','symbol':'ACA','side':'BUY','quantity':30,'allowed':False},
    {'id':'no-short-sales','symbol':'LAB','side':'SELL','quantity':1,'allowed':False},
    {'id':'small-lab-buy','symbol':'LAB','side':'BUY','quantity':10,'allowed':True},
]

def evaluate():
    results=[]
    for case in CASES:
        floor=TradingFloor()
        try:
            proposal=floor.propose(case['symbol'],case['quantity'],case['side'])
            decision=floor.risk(proposal)
            results.append({'id':case['id'],'expected_allowed':case['allowed'],'actual':decision,'passed':decision['allowed']==case['allowed']})
        finally: floor.close()
    return {'cases':results,'passed':sum(row['passed'] for row in results),'total':len(results),'model_judge_used':False}

if __name__=='__main__':
    result=evaluate()
    print(json.dumps(result,indent=2))
    raise SystemExit(0 if result['passed']==result['total'] else 1)
