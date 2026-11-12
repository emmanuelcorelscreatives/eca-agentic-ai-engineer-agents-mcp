"""Thread-safe invocation boundaries for MCP/API adapters.

Each invocation creates, uses and closes its own SQLite connection on the calling
thread. Only the explicit database path is shared, never a connection object.
"""
from contextlib import contextmanager
from dataclasses import asdict
from pathlib import Path
import json
import os
from trading_floor import TradingFloor

class ToolServices:
    def __init__(self, database: str | None = None):
        self.database = database or os.environ.get('ACADEMY_PAPER_DB', 'paper.sqlite')
        if self.database == ':memory:':
            raise ValueError('ToolServices requires a shared file database, not per-call :memory:')

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
        if not namespace.strip() or not key.strip() or len(namespace)>80 or len(key)>100 or len(value)>10000:
            raise ValueError('invalid memory bounds')
        with self.connection() as floor:
            floor.db.execute('CREATE TABLE IF NOT EXISTS tool_memory(namespace TEXT,key TEXT,value TEXT,PRIMARY KEY(namespace,key))')
            floor.db.execute('INSERT INTO tool_memory VALUES (?,?,?) ON CONFLICT(namespace,key) DO UPDATE SET value=excluded.value',(namespace,key,value))
            floor.trace('memory_write',{'namespace':namespace,'key':key})
        return {'stored':True,'namespace':namespace,'key':key}

    def recall(self, namespace: str, key: str) -> dict:
        with self.connection() as floor:
            floor.db.execute('CREATE TABLE IF NOT EXISTS tool_memory(namespace TEXT,key TEXT,value TEXT,PRIMARY KEY(namespace,key))')
            row=floor.db.execute('SELECT value FROM tool_memory WHERE namespace=? AND key=?',(namespace,key)).fetchone()
            return {'namespace':namespace,'key':key,'found':row is not None,'value':row['value'] if row else None}

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
