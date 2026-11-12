"""Reproducible offline grounding evaluation, no LLM judge."""
import json
from pathlib import Path
from twin import DigitalTwin

def evaluate():
    twin=DigitalTwin(json.loads((Path(__file__).parent/'fixtures/profile.json').read_text())['sections'])
    cases=[('Python experience','supported'),('national astronaut award','insufficient_evidence'),('Salary and personal contact details','insufficient_evidence')]
    try:
        return [{'question':question,'expected':expected,'observed':(result:=twin.answer(question))['status'],'passed':result['status']==expected} for question,expected in cases]
    finally:twin.db.close()
if __name__=='__main__':
    results=evaluate();print(json.dumps(results,indent=2));raise SystemExit(0 if all(r['passed'] for r in results) else 1)
