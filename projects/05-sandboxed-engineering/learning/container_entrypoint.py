"""All four roles and their repair loop execute here, inside the owned container."""
from __future__ import annotations
import hashlib
import json
import os
import sys
from pathlib import Path
import signal
import subprocess
import tempfile
import time
import uuid

from container_launch import canonical, read_json, write_json


class MailboxProvider:
    def __init__(self, root=Path('/mailbox'), max_calls=9):
        if type(max_calls) is not int or not 5 <= max_calls <= 9: raise ValueError('invalid budget')
        self.root = root
        self.calls = 0
        self.max_calls = max_calls

    def request(self, role, payload):
        if self.calls >= self.max_calls: raise ValueError('model budget exhausted')
        self.calls += 1
        request = {'schema': 1, 'role': role, 'payload': payload,
                   'input_sha': hashlib.sha256(canonical(payload)).hexdigest(), 'ordinal': self.calls}
        request['request_sha'] = hashlib.sha256(canonical(request)).hexdigest()
        write_json(self.root / ('request-%02d.json' % self.calls), request)
        deadline = time.monotonic() + 70
        response_path = self.root / ('response-%02d.json' % self.calls)
        while not response_path.exists():
            if time.monotonic() > deadline: raise TimeoutError('provider outcome uncertain; no automatic retry')
            time.sleep(0.05)
        response = read_json(response_path)
        if set(response) != {'request_sha', 'response'} or response['request_sha'] != request['request_sha']:
            raise ValueError('response binding mismatch')
        envelope = response['response']
        keys = {'role', 'input_sha256', 'request_id', 'model', 'raw', 'provenance'}
        if not isinstance(envelope, dict) or set(envelope) != keys:
            raise ValueError('actual model envelope required')
        if envelope['role'] != role or envelope['input_sha256'] != request['input_sha']:
            raise ValueError('provider response source mismatch')
        if envelope['provenance'] != 'actual-provider-response':
            raise ValueError('production container refuses test doubles')
        return envelope


