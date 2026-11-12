"""Typed four-role handoffs and bounded repair; fixtures are not model outputs."""
from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
import re

ROLES = ('product_manager', 'architect', 'developer', 'quality_assurance')

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()

def safe_source(path):
    if not isinstance(path, str) or not re.fullmatch(r'src/[a-zA-Z0-9_/]+\.py', path) or '..' in path:
        raise ValueError('implementation path outside src')

def requirements(value):
    if set(value) != {'revision', 'stories', 'criteria'} or type(value['revision']) is not int or value['revision'] < 1:
        raise ValueError('requirements schema')
    if not value['stories'] or not all(isinstance(x, str) and x.strip() for x in value['stories']):
        raise ValueError('stories required')
    if not isinstance(value['criteria'], dict) or not value['criteria']:
        raise ValueError('measurable acceptance criteria required')
    for key, text in value['criteria'].items():
        if not re.fullmatch(r'R[1-9][0-9]*', key) or not isinstance(text, str) or not text.strip():
            raise ValueError('invalid criterion')
    return value

def architecture(value, approved_requirements):
    requirements(approved_requirements)
    if set(value) != {'requirements_sha256', 'modules', 'dependencies'}:
        raise ValueError('architecture schema')
    if value['requirements_sha256'] != digest(approved_requirements): raise ValueError('stale requirements')
    if not isinstance(value['modules'], list) or not value['modules']: raise ValueError('modules required')
    covered = set()
    for module in value['modules']:
        if set(module) != {'path', 'interface', 'requirements'}: raise ValueError('module schema')
        safe_source(module['path'])
        if not isinstance(module['interface'], str) or not module['interface'].strip(): raise ValueError('interface absent')
        if not module['requirements'] or not set(module['requirements']) <= set(approved_requirements['criteria']):
            raise ValueError('unknown requirement reference')
        covered.update(module['requirements'])
    if covered != set(approved_requirements['criteria']): raise ValueError('uncovered requirement')
    # This reviewed expense app needs standard library only. New dependency
    # proposals require a separately reviewed policy and lockfile, never auto-install.
    if value['dependencies'] != []: raise ValueError('unapproved dependency')
    return value

@dataclass(frozen=True)
class Envelope:
    version: int
    role: str
    revision: int
    content: dict
    sha256: str
    provenance: str
    def validate(self, expected_role, expected_revision):
        if self.version != 1 or self.role != expected_role or self.role not in ROLES:
            raise ValueError('handoff role/version mismatch')
        if type(self.revision) is not int or self.revision != expected_revision:
            raise ValueError('obsolete artifact revision')
        if self.sha256 != digest(self.content): raise ValueError('artifact hash mismatch')
        if self.provenance not in ('offline-human-reference', 'actual-provider-response'):
            raise ValueError('provenance required')
        return self.content


def task_order(graph):
    """Topological ordering, with explicit unknown dependency/cycle rejection."""
    if not graph: raise ValueError('empty task graph')
    pending = {key: set(deps) for key, deps in graph.items()}
    if any(not deps <= set(graph) for deps in pending.values()): raise ValueError('missing prerequisite')
    result = []
    while pending:
        ready = sorted(key for key, deps in pending.items() if deps <= set(result))
        if not ready: raise ValueError('cycle')
        result.extend(ready)
        for key in ready: del pending[key]
    return result


def dispatchable(task, graph, state, artifacts):
    task_order(graph)
    if task not in graph: raise ValueError('unknown task')
    for dependency in graph[task]:
        if state.get(dependency) != 'passed' or dependency not in artifacts:
            return False
        envelope, expected_revision = artifacts[dependency]
        envelope.validate(dependency, expected_revision)
    return True


def bounded_repair(initial_source, patches, apply_patch, execute_tests, maximum=2):
    """Keep every observed failure; test callbacks must identify actual execution.

    apply_patch returns a new source mapping. Only existing src/*.py may change;
    immutable acceptance tests/dependencies/docs remain exact. This orchestrator
    never executes generated Python itself; pass the Docker runner for real code.
    """
    if type(maximum) is not int or not 0 <= maximum <= 3: raise ValueError('repair budget')
    source = dict(initial_source)
    seen = {digest(source)}
    trace = []
    candidates = iter(patches)
    for attempt in range(maximum + 1):
        receipt = execute_tests(dict(source))
        if not isinstance(receipt, dict) or receipt.get('execution') not in ('docker', 'offline-functional-fixture'):
            raise ValueError('actual execution provenance required')
        if type(receipt.get('passed')) is not bool or not isinstance(receipt.get('evidence'), dict):
            raise ValueError('structured test evidence required')
        trace.append(dict(attempt=attempt, source_sha256=digest(source), receipt=receipt))
        if receipt['passed']: return dict(passed=True, source=source, trace=trace, reason='tests passed')
        if attempt == maximum: break
        try: patch = next(candidates)
        except StopIteration: break
        revised = apply_patch(dict(source), patch)
        if set(revised) != set(source): raise ValueError('artifact inventory modification')
        for name in source:
            if revised[name] != source[name]: safe_source(name)
        identity = digest(revised)
        if identity in seen: return dict(passed=False, source=source, trace=trace, reason='repeated unchanged repair')
        seen.add(identity); source = revised
    return dict(passed=False, source=source, trace=trace, reason='repair budget or patches exhausted')


def expense_fixture(operator):
    """Safe executed arithmetic fixture, NOT generated-code or provider evidence."""
    if operator not in ('sum', 'first'): raise ValueError('unknown fixture implementation')
    cases = [([], 0), ([0], 0), ([125, 275], 400)]
    results = []
    for values, expected in cases:
        observed = sum(values) if operator == 'sum' else (values[0] if values else 0)
        results.append(dict(inputs=values, expected=expected, observed=observed, passed=observed == expected))
    return dict(execution='offline-functional-fixture', passed=all(x['passed'] for x in results),
                evidence=dict(cases=results, implementation=operator))
