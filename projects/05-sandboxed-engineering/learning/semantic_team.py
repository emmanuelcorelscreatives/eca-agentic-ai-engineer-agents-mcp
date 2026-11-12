"""Versioned four-role engineering flow with real tool-feedback repair.

Authoring implementation: runtime approval requires independent tests, actual
provider responses and an observed container run. Test doubles are opt-in and
can never produce a live-completion status. No provider/host code runs on import.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re

ROLES = ('product_manager', 'architect', 'developer', 'quality_assurance')
FILES = {'expense_app.py', 'test_expense_app.py', 'README.md', 'requirements.txt'}
CRITERIA = {'R1', 'R2', 'R3'}
ACCEPTANCE_TESTS = '''import unittest
from expense_app import total_expenses
class CourseAcceptance(unittest.TestCase):
    def test_empty(self): self.assertEqual(total_expenses([]), 0)
    def test_zero(self): self.assertEqual(total_expenses([0]), 0)
    def test_sum(self): self.assertEqual(total_expenses([125, 275]), 400)
    def test_negative(self):
        with self.assertRaises(ValueError): total_expenses([-1])
    def test_decimal(self):
        with self.assertRaises(ValueError): total_expenses([1.5])
    def test_bool(self):
        with self.assertRaises(ValueError): total_expenses([True])
'''


def sha(value):
    """Canonical JSON hash, including scalar strings; shared by broker/tools."""
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def closed(value, keys):
    if not isinstance(value, dict) or set(value) != set(keys):
        raise ValueError('closed schema mismatch: expected ' + ','.join(sorted(keys)))


def text(value, maximum=10000):
    if not isinstance(value, str) or not value.strip() or len(value.encode()) > maximum:
        raise ValueError('bounded nonempty text required')
    return value


def parse(raw):
    text(raw, 50000)
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result: raise ValueError('duplicate JSON key')
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError('nonfinite JSON')))


class EvidenceStore:
    """Exclusive append-only evidence in an operator-owned fresh directory."""
    def __init__(self, root):
        self.root = Path(root)
        if self.root.is_symlink() or self.root.absolute() != self.root.resolve(strict=True):
            raise ValueError('canonical evidence directory required')
        if not self.root.is_dir(): raise ValueError('evidence directory missing')
        self.sequence = 0
    def record(self, label, value):
        if not re.fullmatch(r'[a-z0-9-]{1,80}', label): raise ValueError('invalid evidence label')
        # Exclusive creation prevents accidentally reusing/replacing past receipts.
        self.sequence += 1
        payload = json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + '\n'
        with (self.root / f'{self.sequence:03d}-{label}.json').open('x', encoding='utf-8') as handle:
            handle.write(payload); handle.flush()
            import os
            os.fsync(handle.fileno())
        return sha(value)


def validate_requirements(value):
    closed(value, {'revision', 'stories', 'criteria', 'priorities'})
    if value['revision'] != 1 or type(value['revision']) is not int: raise ValueError('requirements revision')
    if not isinstance(value['stories'], list) or not value['stories']: raise ValueError('stories missing')
    story_ids = set()
    for story in value['stories']:
        closed(story, {'id', 'text'})
        if not re.fullmatch(r'S[1-9][0-9]*', text(story['id'], 12)) or story['id'] in story_ids:
            raise ValueError('story ID')
        story_ids.add(story['id']); text(story['text'])
    if not isinstance(value['criteria'], dict) or set(value['criteria']) != CRITERIA:
        raise ValueError('R1-empty, R2-exact-sum, R3-invalid-input required')
    for criterion in value['criteria'].values():
        closed(criterion, {'story_id', 'description', 'priority'})
        if criterion['story_id'] not in story_ids: raise ValueError('unknown story')
        text(criterion['description'])
        if type(criterion['priority']) is not int or not 1 <= criterion['priority'] <= 3:
            raise ValueError('priority 1..3')
    if not isinstance(value['priorities'], list) or len(value['priorities']) != 3 or set(value['priorities']) != CRITERIA:
        raise ValueError('ordered priorities must cover all criteria exactly once')
    return value


def validate_architecture(value, requirements):
    closed(value, {'requirements_sha256', 'components', 'data_flows', 'implementation_plan', 'dependencies'})
    if value['requirements_sha256'] != sha(requirements): raise ValueError('stale requirements')
    if value['dependencies'] != []: raise ValueError('standard-library expense app only')
    if not isinstance(value['components'], list) or not value['components']: raise ValueError('components required')
    coverage = set()
    for component in value['components']:
        closed(component, {'path', 'interface', 'criteria'})
        if component['path'] != 'expense_app.py': raise ValueError('only approved app path')
        text(component['interface'])
        if not isinstance(component['criteria'], list) or not set(component['criteria']) <= CRITERIA:
            raise ValueError('unknown criterion')
        coverage.update(component['criteria'])
    if coverage != CRITERIA: raise ValueError('uncovered requirement')
    for key in ('data_flows', 'implementation_plan'):
        if not isinstance(value[key], list) or not value[key]: raise ValueError(key + ' required')
        for line in value[key]: text(line)
    return value


def validate_files(value):
    if not isinstance(value, dict) or set(value) != FILES: raise ValueError('exact four delivery files required')
    for name, content in value.items():
        if not isinstance(content, str) or len(content.encode()) > 50000: raise ValueError('bounded text files')
        if '\x00' in content: raise ValueError('NUL in source')
    for line in value['requirements.txt'].splitlines():
        if line.strip() and not line.lstrip().startswith('#'): raise ValueError('dependency addition forbidden')
    # Parse/compile only: generated Python is never executed in this process.
    for name in ('expense_app.py', 'test_expense_app.py'): compile(value[name], name, 'exec')
    if 'total_expenses' not in value['expense_app.py']: raise ValueError('required function absent')
    return value


def envelope(role, revision, content, response_sha256):
    return {'schema_version': 1, 'role': role, 'revision': revision,
            'content_sha256': sha(content), 'response_sha256': response_sha256, 'content': content}


def consume(artifact, role, revision):
    closed(artifact, {'schema_version', 'role', 'revision', 'content_sha256', 'response_sha256', 'content'})
    if artifact['schema_version'] != 1 or artifact['role'] != role or artifact['revision'] != revision:
        raise ValueError('stale/incorrect handoff')
    if artifact['content_sha256'] != sha(artifact['content']): raise ValueError('corrupt handoff')
    if not re.fullmatch(r'[a-f0-9]{64}', artifact['response_sha256']): raise ValueError('missing producer evidence')
    return artifact['content']


def validate_receipt(receipt, files, qa_tests):
    needed = {'execution', 'source_sha256', 'acceptance_sha256', 'qa_tests_sha256', 'passed',
              'returncode', 'timed_out', 'truncated', 'stdout', 'stderr', 'observations',
              'argv', 'cleanup_confirmed'}
    if not isinstance(receipt, dict) or not needed <= set(receipt): raise ValueError('test receipt incomplete')
    if receipt['execution'] != 'inside-owned-container': raise ValueError('generated code requires owned container')
    if receipt['source_sha256'] != sha(files) or receipt['acceptance_sha256'] != sha(ACCEPTANCE_TESTS) or receipt['qa_tests_sha256'] != sha(qa_tests):
        raise ValueError('stale test inputs')
    for key in ('passed', 'timed_out', 'truncated', 'cleanup_confirmed'):
        if type(receipt[key]) is not bool: raise ValueError('test status must be boolean')
    if receipt['returncode'] is not None and type(receipt['returncode']) is not int: raise ValueError('exit code type')
    if not isinstance(receipt['argv'], list) or not receipt['argv'] or any(not isinstance(x, str) for x in receipt['argv']):
        raise ValueError('actual argv missing')
    for key in ('stdout', 'stderr'):
        if not isinstance(receipt[key], str) or len(receipt[key].encode()) > 65536: raise ValueError('bounded test logs')
    if not isinstance(receipt['observations'], dict) or set(receipt['observations']) != CRITERIA or any(type(x) is not bool for x in receipt['observations'].values()):
        raise ValueError('criterion observations required')
    effective_pass = (receipt['returncode'] == 0 and not receipt['timed_out'] and not receipt['truncated']
                      and receipt['cleanup_confirmed'] and all(receipt['observations'].values()))
    if receipt['passed'] != effective_pass: raise ValueError('contradictory test result')
    return receipt


def run_team(provider, executor, evidence_store, request, max_repairs=2, allow_offline=False):
    """All four roles and repair orchestration execute in the caller's container.

    Provider broker transports only bounded role prompts/responses; it must not
    expose a host shell, Docker socket, filesystem tools, credentials or egress.
    executor is the privileged fixed test capability, never a model tool result.
    On any exception, append the failure and re-raise without deleting evidence.
    """
    closed(request, {'title', 'product_request'})
    text(request['title'], 120); text(request['product_request'])
    if type(max_repairs) is not int or not 0 <= max_repairs <= 2: raise ValueError('maximum two repairs')
    if type(allow_offline) is not bool: raise ValueError('offline flag')
    seen_requests, calls, artifacts, attempts = set(), [], {}, []
    used_fixture = False
    def ask(role, stage, inputs, schema):
        nonlocal used_fixture
        if len(calls) >= 5 + 2 * max_repairs: raise ValueError('provider call budget exhausted')
        payload = {'stage': stage, 'request': request, 'inputs': inputs, 'schema': schema,
                   'ordinal': len(calls) + 1, 'policy': 'expense app only; no network/files/process calls; integer minor units; preserve acceptance suite'}
        evidence_store.record('request-' + stage, {'role': role, 'payload': payload, 'input_sha256': sha(payload)})
        response = provider.request(role, payload)
        # Store raw response BEFORE parsing so every malformed/failed attempt survives.
        response_hash = evidence_store.record('response-' + stage, response)
        closed(response, {'role', 'input_sha256', 'request_id', 'model', 'raw', 'provenance'})
        if response['role'] != role or response['input_sha256'] != sha(payload): raise ValueError('wrong response binding')
        text(response['request_id'], 200); text(response['model'], 200)
        if response['request_id'] in seen_requests: raise ValueError('reused provider request ID')
        seen_requests.add(response['request_id'])
        if response['provenance'] == 'offline-test-double' and allow_offline: used_fixture = True
        elif response['provenance'] != 'actual-provider-response': raise ValueError('actual provider response required')
        calls.append({'role': role, 'stage': stage, 'request_id': response['request_id'], 'response_sha256': response_hash})
        return parse(response['raw']), response_hash
    try:
        pm, proof = ask('product_manager', 'requirements', {},
                        {'revision': 1, 'stories': [{'id': 'S1', 'text': 'user story'}],
                         'criteria': {key: {'story_id': 'S1', 'description': description, 'priority': 1} for key, description in
                                      [('R1', 'empty input returns zero'), ('R2', '125+275 returns400'), ('R3', 'reject negative/decimal/bool')]},
                         'priorities': ['R1', 'R2', 'R3']})
        artifacts['requirements'] = envelope('product_manager', 1, validate_requirements(pm), proof)
        req = consume(artifacts['requirements'], 'product_manager', 1)
        arch, proof = ask('architect', 'architecture', {'requirements': artifacts['requirements']},
                          {'requirements_sha256': sha(req), 'components': [{'path': 'expense_app.py', 'interface': 'total_expenses(amounts)', 'criteria': ['R1','R2','R3']}],
                           'data_flows': ['input minor units to validator to total'], 'implementation_plan': ['implement and test'], 'dependencies': []})
        artifacts['architecture'] = envelope('architect', 1, validate_architecture(arch, req), proof)
        consume(artifacts['architecture'], 'architect', 1)
        dev, proof = ask('developer', 'implementation', {'requirements': artifacts['requirements'], 'architecture': artifacts['architecture']},
                         {'files': {name: 'complete source or documentation' for name in sorted(FILES)}})
        closed(dev, {'files'}); files = validate_files(dev['files'])
        artifacts['implementation'] = envelope('developer', 1, files, proof)
        consume(artifacts['implementation'], 'developer', 1)
        qa_plan, proof = ask('quality_assurance', 'test-plan', {'requirements': artifacts['requirements'], 'architecture': artifacts['architecture'], 'implementation': artifacts['implementation']},
                             {'tests': 'unittest Python source; import expense_app; no code execution claims', 'coverage': ['R1','R2','R3']})
        closed(qa_plan, {'tests', 'coverage'}); text(qa_plan['tests'], 20000)
        if not isinstance(qa_plan['coverage'], list) or set(qa_plan['coverage']) != CRITERIA: raise ValueError('QA plan incomplete')
        compile(qa_plan['tests'], 'test_qa_generated.py', 'exec')
        artifacts['qa_plan'] = envelope('quality_assurance', 1, qa_plan, proof)
        seen_sources = {sha(files)}
        for attempt in range(max_repairs + 1):
            # Fixed course suite and the QA-generated suite are read-only inputs.
            receipt = executor.execute(dict(files), qa_plan['tests'], ACCEPTANCE_TESTS)
            receipt_sha = evidence_store.record('execution-' + str(attempt), receipt)
            validate_receipt(receipt, files, qa_plan['tests'])
            attempts.append({'attempt': attempt, 'source_sha256': sha(files), 'receipt_sha256': receipt_sha, 'receipt': receipt})
            review, proof = ask('quality_assurance', 'review', {'requirements': artifacts['requirements'], 'implementation': artifacts['implementation'],
                                     'tool_result': receipt, 'tool_result_sha256': receipt_sha},
                                {'receipt_sha256': receipt_sha, 'criteria': {'R1': False, 'R2': False, 'R3': False}, 'defects': ['observed defect with criterion ID']})
            closed(review, {'receipt_sha256', 'criteria', 'defects'})
            if review['receipt_sha256'] != receipt_sha or not isinstance(review['criteria'], dict) or set(review['criteria']) != CRITERIA:
                raise ValueError('QA review not bound to actual execution')
            if any(type(x) is not bool for x in review['criteria'].values()): raise ValueError('criterion status')
            if not isinstance(review['defects'], list) or any(not isinstance(x, str) for x in review['defects']): raise ValueError('defect list')
            if review['criteria'] != receipt['observations']: raise ValueError('QA cannot override actual observations')
            evidence_store.record('review-' + str(attempt), {'review': review, 'response_sha256': proof})
            if receipt['passed'] and not review['defects']:
                result = {'passed': True, 'status': 'OFFLINE_TEST_DOUBLE_PASS' if used_fixture else 'ACTUAL_TEAM_RUN_AWAITING_INDEPENDENT_ACCEPTANCE',
                          'artifacts': artifacts, 'files': files, 'attempts': attempts, 'calls': calls,
                          'acceptance_matrix': {key: {'passed': True, 'receipt_sha256': receipt_sha} for key in sorted(CRITERIA)}}
                evidence_store.record('completion', result); return result
            if attempt == max_repairs: break
            patch, proof = ask('developer', 'repair', {'requirements': artifacts['requirements'], 'architecture': artifacts['architecture'],
                                     'implementation': artifacts['implementation'], 'actual_failure': receipt, 'qa_review': review},
                                {'base_sha256': sha(files), 'changes': {'expense_app.py': {'before_sha256': sha(files['expense_app.py']), 'after': 'complete minimally repaired source'}},
                                 'rationale': 'cite actual failure and criterion; do not change tests/docs/dependencies'})
            closed(patch, {'base_sha256', 'changes', 'rationale'}); text(patch['rationale'])
            if patch['base_sha256'] != sha(files) or set(patch['changes']) != {'expense_app.py'}: raise ValueError('repair scope/base mismatch')
            change = patch['changes']['expense_app.py']; closed(change, {'before_sha256', 'after'})
            if change['before_sha256'] != sha(files['expense_app.py']): raise ValueError('stale repair')
            text(change['after'], 50000)
            revised = validate_files({**files, 'expense_app.py': change['after']})
            if sha(revised) in seen_sources: raise ValueError('repeated unchanged repair')
            evidence_store.record('patch-' + str(attempt), {'patch': patch, 'response_sha256': proof,
                                    'before': files, 'after': revised, 'retained_failure_sha256': receipt_sha})
            seen_sources.add(sha(revised)); files = revised
            artifacts['implementation'] = envelope('developer', attempt + 2, files, proof)
            consume(artifacts['implementation'], 'developer', attempt + 2)
        result = {'passed': False, 'status': 'UNRESOLVED_REPAIR_BUDGET', 'artifacts': artifacts, 'files': files, 'attempts': attempts, 'calls': calls}
        evidence_store.record('unresolved', result); return result
    except Exception as exc:
        evidence_store.record('stopped-error', {'error_type': type(exc).__name__, 'message': str(exc), 'artifacts': artifacts, 'attempts': attempts, 'calls': calls})
        raise