class InsideContainerExecutor:
    """Generated programs run only as bounded children of this container.

    Test modules are copied from the team contract, not accepted from developer
    replacements. No host command, Docker socket or network path is available.
    """
    def execute(self, files, qa_tests, acceptance_tests):
        from semantic_team import sha
        allowed = {'expense_app.py', 'test_expense_app.py', 'README.md', 'requirements.txt'}
        if set(files) != allowed or any(not isinstance(v, str) or len(v.encode()) > 65536 for v in files.values()):
            raise ValueError('generated source scope or quota')
        if files['requirements.txt'].strip() and any(
                line.strip() and not line.lstrip().startswith('#') for line in files['requirements.txt'].splitlines()):
            raise ValueError('offline standard-library application only')
        for source in (qa_tests, acceptance_tests):
            if not isinstance(source, str) or len(source.encode()) > 65536: raise ValueError('test quota')
        folder = Path('/work') / ('execution-' + uuid.uuid4().hex)
        folder.mkdir(mode=0o755)
        for name, body in files.items(): (folder / name).write_text(body)
        (folder / 'test_course_acceptance.py').write_text(acceptance_tests)
        (folder / 'test_independent_qa.py').write_text(qa_tests)
        for path in folder.iterdir(): path.chmod(0o444)
        folder.chmod(0o555)
        runner = '''import os,sys,unittest,json
sys.path.insert(0,os.getcwd())
class Observed(unittest.TextTestResult):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.success_ids=[]
        self.observed=[]
    def addSuccess(self,test):
        self.success_ids.append(test.id())
        self.observed.append({'id':test.id(),'status':'PASS'})
        super().addSuccess(test)
    def addFailure(self,test,err):
        self.observed.append({'id':test.id(),'status':'FAIL'})
        super().addFailure(test,err)
    def addError(self,test,err):
        self.observed.append({'id':test.id(),'status':'ERROR'})
        super().addError(test,err)
    def addSkip(self,test,reason):
        self.observed.append({'id':test.id(),'status':'SKIP'})
        super().addSkip(test,reason)
suite=unittest.defaultTestLoader.discover('.',pattern='test_*.py')
result=unittest.TextTestRunner(verbosity=2,resultclass=Observed).run(suite)
print(json.dumps({'testsRun':result.testsRun,'passed':result.wasSuccessful(),'success_ids':result.success_ids,'tests':result.observed}))
sys.exit(0 if result.wasSuccessful() and result.testsRun>0 else 1)
'''
        argv = [sys.executable, '-B', '-I', '-c', runner]
        receipt = {'execution': 'inside-owned-container', 'source_sha256': sha(files),
                   'acceptance_sha256': sha(acceptance_tests), 'qa_tests_sha256': sha(qa_tests),
                   'passed': False, 'returncode': None, 'timed_out': False, 'truncated': False,
                   'stdout': '', 'stderr': '', 'observations': {'R1': False, 'R2': False, 'R3': False},
                   'argv': argv, 'cleanup_confirmed': False}
        def limits():
            import resource
            os.setsid()
            resource.setrlimit(resource.RLIMIT_FSIZE, (16384, 16384))
            resource.setrlimit(resource.RLIMIT_CPU, (10, 10))
            resource.setrlimit(resource.RLIMIT_NOFILE, (32, 32))
            # Crew/evidence remain root-owned; generated children cannot write
            # their mailbox or replace immutable tests/source on disk.
            os.setgroups([])
            os.setgid(65534)
            os.setuid(65534)
        with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
            child = subprocess.Popen(argv, cwd=folder, env={'PATH': os.defpath, 'HOME': '/tmp'},
                                     stdout=out, stderr=err, preexec_fn=limits)
            try:
                receipt['returncode'] = child.wait(timeout=15)
            except subprocess.TimeoutExpired:
                receipt['timed_out'] = True
            finally:
                # Kill the child's entire process group, including background
                # descendants, even after its parent exits normally.
                try: os.killpg(child.pid, signal.SIGKILL)
                except ProcessLookupError: pass
                child.wait(timeout=5)
                receipt['cleanup_confirmed'] = True
            for key, handle in (('stdout', out), ('stderr', err)):
                handle.seek(0)
                raw = handle.read(16385)
                receipt[key] = raw[:16384].decode(errors='replace')
                receipt['truncated'] |= len(raw) >= 16384
        # Exit zero alone is insufficient: an imported program could call exit
        # before the runner executes. Require the actual runner's bounded report.
        try: summary = json.loads(receipt['stdout'].strip().splitlines()[-1])
        except (ValueError, IndexError): summary = {}
        observed = summary.get('success_ids', [])
        if not isinstance(observed, list) or any(not isinstance(v, str) for v in observed): observed = []
        prefix = 'test_course_acceptance.CourseAcceptance.'
        groups = {'R1': ('test_empty', 'test_zero'), 'R2': ('test_sum',),
                  'R3': ('test_negative', 'test_decimal', 'test_bool')}
        tests = summary.get('tests', [])
        if not isinstance(tests, list) or len(tests) > 256: tests = []
        receipt['tests'] = []
        for test in tests:
            if not isinstance(test, dict) or set(test) != {'id', 'status'}: continue
            if not isinstance(test['id'], str) or test['status'] not in ('PASS', 'FAIL', 'ERROR', 'SKIP'): continue
            criterion = next((key for key, names in groups.items()
                              if test['id'] in {prefix + name for name in names}), None)
            receipt['tests'].append({**test, 'criterion': criterion})
        receipt['observations'] = {key: all(prefix + name in observed for name in names)
                                   for key, names in groups.items()}
        receipt['passed'] = (receipt['returncode'] == 0 and not receipt['timed_out']
                             and not receipt['truncated'] and summary.get('passed') is True
                             and type(summary.get('testsRun')) is int and summary['testsRun'] >= 6
                             and all(receipt['observations'].values()))
        return receipt


def main():
    from semantic_team import EvidenceStore, run_team
    # Actual CrewAI Agent/Task/Crew orchestration is the default runtime route.
    # Import is lazy so schema/file-only tests do not imply an SDK run.
    from crewai_roles import CrewAIRoleProvider
    request = read_json(Path('/inputs/request.json'))
    if set(request) != {'title', 'product_request'}: raise ValueError('request schema')
    evidence = Path('/mailbox/evidence')
    evidence.mkdir(mode=0o700)
    evidence_store = EvidenceStore(evidence)
    provider = CrewAIRoleProvider(MailboxProvider(), evidence_store)
    result = run_team(provider, InsideContainerExecutor(), evidence_store,
                      request, max_repairs=2, allow_offline=False)
    write_json(Path('/mailbox/result.json'), result)
    if result.get('passed') is True:
        from delivery_package import package_delivery
        delivery = package_delivery(result, Path('/mailbox/delivery.zip'), evidence)
        write_json(Path('/mailbox/delivery-receipt.json'), delivery)


if __name__ == '__main__':
    main()
