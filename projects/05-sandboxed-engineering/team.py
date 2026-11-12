"""Four-role offline engineering workflow with bounded, allowlisted execution."""
from __future__ import annotations
import argparse
from dataclasses import dataclass, asdict
import hashlib
import json
import re
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile
import uuid

APP = '''"""A small expense calculator. Amounts are integer minor currency units."""
def total_expenses(amounts):
    if any(type(value) is not int or value < 0 for value in amounts):
        raise ValueError("amounts must be non-negative integer minor units")
    return sum(amounts)
'''
TESTS = '''import unittest
from expense_app import total_expenses
class ExpenseTests(unittest.TestCase):
    def test_empty(self): self.assertEqual(total_expenses([]), 0)
    def test_sum(self): self.assertEqual(total_expenses([125, 275]), 400)
    def test_zero(self): self.assertEqual(total_expenses([0]), 0)
    def test_negative(self):
        with self.assertRaises(ValueError): total_expenses([-1])
    def test_non_integer(self):
        with self.assertRaises(ValueError): total_expenses([1.5])
    def test_boolean(self):
        with self.assertRaises(ValueError): total_expenses([True])
if __name__ == "__main__": unittest.main()
'''
DOC = '''# Expense calculator\n\nAmounts use integer minor currency units; 125 means 1.25 in a two-decimal\ncurrency. No currency conversion, persistence or financial recommendation.\n\nRun `python -m unittest -v` in this directory.\n'''
FILES = {'expense_app.py': APP, 'test_expense_app.py': TESTS,
         'README.md': DOC, 'requirements.txt': '# Standard library only. No third-party dependencies.\n'}

@dataclass(frozen=True)
class Specification:
    title: str = 'Expense calculator'
    feature: str = 'sum_non_negative_minor_units'
    currency_decimals: int = 2
    def __post_init__(self):
        if self.feature != 'sum_non_negative_minor_units' or self.currency_decimals != 2:
            raise ValueError('unsupported scope: this teaching builder supports one reviewed feature')
        if not self.title.strip() or len(self.title) > 120:
            raise ValueError('title must contain 1..120 characters')

def safe_path(root: Path, relative: str) -> Path:
    root = root.resolve(strict=True)
    requested = Path(relative)
    if requested.is_absolute() or '..' in requested.parts or not requested.parts:
        raise ValueError('path must remain inside workspace')
    candidate = root / requested
    # No symlink, even one pointing inside: avoid ambiguous write ownership.
    for parent in (candidate, *candidate.parents):
        if parent == root: break
        if parent.is_symlink(): raise ValueError('symlink is forbidden')
    resolved = candidate.resolve()
    if not resolved.is_relative_to(root): raise ValueError('workspace escape')
    return candidate

def plan(spec: Specification) -> dict:
    return dict(specification=asdict(spec), requirements=[
        'Sum non-negative integer minor units exactly',
        'Reject negative, floating-point and boolean inputs',
        'Empty input returns zero'], architecture=dict(module='expense_app.py',
        function='total_expenses(amounts)', dependencies=[]),
        tasks=[dict(role='product_manager', produces='requirements'),
               dict(role='architect', depends_on=['requirements'], produces='architecture'),
               dict(role='developer', depends_on=['architecture'], produces='source'),
               dict(role='quality_assurance', depends_on=['source'], produces='test_report')])

def build(root: Path, spec: Specification) -> dict:
    trace = plan(spec)
    for name, content in FILES.items():
        path = safe_path(root, name)
        # Exclusive creation prevents silently replacing an existing workspace.
        with path.open('x') as handle: handle.write(content)
    trace['artifacts'] = {name: hashlib.sha256(content.encode()).hexdigest() for name, content in FILES.items()}
    safe_path(root, 'delivery-plan.json').write_text(json.dumps(trace, indent=2) + '\n')
    return trace

