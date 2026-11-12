"""Thread-safe invocation boundaries for MCP/API adapters.

Each invocation creates, uses and closes its own SQLite connection on the calling
thread. Only the explicit database path is shared, never a connection object.
"""
from contextlib import contextmanager
from dataclasses import asdict
from pathlib import Path
import json
import os
import re
from trading_floor import TradingFloor

class ToolServices:
    def __init__(self, database: str | None = None, *, memory_read_namespaces=None,
                 memory_write_namespaces=None, memory_forbidden_strings=()):
        self.database = database or os.environ.get('ACADEMY_PAPER_DB', 'paper.sqlite')
        if self.database == ':memory:':
            raise ValueError('ToolServices requires a shared file database, not per-call :memory:')
        # None is the trusted local application's existing single-account access.
        # External callers must receive explicitly configured frozen scope sets.
        self.memory_read_namespaces = self._memory_scopes(memory_read_namespaces)
        self.memory_write_namespaces = self._memory_scopes(memory_write_namespaces)
        if isinstance(memory_forbidden_strings, (str, bytes)):
            raise ValueError('memory forbidden strings must be a collection')
        self._memory_forbidden_strings = tuple(memory_forbidden_strings)
        if any(not isinstance(value,str) or not value for value in self._memory_forbidden_strings):
            raise ValueError('invalid memory forbidden string')

    @staticmethod
    def _memory_scopes(scopes):
        if scopes is None: return None
        if isinstance(scopes,(str,bytes)): raise ValueError('memory scopes must be a collection')
        result=frozenset(scopes)
        if any(not isinstance(value,str) or not value.strip() or value!=value.strip() or len(value)>80 for value in result):
            raise ValueError('invalid configured memory namespace')
        return result

    def _memory_namespace(self,namespace,*,write=False):
        if not isinstance(namespace,str) or not namespace.strip() or namespace!=namespace.strip() or len(namespace)>80:
            raise ValueError('invalid memory namespace')
        allowed=self.memory_write_namespaces if write else self.memory_read_namespaces
        if allowed is not None and namespace not in allowed:
            raise PermissionError('memory namespace is outside the configured caller scope')

    @staticmethod
    def _memory_key(key):
        if not isinstance(key,str) or not key.strip() or len(key)>100:
            raise ValueError('invalid memory key')

    def _memory_sensitive(self,text):
        # Defense in depth, not a claim to recognize every unknown credential.
        return any(value in text for value in self._memory_forbidden_strings) or bool(re.search(
            r'''(?i)\bbearer\s+\S+|["']?\b(?:api[_-]?key|access[_-]?token|password|secret)["']?\s*[=:]\s*\S+''',text))

    @contextmanager
    def connection(self):
        floor = TradingFloor(self.database)
        try: yield floor
        finally: floor.close()

    def research_company(self, symbol: str) -> dict:
        with self.connection() as floor: return floor.research(symbol)

    def propose_order(self, symbol: str, quantity: int, side: str = 'BUY') -> dict:
        with self.connection() as floor:
            proposal = floor.propose(symbol, quantity, side)
            return {'proposal': asdict(proposal), 'risk': floor.risk(proposal)}

    def portfolio(self) -> dict:
        with self.connection() as floor: return floor.state()

    def search_research(self, query: str, limit: int = 5) -> dict:
        """Grounded local corpus retrieval, not claimed to be a web search."""
        if not query.strip() or len(query) > 500 or type(limit) is not int or not 1 <= limit <= 10:
            raise ValueError('nonempty query <=500 characters and limit 1..10 required')
        words = set(query.lower().split())
        with self.connection() as floor:
            matches=[]
            for symbol, record in floor.market['companies'].items():
                text = f"{symbol} {record['name']} {record['sector']} {record['research']}"
                score=sum(word in text.lower() for word in words)
                if score: matches.append({'symbol':symbol,'evidence_id':record['evidence_id'],'text':text,'score':score})
            matches.sort(key=lambda item:(-item['score'],item['symbol']))
            return {'query':query,'matches':matches[:limit],'source':'local synthetic fixture corpus','synthetic':True}

    def grounded_brief(self, query: str) -> dict:
        """Extractive RAG boundary: every claim is returned with its source text."""
        retrieved=self.search_research(query)
        return {'query':query,'claims':[{'text':row['text'],'citation':row['evidence_id']} for row in retrieved['matches']],
                'answer_mode':'deterministic extractive retrieval; no language model called',
                'abstained':not retrieved['matches'],'synthetic':True}

    def remember(self, namespace: str, key: str, value: str) -> dict:
        self._memory_namespace(namespace,write=True)
        self._memory_key(key)
        if not isinstance(value,str) or len(value)>10000:
            raise ValueError('invalid memory bounds')
        if self._memory_sensitive(namespace) or self._memory_sensitive(key) or self._memory_sensitive(value):
            raise ValueError('credential-like or operator-forbidden memory content is unavailable')
        with self.connection() as floor:
            floor.db.execute('CREATE TABLE IF NOT EXISTS tool_memory(namespace TEXT,key TEXT,value TEXT,PRIMARY KEY(namespace,key))')
            floor.db.execute('INSERT INTO tool_memory VALUES (?,?,?) ON CONFLICT(namespace,key) DO UPDATE SET value=excluded.value',(namespace,key,value))
            floor.trace('memory_write',{'namespace':namespace,'key':key})
        return {'stored':True,'namespace':namespace,'key':key}

    def recall(self, namespace: str, key: str) -> dict:
        self._memory_namespace(namespace)
        self._memory_key(key)
        if self._memory_sensitive(namespace) or self._memory_sensitive(key):
            raise ValueError('credential-like or operator-forbidden lookup is unavailable')
        with self.connection() as floor:
            floor.db.execute('CREATE TABLE IF NOT EXISTS tool_memory(namespace TEXT,key TEXT,value TEXT,PRIMARY KEY(namespace,key))')
            row=floor.db.execute('SELECT value FROM tool_memory WHERE namespace=? AND key=?',(namespace,key)).fetchone()
            if row is not None and self._memory_sensitive(row['value']):
                return {'namespace':namespace,'key':key,'found':False,'value':None,'withheld':True}
            return {'namespace':namespace,'key':key,'found':row is not None,'value':row['value'] if row else None}

    def search_memory(self, namespace: str, query: str, limit: int = 5) -> dict:
        """Search one configured namespace, never another account/scope.

        Parameterized literal substring matching, with SQLite's ASCII case folding.
        No wildcard expansion, semantic/embedding ranking or fabricated relevance.
        """
        self._memory_namespace(namespace)
        if not isinstance(query,str) or not query.strip() or len(query)>500 or type(limit) is not int or not 1<=limit<=10:
            raise ValueError('nonempty memory query <=500 characters and limit1..10 required')
        query=query.strip()
        if self._memory_sensitive(namespace) or self._memory_sensitive(query):
            raise ValueError('credential-like or operator-forbidden lookup is unavailable')
        # A SQL predicate excludes known sensitive rows before LIMIT so a hidden
        # historical entry cannot suppress otherwise matching permitted results.
        with self.connection() as floor:
            floor.db.execute('CREATE TABLE IF NOT EXISTS tool_memory(namespace TEXT,key TEXT,value TEXT,PRIMARY KEY(namespace,key))')
            floor.db.create_function('academy_memory_visible',2,
                                    lambda key,value:int(not self._memory_sensitive(key) and not self._memory_sensitive(value)))
            rows=floor.db.execute('''SELECT key,value FROM tool_memory
                WHERE namespace=? AND (instr(lower(key),lower(?))>0 OR instr(lower(value),lower(?))>0)
                AND academy_memory_visible(key,value)=1 ORDER BY key LIMIT ?''',
                (namespace,query,query,limit)).fetchall()
            return {'namespace':namespace,'query':query,'matches':[{'key':row['key'],'value':row['value']} for row in rows],
                    'limit':limit,'search_mode':'literal substring with SQLite ASCII case folding',
                    'scope':'configured namespace in a single-account database; no authentication claim'}

    def orchestrate(self, symbol: str, quantity: int) -> dict:
        """Researcher-as-tool -> strategist -> deterministic risk -> human hold.

        Role boundaries are explicit and runnable; these local role implementations
        are deterministic, not a claim of autonomous model calls.
        """
        research=self.research_company(symbol)
        structured=self.propose_order(symbol,quantity)
        result={'researcher':research,'strategist':structured['proposal'],'risk_manager':structured['risk'],
                'next_state':'AWAITING_HUMAN_APPROVAL' if structured['risk']['allowed'] else 'RISK_REJECTED',
                'execution_performed':False,'role_mode':'deterministic offline reference'}
        self.remember('orchestration',structured['risk']['digest'],json.dumps(result,sort_keys=True))
        return result
