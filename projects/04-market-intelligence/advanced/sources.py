"""Typed replaceable company/market adapters over dated fictional source records.

AUTHOR-ONLY semantic repair: execution and independent validation are pending.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
from datetime import date
import hashlib
import json
import math
from pathlib import Path
from typing import Generic, Literal, Protocol, TypeVar

T=TypeVar('T')

@dataclass(frozen=True)
class Result(Generic[T]):
    status: Literal['success','absent','error']
    value: T | None=None
    reason: str | None=None
    def __post_init__(self):
        if self.status not in ('success','absent','error'):raise ValueError('unknown adapter status')
        if self.status=='success' and (self.value is None or self.reason is not None):raise ValueError('success needs a value only')
        if self.status!='success' and (self.value is not None or not isinstance(self.reason,str) or not self.reason):raise ValueError('absence/error needs an explicit reason only')
    def json(self):
        # Canonical wire types: tuples become lists before an LLM/Pydantic JSON
        # round trip, so truthful structured outputs compare equal to references.
        return json.loads(json.dumps(asdict(self),allow_nan=False))

@dataclass(frozen=True)
class SourceDocument:
    id: str
    subject: str
    date: str
    fictional: bool
    extract: str
    def __post_init__(self):
        date.fromisoformat(self.date)
        if self.fictional is not True:raise ValueError('teaching source must remain fictional')
        if any(not isinstance(v,str) or not v.strip() for v in (self.id,self.subject,self.extract)):raise ValueError('source identity and content required')

@dataclass(frozen=True)
class CompanyResearch:
    symbol: str
    scenario_date: str
    business: SourceDocument
    products: tuple[SourceDocument,...]
    competition: tuple[SourceDocument,...]
    uncertainties: tuple[str,...]
    fictional: bool=True
    def __post_init__(self):
        date.fromisoformat(self.scenario_date)
        if not self.products or not self.competition:raise ValueError('business/product/competition coverage required')
        for doc in (self.business,*self.products,*self.competition):
            if doc.subject != self.symbol or doc.date != self.scenario_date:raise ValueError('company source attribution/date mismatch')
        if self.fictional is not True:raise ValueError('fictional label required')

@dataclass(frozen=True)
class Signal:
    id: str
    metric: str
    value: float
    unit: str
    direction: str
    evidence: SourceDocument
    def __post_init__(self):
        if type(self.value) not in (int,float) or not math.isfinite(self.value):raise ValueError('finite signal required')
        if self.unit not in ('fraction','weeks'):raise ValueError('explicit supported signal unit required')
        if self.direction not in ('increase','decrease','level'):raise ValueError('signal direction required')
        if not self.id or not self.metric:raise ValueError('signal identity required')

@dataclass(frozen=True)
class MarketResearch:
    sector: str
    scenario_date: str
    conditions: str
    signals: tuple[Signal,...]
    uncertainties: tuple[str,...]
    fictional: bool=True
    def __post_init__(self):
        date.fromisoformat(self.scenario_date)
        if not self.conditions or not self.signals:raise ValueError('substantive market conditions/signals required')
        if self.fictional is not True:raise ValueError('fictional label required')
        if len({s.id for s in self.signals})!=len(self.signals):raise ValueError('duplicate sector signal')
        if any(s.evidence.subject != self.sector or s.evidence.date != self.scenario_date for s in self.signals):raise ValueError('sector source attribution/date mismatch')

class ResearchAdapter(Protocol):
    source_sha256: str
    def company(self,symbol: str)->Result[CompanyResearch]:...
    def market(self,sector: str)->Result[MarketResearch]:...

class FixtureResearchAdapter:
    """Load once, pin bytes, and represent unavailable/malformed sources explicitly."""
    def __init__(self,path: Path):
        self.source_sha256='unavailable';self._error=None;self._companies={};self._markets={}
        try:
            with Path(path).open('rb') as handle:raw=handle.read(256_001)
            if len(raw)>256_000:raise ValueError('source payload quota exceeded')
            self.source_sha256=hashlib.sha256(raw).hexdigest()
            data=json.loads(raw)
            if data.get('schema_version')!=1 or data.get('fictional') is not True:raise ValueError('wrong source schema/scope')
            scenario=data['scenario_date'];date.fromisoformat(scenario)
            docs={}
            for row in data['documents']:
                document=SourceDocument(**row)
                if document.id in docs:raise ValueError('duplicate source ID')
                docs[document.id]=document
            for row in data['companies']:
                symbol=row['symbol']
                if symbol in self._companies:raise ValueError('duplicate company source')
                self._companies[symbol]=CompanyResearch(symbol,scenario,docs[row['business']],
                    tuple(docs[k] for k in row['products']),tuple(docs[k] for k in row['competition']),tuple(row['uncertainties']))
            for row in data['sectors']:
                sector=row['sector']
                if sector in self._markets:raise ValueError('duplicate sector source')
                signals=[]
                for item in row['signals']:
                    if 'numerator' in item:
                        expected=self._ratio(item['numerator'],item['denominator'])
                    elif item['unit']=='fraction':
                        expected=self._ratio(item['current']-item['prior'],item['prior'])
                    else:expected=item['current']
                    if 'prior' in item and 'current' in item:
                        direction = 'increase' if item['current'] > item['prior'] else 'decrease' if item['current'] < item['prior'] else 'level'
                        if item['direction'] != direction:raise ValueError('signal direction disagrees with source')
                    if not math.isclose(expected,item['value'],rel_tol=1e-10,abs_tol=1e-12):raise ValueError('signal arithmetic does not reconcile')
                    signals.append(Signal(item['id'],item['metric'],item['value'],item['unit'],item['direction'],docs[item['evidence']]))
                self._markets[sector]=MarketResearch(sector,scenario,row['conditions'],tuple(signals),tuple(row['uncertainties']))
        except OSError:self._error='source-unavailable'
        except (ValueError,TypeError,KeyError,AttributeError):self._error='malformed-source'
        if self._error:self._companies={};self._markets={}
    @staticmethod
    def _ratio(a,b):
        if any(type(v) not in (int,float) or not math.isfinite(v) for v in (a,b)) or b==0:raise ValueError('invalid ratio source')
        return a/b
    def company(self,symbol):
        if self._error:return Result('error',reason=self._error)
        value=self._companies.get(symbol)
        return Result('absent',reason='company-not-in-approved-source') if value is None else Result('success',value)
    def market(self,sector):
        if self._error:return Result('error',reason=self._error)
        value=self._markets.get(sector)
        return Result('absent',reason='sector-not-in-approved-source') if value is None else Result('success',value)


def research_snapshot(adapter: ResearchAdapter,companies) -> dict:
    """Tool-ready typed adapter output, preserving absence/error without made-up facts."""
    return {'fictional':True,'source_sha256':adapter.source_sha256,
            'companies':{c.symbol:adapter.company(c.symbol).json() for c in companies},
            'markets':{sector:adapter.market(sector).json() for sector in sorted({c.sector for c in companies})},
            'scope':'Dated fictional conditions for learning; not live markets, investment advice or forecasts.'}


def main():
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,default=Path(__file__).with_name('research_sources.json'))
    query=parser.add_mutually_exclusive_group(required=True)
    query.add_argument('--company');query.add_argument('--sector')
    args=parser.parse_args()
    adapter=FixtureResearchAdapter(args.source)
    result=adapter.company(args.company) if args.company else adapter.market(args.sector)
    print(json.dumps(result.json(),indent=2,allow_nan=False))

if __name__=='__main__':main()
