"""Typed deterministic agent-app factory; no model responses are simulated."""
from __future__ import annotations
import argparse
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

@dataclass(frozen=True)
class AgentSpec:
    name: str
    purpose: str
    users: tuple[str, ...]
    tools: tuple[str, ...]
    data: str
    output: str
    policies: tuple[str, ...]
    deployment: str = 'local'
    framework: str = 'stdlib'
    def validate(self):
        if not isinstance(self.name, str) or not re.fullmatch(r'[a-z][a-z0-9_]{2,39}',self.name):
            raise ValueError('name must be a safe Python module identifier')
        for value in (self.purpose,self.data,self.output):
            if not isinstance(value,str) or not value.strip() or len(value)>2000:
                raise ValueError('purpose, data and output require bounded text')
        for values in (self.users,self.tools,self.policies):
            if not isinstance(values,tuple) or not values or not all(isinstance(v,str) and v.strip() and len(v)<=2000 for v in values):
                raise ValueError('nonempty typed tuples required')
        if len(set(self.tools)) != len(self.tools) or not set(self.tools)<= {'word_count','uppercase'}:
            raise ValueError('unsupported or duplicate tool')
        if self.framework != 'stdlib' or self.deployment not in {'local','docker'}:
            raise ValueError('this executable adapter supports stdlib local/docker only')
    @classmethod
    def from_json(cls, value):
        if not isinstance(value,dict): raise ValueError('specification must be an object')
        required={'name','purpose','users','tools','data','output','policies'}
        allowed=required|{'deployment','framework'}
        if set(value)-allowed or required-set(value): raise ValueError('unexpected or missing specification fields')
        normalized=dict(value)
        for key in ('users','tools','policies'):
            if not isinstance(normalized[key],list): raise ValueError(key+' must be a JSON array')
            normalized[key]=tuple(normalized[key])
        spec=cls(**normalized); spec.validate(); return spec

def requirements(spec: AgentSpec):
    spec.validate()
    return {'purpose':spec.purpose, 'users':list(spec.users),
            'acceptance':[f'Tool {tool} accepts text and returns a JSON-serializable result' for tool in spec.tools],
            'constraints':list(spec.policies), 'framework':spec.framework,
            'architecture':['validated JSON input','allowlisted tool dispatcher','JSON output'],
            'limitations':['Deterministic template implementation; not an LLM reasoning agent.',
                           'No network integrations or untrusted-code execution are implemented.']}

APP = '''"""Generated deterministic agent: allowlisted typed tools only."""
import json
import sys
ALLOWED_TOOLS = __TOOLS__

def run(tool: str, text: str):
    if tool not in ALLOWED_TOOLS:
        raise ValueError("tool is not enabled")
    if not isinstance(text, str) or len(text) > 100000:
        raise ValueError("text must be a string of at most 100000 characters")
    if tool == "word_count": return {"words": len(text.split())}
    if tool == "uppercase": return {"text": text.upper()}
    raise ValueError("unsupported tool")

if __name__ == "__main__":
    request = json.load(sys.stdin)
    if not isinstance(request, dict) or set(request) != {"tool", "text"}:
        raise ValueError("expected exactly tool and text")
    print(json.dumps(run(request["tool"], request["text"])))
'''

