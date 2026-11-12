"""Assemble numeric, business/product/competition and industry research together.

This semantic repair is authored source, not a claim that its commands passed QA.
"""
import argparse
from dataclasses import asdict
import json
from pathlib import Path
import importlib.util
import sys

def _load(name,filename):
    location=Path(__file__).with_name(filename)
    if name in sys.modules:
        module=sys.modules[name]
        if Path(module.__file__).resolve()!=location.resolve():raise ValueError('unexpected module identity')
        return module
    spec=importlib.util.spec_from_file_location(name,location)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    return module

_lab=_load('eca_stage13_complete_report_lab','research_lab.py')
_sources=_load('eca_stage13_complete_report_sources','sources.py')
BASE,market=_lab.BASE,_lab.market
evidence_registry,review_numeric_claims=_lab.evidence_registry,_lab.review_numeric_claims
markdown,escaped=_lab.markdown,_lab.escaped
FixtureResearchAdapter,research_snapshot=_sources.FixtureResearchAdapter,_sources.research_snapshot


def make_report(directory: Path=BASE,criteria=None):
    criteria=criteria or market.Criteria()
    source=market.FixtureSource(directory/'companies.json')
    companies=source.companies()
    defects=review_numeric_claims(companies,evidence_registry(directory))
    if defects:raise ValueError('numeric source disagreement: '+repr(defects))
    adapter=FixtureResearchAdapter(directory/'advanced/research_sources.json')
    research=research_snapshot(adapter,companies)
    if any(row['status']=='error' for name in ('companies','markets') for row in research[name].values()):
        raise ValueError('research source unavailable/malformed; no completed report')
    return {**market.run(source,criteria),'schema_version':2,
            'company_research':research['companies'],'market_research':research['markets'],
            'research_source_sha256':research['source_sha256']}


def render(report):
    text=markdown(report)
    text+='\n# Business, product and competitive evidence\n'
    for symbol,result in report['company_research'].items():
        text+='\n## '+escaped(symbol)+'\n'
        if result['status']!='success':
            text+='Source status: '+escaped(result['status'])+' — '+escaped(result['reason'])+'\n';continue
        value=result['value']
        text+='Scenario date: '+escaped(value['scenario_date'])+' (fictional).\n'
        for label,records in [('Business',[value['business']]),('Products',value['products']),('Competition',value['competition'])]:
            text+='\n### '+label+'\n'
            for record in records:text+='- '+escaped(record['extract'])+' ['+escaped(record['id'])+']\n'
        for uncertainty in value['uncertainties']:text+='- Uncertainty: '+escaped(uncertainty)+'\n'
    text+='\n# Dated fictional industry conditions\n'
    for sector,result in report['market_research'].items():
        text+='\n## '+escaped(sector)+'\n'
        if result['status']!='success':
            text+='Source status: '+escaped(result['status'])+' — '+escaped(result['reason'])+'\n';continue
        value=result['value'];text+=escaped(value['conditions'])+'\n'
        text+='Scenario date: '+escaped(value['scenario_date'])+' (fictional).\n'
        for signal in value['signals']:
            text+='- '+escaped(signal['metric'])+': '+str(signal['value'])+' '+escaped(signal['unit'])
            text+='; '+escaped(signal['direction'])+' ['+escaped(signal['evidence']['id'])+']\n'
        for uncertainty in value['uncertainties']:text+='- Uncertainty: '+escaped(uncertainty)+'\n'
    return text


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output-dir',type=Path,required=True)
    args=parser.parse_args();report=make_report()
    args.output_dir.mkdir(parents=True,exist_ok=False)
    (args.output_dir/'report.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    (args.output_dir/'report.md').write_text(render(report))
    print(json.dumps({'status':'fictional report assembled after local source validation','schema_version':report['schema_version']}))
if __name__=='__main__':main()
