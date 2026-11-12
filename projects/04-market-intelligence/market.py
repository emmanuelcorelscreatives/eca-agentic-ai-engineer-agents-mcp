"""Offline research workflow. All bundled companies and metrics are fictional."""
from __future__ import annotations
import argparse
from dataclasses import asdict, dataclass
import json
import math
from pathlib import Path
from typing import Protocol

@dataclass(frozen=True)
class Criteria:
    min_growth: float = 0.10
    min_margin: float = 0.12
    max_debt_ratio: float = 0.5
    def __post_init__(self):
        for field, value in asdict(self).items():
            if not math.isfinite(value) or not 0 <= value <= 1:
                raise ValueError(f'{field} must be a finite fraction from 0 to 1')

@dataclass(frozen=True)
class Company:
    symbol: str
    name: str
    sector: str
    growth: float | None
    margin: float | None
    debt_ratio: float | None
    evidence: dict[str, str]
    risks: list[str]
    def __post_init__(self):
        if not self.symbol or not self.name or not self.sector:
            raise ValueError('company identity is required')
        for key in ('growth', 'margin', 'debt_ratio'):
            value = getattr(self, key)
            if value is not None and (not isinstance(value, (int, float)) or not math.isfinite(value)):
                raise ValueError(f'invalid {key}')
        if self.debt_ratio is not None and self.debt_ratio < 0:
            raise ValueError('debt_ratio cannot be negative')

class ResearchSource(Protocol):
    def companies(self) -> list[Company]: ...

class FixtureSource:
    def __init__(self, path: Path): self.path = path
    def companies(self):
        payload = json.loads(self.path.read_text())
        if payload.get('fictional') is not True:
            raise ValueError('offline source must explicitly label fictional data')
        result = [Company(**row) for row in payload['companies']]
        if len({c.symbol for c in result}) != len(result):
            raise ValueError('duplicate company symbols')
        return result

def screen(company: Company, criteria: Criteria) -> dict:
    rules = [('growth', '>=', criteria.min_growth), ('margin', '>=', criteria.min_margin),
             ('debt_ratio', '<=', criteria.max_debt_ratio)]
    checks, uncertainties = [], []
    for metric, op, threshold in rules:
        value = getattr(company, metric)
        evidence = company.evidence.get(metric)
        supported = value is not None and bool(evidence)
        passed = supported and (value >= threshold if op == '>=' else value <= threshold)
        if not supported:
            uncertainties.append(f'{metric}: missing value or evidence; receives no credit')
        checks.append(dict(metric=metric, value=value, operator=op, threshold=threshold,
                           evidence=evidence, supported=supported, passed=passed))
    return dict(symbol=company.symbol, name=company.name, sector=company.sector,
                score=sum(c['passed'] for c in checks), max_score=len(checks),
                checks=checks, risks=company.risks, uncertainties=uncertainties)

def run(source: ResearchSource, criteria: Criteria) -> dict:
    # Context is passed explicitly; no hidden persisted or provider memory.
    companies = source.companies()
    profiles = [screen(c, criteria) for c in companies]
    profiles.sort(key=lambda c: (-c['score'], c['symbol']))
    sectors = sorted({c.sector for c in companies})
    return dict(schema_version=1, fictional=True,
                scope='Educational fictional comparison, not investment advice or live market research.',
                criteria=asdict(criteria), market_context=dict(sectors=sectors,
                observation='Fixture contains no real-time market-condition evidence.'),
                profiles=profiles, quality=dict(company_count=len(companies),
                fully_supported_count=sum(not c['uncertainties'] for c in profiles),
                unsupported_metric_count=sum(len(c['uncertainties']) for c in profiles)))

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data', type=Path, default=Path(__file__).with_name('companies.json'))
    p.add_argument('--min-growth', type=float, default=.10)
    p.add_argument('--min-margin', type=float, default=.12)
    p.add_argument('--max-debt-ratio', type=float, default=.5)
    p.add_argument('--output', type=Path)
    a = p.parse_args()
    result = run(FixtureSource(a.data), Criteria(a.min_growth, a.min_margin, a.max_debt_ratio))
    text = json.dumps(result, indent=2, allow_nan=False)
    if a.output: a.output.write_text(text + '\n')
    else: print(text)

if __name__ == '__main__': main()