def render(spec: AgentSpec):
    spec.validate()
    tools = repr(spec.tools)  # Only validated literal identifiers enter executable code.
    test_lines=['import unittest','from agent import run','class GeneratedTests(unittest.TestCase):']
    for tool in spec.tools:
        expected = "{'words': 2}" if tool=='word_count' else "{'text': 'HELLO ACADEMY'}"
        test_lines += [f'    def test_{tool}(self):',f'        self.assertEqual(run({tool!r}, "hello Academy"), {expected})']
    test_lines += ['    def test_forbidden_tool(self):','        with self.assertRaises(ValueError): run("shell", "ls")',
                  '    def test_wrong_input(self):',f'        with self.assertRaises(ValueError): run({spec.tools[0]!r}, 123)']
    return {
      'agent.py': APP.replace('__TOOLS__',tools),
      'test_agent.py':'\n'.join(test_lines)+'\n',
      'spec.json':json.dumps(asdict(spec),indent=2)+'\n',
      'requirements.json':json.dumps(requirements(spec),indent=2)+'\n',
      'instructions.md':f'# {spec.name}\n\nPurpose: {spec.purpose}\n\n'+ '\n'.join('- '+p for p in spec.policies)+'\n\nOnly use enabled tools. Request human approval before adding external mutations.\n',
      'README.md':f'# {spec.name}\n\n{spec.purpose}\n\nThis is the deterministic stdlib adapter, not an LLM transcript.\n\nRun `python -m unittest -v` and `python agent.py < request.json`.\nAll fixture data is local. No API key is needed.\nTo use Docker: `docker build -t academy-agent .` then `docker run --rm -i --network none --read-only --cap-drop ALL --security-opt no-new-privileges academy-agent < request.json`.\n',
      '.env.example':'# This offline adapter requires no API credentials.\n',
      'request.json':json.dumps({'tool':spec.tools[0],'text':'hello Academy'})+'\n',
      'Dockerfile':'FROM python:3.12-slim\nWORKDIR /app\nCOPY agent.py test_agent.py /app/\nRUN python -m unittest -v\nUSER 65534:65534\nENTRYPOINT ["python", "-B", "agent.py"]\n',
      '.dockerignore':'*\n!agent.py\n!test_agent.py\n!Dockerfile\n',
    }

def inspect_files(files):
    import ast
    expected={'agent.py','test_agent.py','spec.json','requirements.json','instructions.md','README.md','.env.example','request.json','Dockerfile','.dockerignore'}
    if set(files)!=expected: raise ValueError('generated artifact inventory changed')
    for name, data in files.items():
        if '/' in name or '\\' in name or not isinstance(data,str): raise ValueError('invalid artifact')
        if name.endswith('.py'): ast.parse(data, filename=name)
    # Review is a deterministic structural check, not a claimed model review.
    tree=ast.parse(files['agent.py'])
    imports={node.names[0].name for node in ast.walk(tree) if isinstance(node,ast.Import)}
    if imports != {'json','sys'}: raise ValueError('unexpected generated application import')
    if any(isinstance(node, ast.ImportFrom) for node in ast.walk(tree)):
        raise ValueError('unexpected generated application import')

def validate_generated(files):
    inspect_files(files)
    with tempfile.TemporaryDirectory(prefix='academy-factory-test-') as directory:
        root=Path(directory)
        for name,content in files.items(): (root/name).write_text(content)
        result=subprocess.run([sys.executable,'-I','-m','unittest','discover','-s',str(root),'-p','test_agent.py','-v'],
            cwd=root,capture_output=True,text=True,timeout=15,env={'PATH':'/usr/bin:/bin','PYTHONDONTWRITEBYTECODE':'1'})
        if result.returncode: raise ValueError('generated tests failed: '+result.stderr)
        return {'command':'python -I -m unittest discover', 'returncode':result.returncode,
                'stdout':result.stdout,'stderr':result.stderr,
                'isolation':'temporary working directory and isolated Python import mode; NOT an OS security sandbox'}

def build(spec: AgentSpec, destination: Path):
    files=render(spec); receipt=validate_generated(files)
    destination=destination.absolute()
    if destination.exists(): raise FileExistsError('choose a new output directory')
    destination.mkdir(parents=False)
    try:
        for name,content in files.items(): (destination/name).write_text(content)
        manifest={name:hashlib.sha256((destination/name).read_bytes()).hexdigest() for name in sorted(files)}
        receipt['sha256']=manifest
        (destination/'validation-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    except BaseException:
        # Keep partial files as failure evidence; never overwrite a prior project.
        raise
    return receipt

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('spec',type=Path); parser.add_argument('destination',type=Path)
    args=parser.parse_args()
    print(json.dumps(build(AgentSpec.from_json(json.loads(args.spec.read_text())),args.destination),indent=2))
