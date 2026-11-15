"""Offline learner activities: file boundaries, arithmetic repair and handoffs."""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import tempfile

from sandbox import FileTools
import semantic_team
import workflow


def file_activity():
    with tempfile.TemporaryDirectory(prefix='eca-student-files-') as directory:
        workspace = Path(directory)
        (workspace / 'src').mkdir()
        (workspace / 'tests').mkdir()
        with FileTools(workspace) as tools:
            original = tools.write('src/app.py', 'amount = 125\n')
            rejected = {}
            proposals = {
                'traversal': '../escape.py',
                'absolute': str(workspace / 'absolute.py'),
                'readonly_tests': 'tests/test_app.py',
            }
            for label, path in proposals.items():
                try:
                    tools.write(path, 'not executed\n')
                except (ValueError, PermissionError) as error:
                    rejected[label] = type(error).__name__
            try:
                tools.write('src/app.py', 'amount = 400\n', '0' * 64)
            except ValueError as error:
                rejected['stale_write'] = type(error).__name__
            (workspace / 'src/link.py').symlink_to(workspace / 'src/app.py')
            try:
                tools.read('src/link.py')
            except (ValueError, OSError) as error:
                rejected['symlink_read'] = type(error).__name__
            updated = tools.write('src/app.py', 'amount = 400\n', original)
            result = {
                'provenance': 'offline-student-file-activity',
                'content': tools.read('src/app.py'),
                'files': tools.list('src'),
                'original_sha256': original,
                'updated_sha256': updated,
                'rejected': rejected,
                'application_executed': False,
            }
    result['temporary_workspace_removed'] = not workspace.exists()
    return result


def repair_activity():
    initial = {'src/operator.py': 'first', 'tests/fixed.txt': 'unchanged'}
    result = workflow.bounded_repair(
        initial,
        ['sum'],
        lambda source, replacement: {**source, 'src/operator.py': replacement},
        lambda source: workflow.expense_fixture(source['src/operator.py']),
    )
    return {
        'provenance': 'offline-functional-fixture',
        'application_executed': False,
        'provider_called': False,
        'initial_source': initial,
        'result': result,
        'limits': 'Arithmetic cases only; no R3 invalid-input, generated-code or container verification.',
    }


def handoff_activity():
    reference = json.loads(Path(__file__).with_name('reference-contracts.json').read_text())
    requirements = {
        'revision': 1,
        'stories': [{'id': 'S1', 'text': reference['requirements']['stories'][0]}],
        'criteria': {
            criterion: {'story_id': 'S1', 'description': description, 'priority': priority}
            for priority, (criterion, description) in enumerate(
                reference['requirements']['criteria'].items(), 1)
        },
        'priorities': ['R1', 'R2', 'R3'],
    }
    semantic_team.validate_requirements(requirements)
    local_response = {'provenance': 'offline-human-reference', 'content': requirements}
    artifact = semantic_team.envelope('product_manager', 1, requirements, semantic_team.sha(local_response))
    semantic_team.consume(artifact, 'product_manager', 1)
    failures = {}
    changed = deepcopy(artifact)
    changed['content']['stories'][0]['text'] = 'Changed after hashing'
    for label, candidate, revision in (
        ('changed_content', changed, 1), ('obsolete_revision', artifact, 2)
    ):
        try:
            semantic_team.consume(candidate, 'product_manager', revision)
        except ValueError as error:
            failures[label] = str(error)
    return {
        'provenance': 'offline-human-reference',
        'artifact': artifact,
        'rejected': failures,
        'provider_called': False,
        'limits': 'The response hash identifies local reference data, not a provider response or approval.',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('activity', choices=('files', 'repair', 'handoffs'))
    args = parser.parse_args()
    activities = {'files': file_activity, 'repair': repair_activity, 'handoffs': handoff_activity}
    print(json.dumps(activities[args.activity](), indent=2))


if __name__ == '__main__':
    main()
