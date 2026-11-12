"""AUTHOR-ONLY unit suite: all providers/executors below are labelled doubles.

Central QA must run this suite and retain actual results. No test here contacts a
provider or executes model-generated code. Real Docker validation is separate.
"""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'projects/05-sandboxed-engineering/learning/semantic_team.py'
spec = importlib.util.spec_from_file_location('semantic_team_under_test', SOURCE)
team = importlib.util.module_from_spec(spec); spec.loader.exec_module(team)
GOOD = 'def total_expenses(amounts):\n    if any(type(x) is not int or x < 0 for x in amounts):\n        raise ValueError("invalid amount")\n    return sum(amounts)\n'
BAD = GOOD.replace('sum(amounts)', '(amounts[0] if amounts else 0)')
QA = 'import unittest\nfrom expense_app import total_expenses\nclass Extra(unittest.TestCase):\n    def test_pair(self): self.assertEqual(total_expenses([1, 2]), 3)\n'

class ProviderDouble:
    def __init__(self, initial=BAD, mutation=None): self.initial=initial; self.mutation=mutation; self.requests=[]
    def request(self, role, payload):
        self.requests.append((role, payload))
        stage = payload['stage']
        if stage == 'requirements': value = payload['schema']
        elif stage == 'architecture': value = payload['schema']
        elif stage == 'implementation':
            value = {'files': {'expense_app.py': self.initial, 'test_expense_app.py': QA, 'README.md': '# Expense app\n', 'requirements.txt': '# stdlib only\n'}}
        elif stage == 'test-plan': value = {'tests': QA, 'coverage': ['R1','R2','R3']}
        elif stage == 'review':
            receipt = payload['inputs']['tool_result']
            value = {'receipt_sha256': payload['inputs']['tool_result_sha256'], 'criteria': receipt['observations'],
                     'defects': [] if receipt['passed'] else ['R2 exact sum differs from expected result']}
        elif stage == 'repair':
            files = payload['inputs']['implementation']['content']
            value = {'base_sha256': team.sha(files), 'changes': {'expense_app.py': {'before_sha256': team.sha(files['expense_app.py']), 'after': GOOD}}, 'rationale': 'R2 observed 125 instead of400; replace first-element aggregation with sum'}
        else: raise AssertionError(stage)
        if self.mutation: value = self.mutation(stage, value)
        return {'role': role, 'input_sha256': team.sha(payload), 'request_id': 'TEST-DOUBLE-' + str(len(self.requests)),
                'model': 'NO-MODEL-OFFLINE-DOUBLE', 'raw': json.dumps(value), 'provenance': 'offline-test-double'}

class ExecutorDouble:
    """Returns canned receipt variants; NOT actual container execution."""
    def __init__(self, force_fail=False, corrupt=None): self.calls=[]; self.force_fail=force_fail; self.corrupt=corrupt
    def execute(self, files, qa_tests, acceptance_tests):
        self.calls.append((files, qa_tests, acceptance_tests))
        passed = files['expense_app.py'] == GOOD and not self.force_fail
        receipt = {'execution': 'inside-owned-container', 'source_sha256': team.sha(files),
                   'acceptance_sha256': team.sha(acceptance_tests), 'qa_tests_sha256': team.sha(qa_tests),
                   'passed': passed, 'returncode': 0 if passed else 1, 'timed_out': False, 'truncated': False,
                   'stdout': 'UNIT-TEST-DOUBLE: not actual execution', 'stderr': '',
                   'observations': {'R1': True,'R2': passed,'R3': True},
                   'argv': ['UNIT-TEST-DOUBLE'], 'cleanup_confirmed': True}
        if self.corrupt: self.corrupt(receipt)
        return receipt

