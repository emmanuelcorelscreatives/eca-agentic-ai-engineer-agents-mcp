"""Deterministic input validation, scoped context and budget accounting (not an LLM)."""
import json
from dataclasses import dataclass, field
from pathlib import Path

CONFIG = Path(__file__).with_name("config")

def configuration():
    agents = json.loads((CONFIG / "agents.yaml").read_text())
    tasks = json.loads((CONFIG / "tasks.yaml").read_text())
    seen = set()
    for name, task in tasks.items():
        if task['agent'] not in agents or not set(task['context']) <= seen:
            raise ValueError('unknown role or forward task context')
        if not task['expected_output'].strip():
            raise ValueError('measurable expected output required')
        seen.add(name)
    return agents, tasks

def load_facts(path):
    pack = json.loads(Path(path).read_text())
    if pack.get('fictional') is not True or not pack.get('topic'):
        raise ValueError('explicit fictional fact pack required')
    facts = pack.get('facts', [])
    if not facts or len(facts) > 20:
        raise ValueError('fact count outside teaching budget')
    ids = [f['id'] for f in facts]
    if len(ids) != len(set(ids)) or any(not isinstance(f['text'], str) or not f['text'].strip() for f in facts):
        raise ValueError('unique IDs and nonempty fact text required')
    if sum(len(f['text']) for f in facts) > 1200:
        raise ValueError('fact context too large')
    return pack

@dataclass
class FactSearch:
    pack: dict
    limit: int = 6
    calls: int = 0
    def search(self, query: str, max_results: int = 4):
        if not isinstance(query, str) or not 1 <= len(query.strip()) <= 100:
            raise ValueError('query must contain 1-100 characters')
        if isinstance(max_results, bool) or not isinstance(max_results, int) or not 1 <= max_results <= 4:
            raise ValueError('max_results must be an integer 1-4')
        if self.calls >= self.limit:
            raise RuntimeError('shared tool-call budget exhausted')
        self.calls += 1
        terms = query.lower().split()
        matches = [f for f in self.pack['facts'] if query == '*' or any(t in f['text'].lower() or t == f['id'].lower() for t in terms)]
        return [{'source':'fictional-retailer-pack', **f} for f in matches[:max_results]]

@dataclass
class ScopedMemory:
    """Application-owned bounded explicit context, not CrewAI vector memory."""
    run_id: str
    max_chars: int = 1200
    _items: dict = field(default_factory=dict)
    def put(self, run_id, key, value):
        if run_id != self.run_id: raise PermissionError('cross-run memory denied')
        if key not in {'support','challenge','verdict'}: raise PermissionError('unapproved context key')
        candidate = dict(self._items, **{key:value})
        if any(not isinstance(v,str) for v in candidate.values()) or sum(map(len,candidate.values())) > self.max_chars:
            raise ValueError('context character budget exceeded')
        self._items = candidate
    def context(self, run_id, keys):
        if run_id != self.run_id: raise PermissionError('cross-run memory denied')
        if not set(keys) <= {'support','challenge','verdict'}: raise PermissionError('unapproved context key')
        return {key:self._items[key] for key in keys if key in self._items}
    def reset(self): self._items.clear()

def validate_verdict(result, pack):
    required = {'decision','fact_ids','rationale','uncertainties','fictional'}
    if set(result) != required or result['fictional'] is not True:
        raise ValueError('exact fictional verdict schema required')
    if result['decision'] not in pack['allowed_decisions']:
        raise ValueError('unsupported decision')
    ids = result['fact_ids']
    known = {f['id'] for f in pack['facts']}
    if not isinstance(ids,list) or len(ids)<2 or len(ids)!=len(set(ids)) or not set(ids)<=known:
        raise ValueError('at least two distinct real fact IDs required')
    if not isinstance(result['rationale'],str) or not result['rationale'].strip(): raise ValueError('rationale required')
    if not isinstance(result['uncertainties'],list) or not result['uncertainties'] or any(not isinstance(v,str) or not v.strip() for v in result['uncertainties']):
        raise ValueError('explicit uncertainty required')
    return result
