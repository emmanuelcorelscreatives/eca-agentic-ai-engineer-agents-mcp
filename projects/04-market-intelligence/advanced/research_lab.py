"""Stage 13 executable evidence, cache, profile and evaluation tools (stdlib)."""
from __future__ import annotations
import argparse
from dataclasses import dataclass, asdict
from datetime import date
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys

BASE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('eca_market_advanced_core', BASE/'market.py')
market = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = market
spec.loader.exec_module(market)


def canonical(value) -> bytes:
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()


def digest(value) -> str:return hashlib.sha256(canonical(value)).hexdigest()


def ratio(numerator: float | None, denominator: float | None) -> float:
    if numerator is None or denominator is None:raise ValueError('missing ratio input')
    if any(type(v) not in (int,float) or not math.isfinite(v) for v in (numerator,denominator)):
        raise ValueError('ratio inputs must be finite numbers')
    if denominator == 0:raise ValueError('zero denominator')
    return numerator/denominator


def fraction(value: float, unit: str) -> float:
    if type(value) not in (int,float) or not math.isfinite(value):raise ValueError('finite numeric value required')
    if unit == 'percent':return value/100
    if unit == 'fraction':return value
    raise ValueError('explicit percent or fraction unit required')


@dataclass(frozen=True)
class Evidence:
    id: str
    scenario_date: str
    company: str
    metric: str
    value: float | None
    units: str='fraction'
    fictional: bool=True
    def __post_init__(self):
        date.fromisoformat(self.scenario_date)
        if self.fictional is not True:raise ValueError('fixture evidence must remain fictional')
        if self.units != 'fraction':raise ValueError('normalized metrics must use fraction units')
        if self.metric not in ('growth','margin','debt_ratio'):raise ValueError('unknown metric')
        if self.value is not None and (type(self.value) not in (int,float) or not math.isfinite(self.value)):
            raise ValueError('metric must be finite or explicitly unknown')


def evidence_registry(directory: Path=BASE) -> dict[str, Evidence]:
    ledger=json.loads((directory/'synthetic-ledger.json').read_text())
    if ledger.get('fictional') is not True:raise ValueError('unlabelled ledger')
    registry={}
    for key,row in ledger['records'].items():
        metrics={'growth':ratio(row['current_revenue']-row['prior_revenue'],row['prior_revenue']),
                 'margin':None if row['operating_profit'] is None else ratio(row['operating_profit'],row['current_revenue']),
                 'debt_ratio':ratio(row['debt'],row['assets'])}
        suffix={'growth':'revenue-year-comparison','margin':'operating-profit','debt_ratio':'balance-sheet'}
        for metric,value in metrics.items():
            identifier=f'synthetic-ledger/{key}/{suffix[metric]}'
            registry[identifier]=Evidence(identifier,'2026-01-01',key,metric,value)
    return registry


def review_numeric_claims(companies, registry) -> list[str]:
    defects=[]
    for company in companies:
        key=company.symbol.split('-')[0].lower()
        for metric in ('growth','margin','debt_ratio'):
            value=getattr(company,metric);identifier=company.evidence.get(metric)
            if value is None:continue
            evidence=registry.get(identifier)
            if evidence is None or evidence.company != key or evidence.metric != metric:
                defects.append(f'{company.symbol}/{metric}: missing or misattributed evidence')
            elif evidence.value is None or not math.isclose(value,evidence.value,rel_tol=1e-10,abs_tol=1e-12):
                defects.append(f'{company.symbol}/{metric}: number disagrees with ledger')
    return defects


def sector_context(sector: str) -> dict:
    # No fictional row is promoted into a real trend observation.
    return dict(sector=sector,fictional=True,scenario_date='2026-01-01',
                live_market_signal=None, uncertainty='No approved live-sector evidence supplied')


class ResearchMemory:
    """Validated cache: source bytes and criteria both participate in the key."""
    def __init__(self):self._entries={}
    def put(self,source_sha: str,criteria: dict,report: dict,expected: dict):
        if report != expected:raise ValueError('unvalidated report cannot enter accepted memory')
        self._entries[digest(dict(source=source_sha,criteria=criteria))]=canonical(report)
    def get(self,source_sha: str,criteria: dict):
        raw=self._entries.get(digest(dict(source=source_sha,criteria=criteria)))
        return None if raw is None else json.loads(raw)


def escaped(value: str) -> str:
    return str(value).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('|','\\|').replace('\n',' ')


def markdown(report: dict) -> str:
    lines=['# Fictional Academy market comparison','',report['scope'],'',
           'Scenario date: 2026-01-01 (teaching date, not a live observation).','',
           'Criteria: `'+json.dumps(report['criteria'],sort_keys=True)+'`','']
    for profile in report['profiles']:
        lines.extend([f"## {escaped(profile['symbol'])}: {escaped(profile['name'])}",
                      f"Score: {profile['score']}/{profile['max_score']}",'',
                      '| Metric | Value (fraction) | Rule | Credit | Evidence |',
                      '| --- | --- | --- | --- | --- |'])
        for check in profile['checks']:
            value='unknown' if check['value'] is None else str(check['value'])
            rule=f"{check['operator']} {check['threshold']}"
            lines.append(f"| {check['metric']} | {value} | {rule} | {int(check['passed'])} | {escaped(check['evidence'] or 'missing')} |")
        lines+=['','Risks:']+['- '+escaped(risk) for risk in profile['risks']]
        lines+=['Uncertainties:']+['- '+escaped(uncertainty) for uncertainty in profile['uncertainties']]+['']
    return '\n'.join(lines)+'\n'


def evaluate(candidate: dict,reference: dict) -> dict:
    # Exact structured report is intentionally authoritative, not LLM confidence.
    defects=[]
    if set(candidate) != set(reference):defects.append('unexpected or missing report fields')
    for field in ('fictional','criteria','profiles','quality','market_context','scope'):
        if candidate.get(field) != reference[field]:defects.append('changed or missing '+field)
    symbols=[p.get('symbol') for p in candidate.get('profiles',[])]
    if len(set(symbols)) != len(symbols):defects.append('duplicate company')
    return dict(passed=not defects,defects=defects)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,required=True)
    args=parser.parse_args()
    companies=market.FixtureSource(BASE/'companies.json').companies()
    defects=review_numeric_claims(companies,evidence_registry())
    if defects:raise ValueError(defects)
    reference=market.run(market.FixtureSource(BASE/'companies.json'),market.Criteria())
    args.output_dir.mkdir(parents=True,exist_ok=False)
    (args.output_dir/'report.json').write_text(json.dumps(reference,indent=2)+'\n')
    (args.output_dir/'report.md').write_text(markdown(reference))
    (args.output_dir/'evidence.json').write_text(json.dumps({k:asdict(v) for k,v in evidence_registry().items()},indent=2)+'\n')
    print(json.dumps(dict(status='offline evidence checks passed',output=str(args.output_dir),
                         evaluation=evaluate(reference,reference),report_sha256=digest(reference))))
if __name__=='__main__':main()