class SemanticTests(unittest.TestCase):
    def run_case(self, provider=None, executor=None, maximum=2, offline=True):
        with tempfile.TemporaryDirectory() as temp:
            store = team.EvidenceStore(Path(temp))
            p=provider or ProviderDouble(); e=executor or ExecutorDouble()
            result = team.run_team(p,e,store,{'title':'Expense calculator','product_request':'Total nonnegative integer minor units'},max_repairs=maximum,allow_offline=offline)
            evidence = [(path.name,json.loads(path.read_text())) for path in sorted(Path(temp).glob('*.json'))]
            return result,p,e,evidence
    def test_all_roles_typed_and_tool_failure_routes_back(self):
        result,p,e,evidence = self.run_case()
        self.assertTrue(result['passed']); self.assertEqual(result['status'],'OFFLINE_TEST_DOUBLE_PASS')
        self.assertEqual(len(e.calls),2); self.assertEqual(len(p.requests),7)
        self.assertFalse(result['attempts'][0]['receipt']['passed'])
        self.assertTrue(result['attempts'][1]['receipt']['passed'])
        repair = next(payload for role,payload in p.requests if payload['stage']=='repair')
        self.assertEqual(repair['inputs']['actual_failure']['observations']['R2'],False)
        self.assertEqual(repair['inputs']['qa_review']['criteria']['R2'],False)
        self.assertEqual(e.calls[0][1:],e.calls[1][1:])  # unchanged QA/course suites
        for artifact in result['artifacts'].values():
            self.assertEqual(artifact['content_sha256'],team.sha(artifact['content']))
        self.assertTrue(any('patch' in name for name,value in evidence))
    def test_default_rejects_fixture_as_actual(self):
        with self.assertRaises(ValueError): self.run_case(offline=False)
    def test_no_failure_needs_no_repair(self):
        result,p,e,_=self.run_case(provider=ProviderDouble(initial=GOOD))
        self.assertTrue(result['passed']); self.assertEqual(len(p.requests),5); self.assertEqual(len(e.calls),1)
    def test_zero_budget_preserves_unresolved(self):
        result,p,e,evidence=self.run_case(maximum=0)
        self.assertFalse(result['passed']); self.assertEqual(result['status'],'UNRESOLVED_REPAIR_BUDGET')
        self.assertEqual(len(e.calls),1); self.assertEqual(len(p.requests),5)
        self.assertTrue(any('unresolved' in name for name,value in evidence))
    def test_test_changes_and_extra_files_forbidden(self):
        def mutate(stage,value):
            if stage=='repair': value['changes']['test_expense_app.py']={'before_sha256':'0'*64,'after':'pass'}
            return value
        with self.assertRaises(ValueError): self.run_case(provider=ProviderDouble(mutation=mutate))
    def test_stale_patch_refused(self):
        def mutate(stage,value):
            if stage=='repair': value['base_sha256']='0'*64
            return value
        with self.assertRaises(ValueError): self.run_case(provider=ProviderDouble(mutation=mutate))
    def test_repeat_source_refused(self):
        def mutate(stage,value):
            if stage=='repair': value['changes']['expense_app.py']['after']=BAD
            return value
        with self.assertRaises(ValueError): self.run_case(provider=ProviderDouble(mutation=mutate))
    def test_stale_architecture_refused(self):
        def mutate(stage,value):
            if stage=='architecture': value['requirements_sha256']='0'*64
            return value
        with self.assertRaises(ValueError): self.run_case(provider=ProviderDouble(mutation=mutate))
    def test_unapproved_dependency_refused(self):
        def mutate(stage,value):
            if stage=='architecture': value['dependencies']=['surprise==1']
            return value
        with self.assertRaises(ValueError): self.run_case(provider=ProviderDouble(mutation=mutate))
    def test_missing_priority_refused(self):
        def mutate(stage,value):
            if stage=='requirements': del value['priorities']
            return value
        with self.assertRaises(ValueError): self.run_case(provider=ProviderDouble(mutation=mutate))
    def test_model_cannot_override_actual_tool_observations(self):
        def mutate(stage,value):
            if stage=='review': value['criteria']={'R1':True,'R2':True,'R3':True};value['defects']=[]
            return value
        with self.assertRaises(ValueError): self.run_case(provider=ProviderDouble(mutation=mutate))
    def test_model_review_must_reference_current_receipt(self):
        def mutate(stage,value):
            if stage=='review': value['receipt_sha256']='0'*64
            return value
        with self.assertRaises(ValueError): self.run_case(provider=ProviderDouble(mutation=mutate))
    def test_execution_bound_to_exact_source(self):
        with self.assertRaises(ValueError): self.run_case(executor=ExecutorDouble(corrupt=lambda r:r.update(source_sha256='0'*64)))
    def test_contradictory_success_refused(self):
        with self.assertRaises(ValueError): self.run_case(executor=ExecutorDouble(corrupt=lambda r:r.update(passed=True)))
    def test_missing_cleanup_not_pass(self):
        with self.assertRaises(ValueError): self.run_case(provider=ProviderDouble(initial=GOOD),executor=ExecutorDouble(corrupt=lambda r:r.update(cleanup_confirmed=False)))
    def test_raw_failure_evidence_retained(self):
        def mutate(stage,value):
            if stage=='requirements': value['revision']=99
            return value
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                team.run_team(ProviderDouble(mutation=mutate),ExecutorDouble(),team.EvidenceStore(Path(temp)),
                    {'title':'Expense','product_request':'Integer minor amounts'},allow_offline=True)
            names=[p.name for p in Path(temp).glob('*.json')]
            self.assertTrue(any('response-requirements' in name for name in names))
            self.assertTrue(any('stopped-error' in name for name in names))
    def test_duplicate_json_rejected(self):
        with self.assertRaises(ValueError): team.parse('{"a":1,"a":2}')
    def test_artifact_content_or_revision_tamper(self):
        artifact=team.envelope('architect',1,{'x':1},'a'*64)
        artifact['content']['x']=2
        with self.assertRaises(ValueError): team.consume(artifact,'architect',1)
    def test_invalid_budget(self):
        for maximum in (-1,3,True):
            with self.assertRaises(ValueError): self.run_case(maximum=maximum)

if __name__=='__main__':unittest.main()
