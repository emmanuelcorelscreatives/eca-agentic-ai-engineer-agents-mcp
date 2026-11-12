"""Actual factory engineering exercises; no invented model or Docker results."""
import argparse
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'projects/07-agent-factory/factory.py'
spec=importlib.util.spec_from_file_location('s25_factory',path)
factory=importlib.util.module_from_spec(spec);sys.modules[spec.name]=factory;spec.loader.exec_module(factory)

def run_case(case):
    sample=json.loads((path.parent/'examples/text_helper.json').read_text())
    if case=='schema':
        valid=factory.AgentSpec.from_json(sample)
        refused=[]
        for field,value in [('name','../../escape'),('tools',['shell']),('framework','imaginary')]:
            invalid={**sample,field:value}
            try:factory.AgentSpec.from_json(invalid)
            except ValueError:refused.append(field)
        assert len(refused)==3
        return {'status':'passed','normalized_name':valid.name,'rejected_fields':refused}
    if case=='generate':
        with tempfile.TemporaryDirectory(prefix='academy-s25-') as directory:
            receipt=factory.build(factory.AgentSpec.from_json(sample),Path(directory)/'generated')
            assert receipt['returncode']==0
            return {'status':'passed','test_output':receipt['stderr'],'artifact_sha256':receipt['sha256']}
    if case=='review':
        files=factory.render(factory.AgentSpec.from_json(sample));factory.inspect_files(files)
        files['agent.py']='import os\n'
        try:factory.inspect_files(files)
        except ValueError as error:return {'status':'passed','observation':'unsupported generated import rejected','reason':str(error)}
        raise AssertionError('unsupported import was accepted')
    if case=='failure':
        files=factory.render(factory.AgentSpec.from_json(sample));files['test_agent.py']='raise RuntimeError("seeded failing test")\n'
        try:factory.validate_generated(files)
        except ValueError as error:return {'status':'passed','observation':'actual failed subprocess preserved as failure','diagnostic':str(error)}
        raise AssertionError('test failure was promoted to success')
    raise ValueError('unknown case')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('case',choices=['schema','generate','review','failure'])
    print(json.dumps(run_case(parser.parse_args().case),indent=2))