def verify_template(root: Path):
    actual = {p.name for p in root.iterdir()}
    if actual != set(FILES) | {'delivery-plan.json'}:
        raise ValueError('unexpected workspace content; refusing execution')
    if not safe_path(root, 'delivery-plan.json').is_file():
        raise ValueError('delivery plan must be an ordinary workspace file')
    for name, content in FILES.items():
        path = safe_path(root, name)
        if not path.is_file() or path.read_bytes() != content.encode():
            raise ValueError(f'unreviewed source or tests: {name}; use isolated Docker for new agent code')

def test(root: Path, timeout: float = 10, docker_image: str | None = None) -> dict:
    if not 0 < timeout <= 60: raise ValueError('timeout must be positive and at most 60 seconds')
    verify_template(root)
    # Only the byte-identical, course-owned template runs on the host. This is NOT
    # a general Python sandbox. Agent-generated alterations are rejected above.
    command = [sys.executable, '-B', '-I', '-c',
               'import sys,unittest;sys.path.insert(0,".");'
               'r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.discover("."));'
               'sys.exit(not r.wasSuccessful())']
    container_name = None
    if docker_image:
        # Image must already be locally present; no pull or network access.
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._/:~-]*@sha256:[0-9a-f]{64}', docker_image):
            raise ValueError('use a preloaded digest-pinned Docker image')
        container_name = 'eca-engineering-' + uuid.uuid4().hex
        command = ['docker', 'run', '--name', container_name, '--rm', '--pull=never', '--network=none', '--read-only',
                   '--cap-drop=ALL', '--security-opt=no-new-privileges', '--pids-limit=64',
                   '--memory=256m', '--cpus=1', '--user=65534:65534',
                   '--mount', f'type=bind,source={root.resolve()},target=/workspace,readonly',
                   '--tmpfs', '/tmp:rw,noexec,nosuid,size=16m', '--workdir=/workspace',
                   docker_image, 'python', '-B', '-m', 'unittest', '-v']
    try:
        result = subprocess.run(command, cwd=root, capture_output=True, text=True,
                                timeout=timeout, env={'PATH': os.defpath, 'PYTHONDONTWRITEBYTECODE': '1'})
        return dict(passed=result.returncode == 0, returncode=result.returncode,
                    stdout=result.stdout, stderr=result.stderr, timed_out=False,
                    execution='docker' if docker_image else 'reviewed-template-only')
    except subprocess.TimeoutExpired:
        return dict(passed=False, returncode=None, timed_out=True,
                    execution='docker-timeout' if docker_image else 'reviewed-template-only')
    finally:
        if container_name:
            # Only this invocation's owned random-name container may be removed.
            cleanup = subprocess.run(['docker', 'rm', '-f', container_name], capture_output=True, timeout=10)
            if cleanup.returncode:
                inspected = subprocess.run(['docker', 'container', 'inspect', container_name], capture_output=True, timeout=10)
                if inspected.returncode != 1 or b'No such container' not in inspected.stderr:
                    raise RuntimeError('container cleanup unproven; operator intervention required')

def package(root: Path, destination: Path):
    verify_template(root)
    if destination.resolve().is_relative_to(root.resolve()):
        raise ValueError('package destination must be outside workspace')
    with zipfile.ZipFile(destination, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(root.iterdir()): archive.write(path, path.name)

def run(spec: Specification, output: Path | None = None) -> dict:
    with tempfile.TemporaryDirectory(prefix='eca-engineering-') as temp:
        root = Path(temp)
        trace = build(root, spec)
        qa = test(root)
        if not qa['passed']: raise RuntimeError('delivery blocked: tests failed')
        if output: package(root, output)
        return dict(plan=trace, qa=qa, package=str(output) if output else None,
                    workflow='offline role orchestration; no model or provider calls')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--title', default='Expense calculator')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    print(json.dumps(run(Specification(title=args.title), args.output), indent=2))
if __name__ == '__main__': main()
